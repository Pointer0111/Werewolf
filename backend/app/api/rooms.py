"""
房间相关API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import random
import string

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.game import Game, GamePlayer, GameStatus

router = APIRouter()


class RoomCreate(BaseModel):
    room_name: str
    max_players: int = 12
    roles_config: dict = None


class RoomResponse(BaseModel):
    id: int
    room_code: str
    room_name: str
    owner_id: int
    max_players: int
    status: str
    current_round: int
    
    class Config:
        from_attributes = True


class RoomJoin(BaseModel):
    room_code: str


def generate_room_code(length: int = 6) -> str:
    """生成房间号"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建房间"""
    # 生成唯一房间号
    room_code = generate_room_code()
    while db.query(Game).filter(Game.room_code == room_code).first():
        room_code = generate_room_code()
    
    # 创建房间
    game = Game(
        room_code=room_code,
        room_name=room_data.room_name,
        owner_id=current_user.id,
        max_players=room_data.max_players,
        roles_config=room_data.roles_config or {},
        status=GameStatus.WAITING
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    
    # 房主自动加入
    player = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
        seat_number=1
    )
    db.add(player)
    db.commit()
    
    return game


@router.post("/join", response_model=RoomResponse)
async def join_room(
    join_data: RoomJoin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """加入房间"""
    game = db.query(Game).filter(Game.room_code == join_data.room_code).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if game.status != GameStatus.WAITING:
        raise HTTPException(status_code=400, detail="游戏已开始或已结束")
    
    # 检查是否已在房间中
    existing_player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game.id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if existing_player:
        return game
    
    # 检查房间人数
    current_players = db.query(GamePlayer).filter(GamePlayer.game_id == game.id).count()
    if current_players >= game.max_players:
        raise HTTPException(status_code=400, detail="房间已满")
    
    # 加入房间
    player = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
        seat_number=current_players + 1
    )
    db.add(player)
    db.commit()
    
    return game


@router.get("/{room_code}", response_model=RoomResponse)
async def get_room(room_code: str, db: Session = Depends(get_db)):
    """获取房间信息"""
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="房间不存在")
    return game


@router.get("/", response_model=List[RoomResponse])
async def list_rooms(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取房间列表"""
    query = db.query(Game)
    if status:
        query = query.filter(Game.status == GameStatus[status.upper()])
    games = query.order_by(Game.created_at.desc()).limit(50).all()
    return games

