# -*- coding: utf-8 -*-
"""初始化数据库"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, engine
from app.models.user import User
from app.models.game import Game, GamePlayer, GameRecord

def init_db():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

