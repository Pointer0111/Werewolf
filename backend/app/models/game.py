"""
游戏相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class GameStatus(enum.Enum):
    """游戏状态"""
    WAITING = "waiting"  # 等待中
    PLAYING = "playing"  # 进行中
    FINISHED = "finished"  # 已结束


class Game(Base):
    """游戏房间"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    room_code = Column(String(10), unique=True, index=True, nullable=False)
    room_name = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 游戏配置
    max_players = Column(Integer, default=12)
    roles_config = Column(JSON)  # 角色配置
    
    # 游戏状态
    status = Column(SQLEnum(GameStatus), default=GameStatus.WAITING)
    current_round = Column(Integer, default=0)
    current_phase = Column(String(20))  # night/day
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))


class GamePlayer(Base):
    """游戏玩家"""
    __tablename__ = "game_players"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 游戏信息
    role = Column(String(20))  # 角色名称
    seat_number = Column(Integer)  # 座位号
    is_alive = Column(Boolean, default=True)
    
    # 时间戳
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


class GameRecord(Base):
    """游戏记录"""
    __tablename__ = "game_records"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    # 游戏结果
    winner = Column(String(20))  # villagers/werewolves
    duration = Column(Integer)  # 游戏时长（秒）
    rounds = Column(Integer)  # 总轮数
    
    # 游戏详情（JSON格式存储）
    game_log = Column(JSON)
    
    # 时间戳
    finished_at = Column(DateTime(timezone=True), server_default=func.now())

