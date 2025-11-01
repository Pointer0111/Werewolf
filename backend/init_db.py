"""
初始化数据库脚本
"""
from app.core.database import Base, engine
from app.models.user import User
from app.models.game import Game, GamePlayer, GameRecord

def init_db():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")

if __name__ == "__main__":
    init_db()

