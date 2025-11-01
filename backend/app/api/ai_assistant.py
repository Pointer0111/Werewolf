"""
AI助手相关API：获取游戏日志和玩家信息
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.game import Game, GamePlayer, GameStatus
from app.services.game_engine import GameEngine, Role

router = APIRouter()


class GameLogResponse(BaseModel):
    """游戏日志响应"""
    logs: List[Dict]
    total_count: int


class PlayerInfoResponse(BaseModel):
    """玩家信息响应"""
    player_id: int
    player_name: str
    role: Optional[str]
    is_alive: bool
    seat_number: Optional[int]


class GameContextResponse(BaseModel):
    """游戏上下文响应（供AI助手使用）"""
    game_id: int
    room_code: str
    current_round: int
    current_phase: str
    player_info: PlayerInfoResponse
    game_logs: List[Dict]
    alive_players: List[int]
    dead_players: List[int]


# 游戏引擎实例存储（实际项目中应该使用Redis或数据库存储）
_game_engines: Dict[str, GameEngine] = {}


def get_or_create_game_engine(room_code: str, db: Session) -> Optional[GameEngine]:
    """获取或创建游戏引擎实例"""
    # 从数据库加载游戏信息
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        return None
    
    # 如果已有引擎实例，直接返回
    if room_code in _game_engines:
        return _game_engines[room_code]
    
    # 创建新的游戏引擎实例
    players = db.query(GamePlayer).filter(GamePlayer.game_id == game.id).all()
    player_ids = [p.user_id for p in players]
    
    if not player_ids:
        return None
    
    engine = GameEngine(game.id, len(player_ids))
    
    # 分配角色（如果游戏已开始）
    if game.status == GameStatus.PLAYING:
        roles = engine.assign_roles(player_ids)
        # 设置玩家存活状态
        for player in players:
            engine.roles[player.user_id] = Role(player.role) if player.role else Role.VILLAGER
            if not player.is_alive:
                engine.alive_players.discard(player.user_id)
                engine.dead_players.add(player.user_id)
    
    _game_engines[room_code] = engine
    return engine


@router.get("/game/{room_code}/logs", response_model=GameLogResponse)
async def get_game_logs(
    room_code: str,
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取游戏日志（包含玩家发言）"""
    # 验证用户是否在游戏中
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game.id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=403, detail="您不在此游戏中")
    
    # 获取游戏引擎
    engine = get_or_create_game_engine(room_code, db)
    if not engine:
        raise HTTPException(status_code=400, detail="游戏尚未开始")
    
    logs = engine.get_all_logs() if limit is None else engine.get_recent_logs(limit)
    
    return {
        "logs": logs,
        "total_count": len(engine.get_all_logs())
    }


@router.get("/game/{room_code}/player-info", response_model=PlayerInfoResponse)
async def get_player_info(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前玩家的角色信息"""
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game.id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=403, detail="您不在此游戏中")
    
    # 获取游戏引擎
    engine = get_or_create_game_engine(room_code, db)
    if not engine:
        raise HTTPException(status_code=400, detail="游戏尚未开始")
    
    # 获取玩家角色
    role = engine.get_player_role(current_user.id)
    role_name = role.value if role else None
    
    return {
        "player_id": current_user.id,
        "player_name": current_user.nickname or current_user.username,
        "role": role_name,
        "is_alive": player.is_alive,
        "seat_number": player.seat_number
    }


@router.get("/game/{room_code}/context", response_model=GameContextResponse)
async def get_game_context(
    room_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取完整游戏上下文（供AI助手使用）"""
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game.id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=403, detail="您不在此游戏中")
    
    # 获取游戏引擎
    engine = get_or_create_game_engine(room_code, db)
    if not engine:
        raise HTTPException(status_code=400, detail="游戏尚未开始")
    
    # 获取玩家角色
    role = engine.get_player_role(current_user.id)
    role_name = role.value if role else None
    
    # 获取游戏状态
    game_state = engine.get_game_state()
    
    return {
        "game_id": game.id,
        "room_code": room_code,
        "current_round": game_state.get("round", game.current_round),
        "current_phase": game_state.get("phase", game.current_phase or "waiting"),
        "player_info": {
            "player_id": current_user.id,
            "player_name": current_user.nickname or current_user.username,
            "role": role_name,
            "is_alive": player.is_alive,
            "seat_number": player.seat_number
        },
        "game_logs": engine.get_all_logs(),
        "alive_players": list(engine.alive_players),
        "dead_players": list(engine.dead_players)
    }

