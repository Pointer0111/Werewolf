"""
Redis客户端连接
"""
import redis
from app.core.config import settings
import json


class RedisClient:
    """Redis客户端单例"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        return cls._instance
    
    def get(self, key: str):
        """获取值"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def set(self, key: str, value, ex: int = None):
        """设置值"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str):
        """删除键"""
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.client.exists(key) > 0


redis_client = RedisClient()

