"""
处理玩家发言的服务函数
"""
from sqlalchemy.orm import Session
from app.models.game import Game, GamePlayer, GameStatus
from app.api.ai_assistant import get_or_create_game_engine


def handle_player_speech(room_code: str, user_id: int, speech_content: str, db: Session):
    """处理玩家发言并记录到游戏日志"""
    # 获取游戏引擎
    engine = get_or_create_game_engine(room_code, db)
    if not engine:
        return False
    
    # 获取玩家信息
    game = db.query(Game).filter(Game.room_code == room_code).first()
    if not game:
        return False
    
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game.id,
        GamePlayer.user_id == user_id
    ).first()
    
    if not player:
        return False
    
    # 获取玩家名称
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    player_name = user.nickname if user and user.nickname else (user.username if user else f"玩家{user_id}")
    
    # 记录发言
    success = engine.record_speech(user_id, player_name, speech_content)
    return success

