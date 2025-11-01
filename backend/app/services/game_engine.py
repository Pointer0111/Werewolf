"""
游戏逻辑引擎：角色分配、状态机、回合控制、胜负判定
"""
import random
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class Role(Enum):
    """角色枚举"""
    VILLAGER = "villager"  # 村民
    WEREWOLF = "werewolf"  # 狼人
    SEER = "seer"  # 预言家
    WITCH = "witch"  # 女巫
    HUNTER = "hunter"  # 猎人
    GUARD = "guard"  # 守卫


class GamePhase(Enum):
    """游戏阶段"""
    NIGHT = "night"  # 夜晚
    DAY = "day"  # 白天
    VOTING = "voting"  # 投票
    RESULT = "result"  # 结果


class GameEngine:
    """游戏引擎"""
    
    def __init__(self, game_id: int, player_count: int):
        self.game_id = game_id
        self.player_count = player_count
        self.roles: Dict[int, Role] = {}  # {player_id: role}
        self.alive_players: set = set()
        self.dead_players: set = set()
        self.current_round = 0
        self.current_phase = GamePhase.NIGHT
        self.night_actions = {}  # 夜晚行动记录
        self.votes = {}  # 投票记录
        self.game_log = []  # 游戏日志（包含系统日志和玩家发言）
        self.speeches = []  # 玩家发言记录
    
    def assign_roles(self, player_ids: List[int]) -> Dict[int, Role]:
        """分配角色"""
        roles = self._generate_role_config(player_ids)
        self.roles = roles
        self.alive_players = set(player_ids)
        
        self.game_log.append({
            "type": "game_log",
            "round": 0,
            "message": "游戏开始，角色已分配",
            "timestamp": None
        })
        
        return roles
    
    def _generate_role_config(self, player_ids: List[int]) -> Dict[int, Role]:
        """根据玩家人数生成角色配置"""
        count = len(player_ids)
        roles = {}
        shuffled_ids = player_ids.copy()
        random.shuffle(shuffled_ids)
        
        # 基础配置：根据人数分配角色
        if count >= 6:
            # 至少1个狼人，1个预言家，其余村民
            roles[shuffled_ids[0]] = Role.WEREWOLF
            roles[shuffled_ids[1]] = Role.SEER
            
            if count >= 8:
                roles[shuffled_ids[2]] = Role.WITCH
            if count >= 10:
                roles[shuffled_ids[3]] = Role.HUNTER
            if count >= 12:
                roles[shuffled_ids[4]] = Role.GUARD
            
            # 其余为村民
            assigned_count = len(roles)
            for i in range(assigned_count, count):
                roles[shuffled_ids[i]] = Role.VILLAGER
            
            # 确保至少2个狼人（8人以上）
            if count >= 8:
                villager_indices = [i for i, role in roles.items() if role == Role.VILLAGER]
                if villager_indices:
                    roles[random.choice(villager_indices)] = Role.WEREWOLF
        
        return roles
    
    def start_night(self):
        """开始夜晚阶段"""
        self.current_round += 1
        self.current_phase = GamePhase.NIGHT
        self.night_actions = {}
        
        from datetime import datetime
        self.game_log.append({
            "type": "game_log",
            "round": self.current_round,
            "phase": "night",
            "message": f"🌙 第 {self.current_round} 夜开始，请各位玩家进行行动",
            "timestamp": datetime.now().isoformat()
        })
    
    def record_night_action(self, player_id: int, action_type: str, target_id: Optional[int] = None, data: dict = None):
        """记录夜晚行动"""
        if player_id not in self.alive_players:
            return False
        
        self.night_actions[player_id] = {
            "type": action_type,
            "target_id": target_id,
            "data": data or {}
        }
        return True
    
    def process_night_actions(self):
        """处理夜晚行动（按顺序：守卫->狼人->预言家->女巫）"""
        killed_targets = []
        protected_target = None
        
        # 1. 守卫行动
        guard_id = next((pid for pid, role in self.roles.items() if role == Role.GUARD and pid in self.alive_players), None)
        if guard_id and guard_id in self.night_actions:
            action = self.night_actions[guard_id]
            if action["type"] == "guard" and action["target_id"]:
                protected_target = action["target_id"]
        
        # 2. 狼人行动
        werewolves = [pid for pid, role in self.roles.items() if role == Role.WEREWOLF and pid in self.alive_players]
        werewolf_target = None
        if werewolves:
            werewolf_actions = [self.night_actions.get(wid) for wid in werewolves if wid in self.night_actions]
            if werewolf_actions and werewolf_actions[0]:
                werewolf_target = werewolf_actions[0].get("target_id")
        
        # 3. 预言家查验
        seer_id = next((pid for pid, role in self.roles.items() if role == Role.SEER and pid in self.alive_players), None)
        seer_result = None
        if seer_id and seer_id in self.night_actions:
            action = self.night_actions[seer_id]
            if action["type"] == "check" and action["target_id"]:
                target_role = self.roles.get(action["target_id"])
                seer_result = {
                    "target_id": action["target_id"],
                    "is_werewolf": target_role == Role.WEREWOLF
                }
        
        # 4. 女巫行动
        witch_id = next((pid for pid, role in self.roles.items() if role == Role.WITCH and pid in self.alive_players), None)
        saved_target = None
        poisoned_target = None
        
        if witch_id and witch_id in self.night_actions:
            action = self.night_actions[witch_id]
            if action["type"] == "save" and action.get("data", {}).get("use_antidote"):
                saved_target = werewolf_target
            if action["type"] == "poison" and action.get("target_id"):
                poisoned_target = action["target_id"]
        
        # 结算夜晚结果
        if werewolf_target:
            if werewolf_target != protected_target:  # 守卫保护
                if saved_target != werewolf_target:  # 女巫救人
                    killed_targets.append(werewolf_target)
        
        if poisoned_target and poisoned_target in self.alive_players:
            killed_targets.append(poisoned_target)
        
        # 更新存活状态
        for target_id in killed_targets:
            if target_id in self.alive_players:
                self.alive_players.remove(target_id)
                self.dead_players.add(target_id)
        
        night_result = {
            "killed": killed_targets,
            "protected": protected_target,
            "seer_result": seer_result,
            "saved": saved_target is not None
        }
        
        from datetime import datetime
        
        # 生成夜晚结果的日志消息
        log_messages = []
        if killed_targets:
            log_messages.append(f"💀 夜晚结束，{len(killed_targets)} 名玩家死亡")
        else:
            log_messages.append("✅ 夜晚结束，无人死亡")
        
        if protected_target:
            log_messages.append(f"🛡️ 守卫保护了一名玩家")
        
        if saved_target:
            log_messages.append(f"💊 女巫使用解药救活了一名玩家")
        
        for msg in log_messages:
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "night",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            })
        
        return night_result
    
    def start_day(self):
        """开始白天阶段"""
        self.current_phase = GamePhase.DAY
        self.votes = {}
        
        from datetime import datetime
        self.game_log.append({
            "type": "game_log",
            "round": self.current_round,
            "phase": "day",
            "message": f"☀️ 第 {self.current_round} 天开始，请各位玩家发言讨论",
            "timestamp": datetime.now().isoformat()
        })
    
    def record_speech(self, player_id: int, player_name: str, speech_content: str) -> bool:
        """记录玩家发言"""
        if player_id not in self.alive_players:
            return False
        
        from datetime import datetime
        speech_record = {
            "type": "speech",
            "player_id": player_id,
            "player_name": player_name,
            "content": speech_content,
            "round": self.current_round,
            "phase": "day",
            "timestamp": datetime.now().isoformat()
        }
        
        self.speeches.append(speech_record)
        
        # 同时记录到游戏日志
        self.game_log.append({
            "type": "game_log",
            "round": self.current_round,
            "phase": "day",
            "message": f"💬 {player_name}: {speech_content}",
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "player_name": player_name
        })
        
        return True
    
    def record_vote(self, voter_id: int, target_id: int) -> bool:
        """记录投票"""
        if voter_id not in self.alive_players:
            return False
        if target_id not in self.alive_players and target_id != -1:  # -1表示弃权
            return False
        
        self.votes[voter_id] = target_id
        return True
    
    def process_voting(self):
        """处理投票结果"""
        if not self.votes:
            return None
        
        # 统计票数
        vote_count = {}
        for target_id in self.votes.values():
            vote_count[target_id] = vote_count.get(target_id, 0) + 1
        
        # 找出得票最多的（可能多个）
        max_votes = max(vote_count.values()) if vote_count else 0
        candidates = [tid for tid, count in vote_count.items() if count == max_votes]
        
        from datetime import datetime
        
        # 如果只有一个得票最多，则被投票出局
        if len(candidates) == 1 and candidates[0] != -1:
            eliminated = candidates[0]
            if eliminated in self.alive_players:
                self.alive_players.remove(eliminated)
                self.dead_players.add(eliminated)
            
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "day",
                "message": f"🗳️ 投票结束，玩家 {eliminated} 被投票出局（{max_votes} 票）",
                "timestamp": datetime.now().isoformat()
            })
            
            return eliminated
        
        # 平票或无人被投出
        if len(candidates) > 1:
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "day",
                "message": f"⚖️ 投票平票，无人被投票出局",
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "day",
                "message": f"❌ 投票失败，无人被投票出局",
                "timestamp": datetime.now().isoformat()
            })
        
        return None
    
    def check_winner(self) -> Optional[str]:
        """检查胜负条件"""
        alive_werewolves = [pid for pid in self.alive_players if self.roles.get(pid) == Role.WEREWOLF]
        alive_villagers = [pid for pid in self.alive_players if self.roles.get(pid) != Role.WEREWOLF]
        
        from datetime import datetime
        
        # 狼人胜利：狼人数量 >= 村民数量
        if len(alive_werewolves) >= len(alive_villagers):
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "result",
                "message": f"🐺 游戏结束！狼人获胜！",
                "timestamp": datetime.now().isoformat()
            })
            return "werewolves"
        
        # 村民胜利：所有狼人出局
        if len(alive_werewolves) == 0:
            self.game_log.append({
                "type": "game_log",
                "round": self.current_round,
                "phase": "result",
                "message": f"👨‍🌾 游戏结束！村民获胜！",
                "timestamp": datetime.now().isoformat()
            })
            return "villagers"
        
        return None
    
    def get_recent_logs(self, limit: int = 20) -> List[dict]:
        """获取最近的游戏日志"""
        return self.game_log[-limit:]
    
    def get_all_logs(self) -> List[dict]:
        """获取所有游戏日志（包含发言）"""
        return self.game_log
    
    def get_player_role(self, player_id: int) -> Optional[Role]:
        """获取玩家角色"""
        return self.roles.get(player_id)
    
    def get_game_state(self) -> dict:
        """获取当前游戏状态"""
        return {
            "game_id": self.game_id,
            "round": self.current_round,
            "phase": self.current_phase.value,
            "alive_players": list(self.alive_players),
            "dead_players": list(self.dead_players),
            "winner": self.check_winner()
        }

