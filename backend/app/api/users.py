"""
用户相关API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: str = None
    avatar: str = None
    total_games: int
    win_games: int
    win_rate: float
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: str = None
    avatar: str = None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

