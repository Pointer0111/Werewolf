"""
安全相关：密码加密、JWT Token生成
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import hashlib
    # 如果密码超过72字节，使用相同的哈希处理
    original_password = plain_password
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        # 如果失败，尝试使用原始密码（向后兼容）
        if not result and original_password != plain_password:
            result = pwd_context.verify(original_password, hashed_password)
        return result
    except:
        return False


def get_password_hash(password: str) -> str:
    """加密密码"""
    # bcrypt 限制密码长度最多72字节，超过部分会被截断
    # 为了安全，我们在加密前先进行哈希处理
    import hashlib
    if len(password.encode('utf-8')) > 72:
        # 如果密码超过72字节，先进行SHA256哈希
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

