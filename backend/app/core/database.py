"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# 如果 DATABASE_URL 使用默认值或连接失败，使用 SQLite 作为后备
database_url = settings.DATABASE_URL

# 检查是否是默认配置或连接字符串无效
if database_url == "postgresql://user:password@localhost/werewolf" or not database_url:
    # 使用 SQLite 作为开发数据库
    database_url = "sqlite:///./werewolf.db"
    print("[WARNING] 使用 SQLite 数据库（开发模式）")
    print("          如需使用 PostgreSQL，请在 .env 文件中配置 DATABASE_URL")

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

