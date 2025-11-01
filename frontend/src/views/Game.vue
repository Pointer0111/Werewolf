<template>
  <div class="game-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>游戏进行中 - 房间：{{ roomCode }}</h2>
          <div>
            <el-tag :type="phaseType">{{ phaseText }}</el-tag>
            <span class="round-info">第 {{ currentRound }} 轮</span>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <div class="game-content">
          <!-- 游戏状态 -->
          <el-card class="game-status-card">
            <template #header>
              <span>游戏状态</span>
            </template>
            <div class="status-info">
              <p>当前阶段：{{ phaseText }}</p>
              <p>存活玩家：{{ alivePlayers.length }} 人</p>
              <p v-if="winner">获胜方：{{ winnerText }}</p>
            </div>
          </el-card>
          
          <!-- 玩家区域 -->
          <div class="players-area">
            <div 
              v-for="player in gamePlayers" 
              :key="player.id"
              class="player-card"
              :class="{ 
                'dead': !player.is_alive,
                'current-turn': currentPlayerId === player.user_id 
              }"
            >
              <el-avatar :size="80">{{ player.nickname?.[0] || '?' }}</el-avatar>
              <p class="player-name">{{ player.nickname || '玩家' }}</p>
              <p class="player-role" v-if="showRole(player)">{{ player.role }}</p>
              <el-tag v-if="!player.is_alive" type="danger">已出局</el-tag>
            </div>
          </div>
          
          <!-- 发言区域（白天阶段） -->
          <el-card v-if="currentPhase === 'day'" class="speech-card">
            <template #header>
              <span>发言讨论</span>
            </template>
            <el-input
              v-model="speechContent"
              type="textarea"
              :rows="3"
              placeholder="请输入您的发言..."
              @keyup.ctrl.enter="handleSpeech"
            />
            <div style="margin-top: 10px; text-align: right;">
              <el-button type="primary" @click="handleSpeech" :disabled="!speechContent.trim()">
                发送发言 (Ctrl+Enter)
              </el-button>
            </div>
          </el-card>
          
          <!-- 行动区域 -->
          <el-card v-if="canAct" class="action-card">
            <template #header>
              <span>您的行动</span>
            </template>
            <div v-if="currentPhase === 'night'">
              <el-button 
                v-for="target in alivePlayers" 
                :key="target.id"
                @click="handleNightAction(target.id)"
              >
                选择 {{ target.nickname }}
              </el-button>
            </div>
            <div v-if="currentPhase === 'day'">
              <el-button 
                v-for="target in alivePlayers" 
                :key="target.id"
                @click="handleVote(target.id)"
              >
                投票给 {{ target.nickname }}
              </el-button>
              <el-button @click="handleVote(-1)">弃权</el-button>
            </div>
          </el-card>
          
          <!-- 游戏日志 -->
          <el-card class="game-log-card">
            <template #header>
              <span>游戏日志</span>
            </template>
            <div class="log-content">
              <div 
                v-for="(log, index) in gameLogs" 
                :key="index"
                class="log-item"
              >
                {{ log }}
              </div>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRoomStore } from '@/stores/room'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const roomCode = route.params.roomCode
const currentPhase = ref('night')
const currentRound = ref(1)
const gamePlayers = ref([])
const alivePlayers = computed(() => gamePlayers.value.filter(p => p.is_alive))
const currentPlayerId = ref(null)
const gameLogs = ref([])
const winner = ref(null)
const speechContent = ref('')

const phaseText = computed(() => {
  const map = {
    'night': '夜晚',
    'day': '白天',
    'voting': '投票中',
    'result': '结果'
  }
  return map[currentPhase.value] || currentPhase.value
})

const phaseType = computed(() => {
  const map = {
    'night': 'info',
    'day': 'success',
    'voting': 'warning',
    'result': 'danger'
  }
  return map[currentPhase.value] || 'info'
})

const winnerText = computed(() => {
  return winner.value === 'werewolves' ? '狼人' : '村民'
})

const canAct = computed(() => {
  return currentPlayerId.value === authStore.user?.id && alivePlayers.value.length > 1
})

const showRole = (player) => {
  // TODO: 根据游戏规则决定是否显示角色
  return false
}

const handleNightAction = (targetId) => {
  roomStore.sendMessage({
    type: 'game_action',
    action: 'night_action',
    data: { target_id: targetId }
  })
  ElMessage.success('行动已提交')
}

const handleSpeech = () => {
  if (!speechContent.value.trim()) {
    ElMessage.warning('请输入发言内容')
    return
  }
  
  roomStore.sendMessage({
    type: 'speech',
    content: speechContent.value.trim()
  })
  
  speechContent.value = ''
  ElMessage.success('发言已发送')
}

const handleVote = (targetId) => {
  roomStore.sendMessage({
    type: 'game_action',
    action: 'vote',
    data: { target_id: targetId }
  })
  ElMessage.success('投票已提交')
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'game_status':
      currentPhase.value = data.current_phase
      currentRound.value = data.current_round
      break
    case 'phase_change':
      currentPhase.value = data.phase
      if (data.message) {
        gameLogs.value.push(data.message)
        scrollToBottom()
      }
      break
    case 'game_log':
      // 游戏日志消息
      if (data.message) {
        gameLogs.value.push(data.message)
        scrollToBottom()
      }
      break
    case 'game_action':
      // 处理游戏行动结果
      if (data.data?.log_message) {
        gameLogs.value.push(data.data.log_message)
        scrollToBottom()
      }
      break
    case 'game_over':
      winner.value = data.winner
      if (data.message) {
        gameLogs.value.push(data.message)
        scrollToBottom()
      }
      ElMessage.success(`游戏结束！${winnerText.value}获胜`)
      break
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    const logContent = document.querySelector('.log-content')
    if (logContent) {
      logContent.scrollTop = logContent.scrollHeight
    }
  })
}

onMounted(async () => {
  currentPlayerId.value = authStore.user?.id
  connectWebSocket()
})

const connectWebSocket = () => {
  if (authStore.token) {
    const ws = roomStore.connectWebSocket(roomCode, authStore.token)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
  }
}

onUnmounted(() => {
  roomStore.disconnectWebSocket()
})
</script>

<style scoped>
.game-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  color: white;
}

.header-content h2 {
  margin: 0;
  color: white;
}

.round-info {
  margin-left: 20px;
  color: white;
}

.game-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.game-status-card {
  margin-bottom: 20px;
}

.status-info {
  display: flex;
  gap: 30px;
}

.players-area {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.player-card {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  transition: all 0.3s;
}

.player-card.dead {
  opacity: 0.5;
  background: #f0f0f0;
}

.player-card.current-turn {
  border: 3px solid #409eff;
  box-shadow: 0 0 10px #409eff;
}

.player-name {
  margin-top: 10px;
  font-weight: bold;
}

.player-role {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.speech-card {
  margin: 20px 0;
}

.action-card {
  margin: 20px 0;
}

.game-log-card {
  margin-top: 20px;
}

.log-content {
  height: 200px;
  overflow-y: auto;
}

.log-item {
  padding: 8px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  line-height: 1.5;
}

.log-item:last-child {
  border-bottom: none;
}

.log-content::-webkit-scrollbar {
  width: 6px;
}

.log-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.log-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

