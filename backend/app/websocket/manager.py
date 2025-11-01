"""
WebSocket连接管理器
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # {room_code: {websocket: user_id}}
        self.active_connections: Dict[str, Dict[WebSocket, int]] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str, user_id: int):
        """连接WebSocket"""
        await websocket.accept()
        
        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}
        
        self.active_connections[room_code][websocket] = user_id
        
        # 通知房间内其他玩家
        await self.broadcast(
            room_code,
            {
                "type": "player_joined",
                "user_id": user_id,
                "message": f"玩家 {user_id} 加入了房间"
            },
            exclude={websocket}
        )
    
    def disconnect(self, websocket: WebSocket, room_code: str):
        """断开WebSocket连接"""
        if room_code in self.active_connections:
            user_id = self.active_connections[room_code].pop(websocket, None)
            
            # 如果房间为空，删除房间
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
            
            return user_id
        return None
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)
    
    async def broadcast(self, room_code: str, message: dict, exclude: Set[WebSocket] = None):
        """广播消息到房间内所有连接"""
        if room_code not in self.active_connections:
            return
        
        exclude = exclude or set()
        disconnected = []
        
        for websocket, user_id in self.active_connections[room_code].items():
            if websocket not in exclude:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)
        
        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws, room_code)
    
    def get_room_users(self, room_code: str) -> List[int]:
        """获取房间内的用户ID列表"""
        if room_code not in self.active_connections:
            return []
        return list(self.active_connections[room_code].values())
    
    def get_user_websocket(self, room_code: str, user_id: int) -> WebSocket:
        """获取指定用户的WebSocket连接"""
        if room_code not in self.active_connections:
            return None
        
        for websocket, uid in self.active_connections[room_code].items():
            if uid == user_id:
                return websocket
        return None


manager = ConnectionManager()

