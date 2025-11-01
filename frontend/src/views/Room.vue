<template>
  <div class="room-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>房间：{{ roomInfo?.room_name || roomCode }}</h2>
          <div>
            <el-button @click="$router.push('/home')">返回大厅</el-button>
            <el-button @click="handleLeaveRoom">离开房间</el-button>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <div class="room-content">
          <!-- 房间信息 -->
          <el-card>
            <template #header>
              <span>房间信息</span>
            </template>
            <p>房间号：{{ roomInfo?.room_code }}</p>
            <p>最大人数：{{ roomInfo?.max_players }}</p>
            <p>状态：{{ getStatusText(roomInfo?.status) }}</p>
          </el-card>
          
          <!-- 玩家列表 -->
          <el-card class="players-card">
            <template #header>
              <span>玩家列表 ({{ players.length }}/{{ roomInfo?.max_players }})</span>
            </template>
            <div class="players-grid">
              <div 
                v-for="player in players" 
                :key="player.id"
                class="player-item"
              >
                <el-avatar :size="60">{{ player.nickname?.[0] || '?' }}</el-avatar>
                <p>{{ player.nickname || '玩家' }}</p>
              </div>
            </div>
          </el-card>
          
          <!-- 聊天区域 -->
          <el-card class="chat-card">
            <template #header>
              <span>房间聊天</span>
            </template>
            <div class="chat-messages" ref="chatMessagesRef">
              <div 
                v-for="(msg, index) in messages" 
                :key="index"
                class="chat-message"
              >
                <strong>{{ msg.user_id }}:</strong> {{ msg.message }}
              </div>
            </div>
            <div class="chat-input">
              <el-input 
                v-model="chatMessage" 
                placeholder="输入消息..."
                @keyup.enter="sendChatMessage"
              >
                <template #append>
                  <el-button @click="sendChatMessage">发送</el-button>
                </template>
              </el-input>
            </div>
          </el-card>
          
          <!-- 控制按钮 -->
          <div class="room-actions" v-if="isOwner">
            <el-button 
              type="primary" 
              size="large"
              @click="handleStartGame"
              :disabled="players.length < 6 || roomInfo?.status !== 'waiting'"
            >
              开始游戏
            </el-button>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRoomStore } from '@/stores/room'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const roomCode = route.params.roomCode
const roomInfo = ref(null)
const players = ref([])
const messages = ref([])
const chatMessage = ref('')
const chatMessagesRef = ref(null)
const isOwner = ref(false)

const getStatusText = (status) => {
  const map = {
    'waiting': '等待中',
    'playing': '游戏中',
    'finished': '已结束'
  }
  return map[status] || status
}

const loadRoomInfo = async () => {
  const room = await roomStore.getRoom(roomCode)
  if (room) {
    roomInfo.value = room
    isOwner.value = room.owner_id === authStore.user?.id
    
    // 如果游戏已开始，跳转到游戏页面
    if (room.status === 'playing') {
      router.push(`/game/${roomCode}`)
    }
  }
}

const connectWebSocket = () => {
  if (authStore.token) {
    const ws = roomStore.connectWebSocket(roomCode, authStore.token)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'connected':
      ElMessage.success('已连接到房间')
      break
    case 'player_joined':
      messages.value.push({
        user_id: data.user_id,
        message: data.message,
        timestamp: new Date()
      })
      scrollToBottom()
      break
    case 'player_left':
      messages.value.push({
        user_id: data.user_id,
        message: data.message,
        timestamp: new Date()
      })
      scrollToBottom()
      break
    case 'chat':
      messages.value.push({
        user_id: data.user_id,
        message: data.message,
        timestamp: data.timestamp
      })
      scrollToBottom()
      break
    case 'game_started':
      router.push(`/game/${roomCode}`)
      break
  }
}

const sendChatMessage = () => {
  if (!chatMessage.value.trim()) return
  
  roomStore.sendMessage({
    type: 'chat',
    message: chatMessage.value,
    timestamp: new Date().toISOString()
  })
  
  chatMessage.value = ''
}

const handleStartGame = () => {
  // TODO: 实现开始游戏逻辑
  ElMessage.info('开始游戏功能开发中...')
}

const handleLeaveRoom = () => {
  roomStore.disconnectWebSocket()
  router.push('/home')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

onMounted(async () => {
  await loadRoomInfo()
  connectWebSocket()
})

onUnmounted(() => {
  roomStore.disconnectWebSocket()
})
</script>

<style scoped>
.room-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h2 {
  color: white;
  margin: 0;
}

.room-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.players-card {
  margin: 20px 0;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 20px;
}

.player-item {
  text-align: center;
}

.player-item p {
  margin-top: 10px;
  font-size: 14px;
}

.chat-card {
  margin: 20px 0;
}

.chat-messages {
  height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.chat-message {
  margin-bottom: 10px;
  padding: 5px;
}

.chat-input {
  margin-top: 10px;
}

.room-actions {
  text-align: center;
  margin-top: 20px;
}
</style>

