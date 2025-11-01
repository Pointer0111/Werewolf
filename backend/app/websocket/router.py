"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.api.auth import get_current_user
from app.websocket.manager import manager
from app.models.game import Game, GameStatus
from app.models.user import User

router = APIRouter()


async def get_current_user_from_token(websocket: WebSocket):
    """从WebSocket查询参数或Header获取用户"""
    # 从query参数获取token
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=1008, reason="未提供认证token")
        return None
    
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    
    if not payload:
        await websocket.close(code=1008, reason="无效的token")
        return None
    
    return payload.get("user_id")


@router.websocket("/ws/room/{room_code}")
async def websocket_room(websocket: WebSocket, room_code: str):
    """房间WebSocket连接"""
    # 获取用户信息
    user_id = await get_current_user_from_token(websocket)
    if not user_id:
        return
    
    # 验证房间是否存在
    db = next(get_db())
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        await websocket.close(code=1008, reason="房间不存在")
        return
    
    # 连接
    await manager.connect(websocket, room_code, user_id)
    
    try:
        # 发送当前游戏状态
        await manager.send_personal_message({
            "type": "connected",
            "room_code": room_code,
            "user_id": user_id,
            "message": "连接成功"
        }, websocket)
        
        # 保持连接，接收消息
        while True:
            data = await websocket.receive_json()
            await handle_room_message(room_code, user_id, data, websocket, db)
    
    except WebSocketDisconnect:
        user_id = manager.disconnect(websocket, room_code)
        if user_id:
            await manager.broadcast(room_code, {
                "type": "player_left",
                "user_id": user_id,
                "message": f"玩家 {user_id} 离开了房间"
            })


async def broadcast_game_log(room_code: str, log_message: str, phase: str = None, round_num: int = None):
    """广播游戏日志到房间所有玩家"""
    await manager.broadcast(room_code, {
        "type": "game_log",
        "message": log_message,
        "phase": phase,
        "round": round_num,
        "timestamp": None
    })


async def handle_room_message(room_code: str, user_id: int, data: dict, websocket: WebSocket, db: Session):
    """处理房间消息"""
    message_type = data.get("type")
    
    if message_type == "chat":
        # 聊天消息（房间聊天，不在游戏日志中）
        await manager.broadcast(room_code, {
            "type": "chat",
            "user_id": user_id,
            "message": data.get("message", ""),
            "timestamp": data.get("timestamp")
        }, exclude={websocket})
    
    elif message_type == "speech":
        # 游戏中的发言（记录到游戏日志）
        from app.models.user import User
        from app.models.game import GamePlayer
        from app.api.speech_handler import handle_player_speech
        
        speech_content = data.get("content", "")
        
        # 验证游戏状态
        game = db.query(Game).filter(Game.room_code == room_code).first()
        if not game or game.status != GameStatus.PLAYING:
            await manager.send_personal_message({
                "type": "error",
                "message": "游戏未开始，无法发言"
            }, websocket)
            return
        
        # 验证玩家状态
        player = db.query(GamePlayer).filter(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == user_id
        ).first()
        
        if not player or not player.is_alive:
            await manager.send_personal_message({
                "type": "error",
                "message": "您已出局，无法发言"
            }, websocket)
            return
        
        # 获取玩家名称
        user = db.query(User).filter(User.id == user_id).first()
        player_name = user.nickname if user and user.nickname else (user.username if user else f"玩家{user_id}")
        
        # 记录发言到游戏引擎
        success = handle_player_speech(room_code, user_id, speech_content, db)
        
        if success:
            # 广播发言消息到所有玩家
            await manager.broadcast(room_code, {
                "type": "game_log",
                "message": f"💬 {player_name}: {speech_content}",
                "phase": "day",
                "round": game.current_round or 1,
                "player_id": user_id,
                "player_name": player_name
            })
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "发言记录失败"
            }, websocket)
    
    elif message_type == "game_action":
        # 游戏行动（夜晚行动、投票等）
        await manager.broadcast(room_code, {
            "type": "game_action",
            "user_id": user_id,
            "action": data.get("action"),
            "data": data.get("data")
        }, exclude={websocket})
    
    elif message_type == "get_status":
        # 获取游戏状态
        game = db.query(Game).filter(Game.room_code == room_code).first()
        if game:
            await manager.send_personal_message({
                "type": "game_status",
                "status": game.status.value,
                "current_round": game.current_round,
                "current_phase": game.current_phase or "waiting"
            }, websocket)

