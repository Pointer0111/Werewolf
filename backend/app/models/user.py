"""
用户数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    
    # 游戏统计数据
    total_games = Column(Integer, default=0)
    win_games = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

