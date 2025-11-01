"""
狼人杀游戏系统 - FastAPI 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, rooms, users, ai_assistant
from app.websocket import router as websocket_router
from app.core.config import settings

app = FastAPI(
    title="狼人杀游戏系统",
    description="基于FastAPI的在线狼人杀游戏平台",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["房间"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["AI助手"])
app.include_router(websocket_router.router, tags=["WebSocket"])


@app.get("/")
async def root():
    return {"message": "狼人杀游戏系统API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

