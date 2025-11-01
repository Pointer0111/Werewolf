<template>
  <div class="home-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🐺 狼人杀游戏大厅</h1>
          <div class="header-actions">
            <el-button @click="$router.push('/profile')">
              <el-icon><User /></el-icon>
              个人中心
            </el-button>
            <el-button @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <div class="main-content">
          <!-- 创建房间区域 -->
          <el-card class="create-room-card">
            <template #header>
              <span>创建房间</span>
            </template>
            <el-form :model="createForm" label-width="100px">
              <el-form-item label="房间名称">
                <el-input v-model="createForm.room_name" placeholder="请输入房间名称" />
              </el-form-item>
              <el-form-item label="最大人数">
                <el-select v-model="createForm.max_players" style="width: 100%">
                  <el-option label="6人" :value="6" />
                  <el-option label="8人" :value="8" />
                  <el-option label="10人" :value="10" />
                  <el-option label="12人" :value="12" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleCreateRoom" :loading="creating">
                  创建房间
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 加入房间区域 -->
          <el-card class="join-room-card">
            <template #header>
              <span>加入房间</span>
            </template>
            <el-form :model="joinForm" label-width="100px">
              <el-form-item label="房间号">
                <el-input v-model="joinForm.room_code" placeholder="请输入房间号" />
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="handleJoinRoom" :loading="joining">
                  加入房间
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 房间列表 -->
          <el-card class="rooms-list-card">
            <template #header>
              <div class="rooms-header">
                <span>房间列表</span>
                <el-button @click="fetchRooms">刷新</el-button>
              </div>
            </template>
            <el-table :data="rooms" style="width: 100%">
              <el-table-column prop="room_code" label="房间号" width="120" />
              <el-table-column prop="room_name" label="房间名称" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button 
                    size="small" 
                    @click="joinRoomByCode(scope.row.room_code)"
                    :disabled="scope.row.status !== 'waiting'"
                  >
                    加入
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useRoomStore } from '@/stores/room'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const rooms = ref([])
const creating = ref(false)
const joining = ref(false)

const createForm = reactive({
  room_name: '',
  max_players: 12
})

const joinForm = reactive({
  room_code: ''
})

const getStatusType = (status) => {
  const map = {
    'waiting': 'success',
    'playing': 'warning',
    'finished': 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'waiting': '等待中',
    'playing': '游戏中',
    'finished': '已结束'
  }
  return map[status] || status
}

const fetchRooms = async () => {
  await roomStore.fetchRooms()
  rooms.value = roomStore.rooms
}

const handleCreateRoom = async () => {
  if (!createForm.room_name.trim()) {
    ElMessage.warning('请输入房间名称')
    return
  }
  
  creating.value = true
  const result = await roomStore.createRoom(createForm)
  creating.value = false
  
  if (result.success) {
    ElMessage.success('房间创建成功')
    router.push(`/room/${result.room.room_code}`)
  } else {
    ElMessage.error(result.message)
  }
}

const handleJoinRoom = async () => {
  if (!joinForm.room_code.trim()) {
    ElMessage.warning('请输入房间号')
    return
  }
  
  joining.value = true
  const result = await roomStore.joinRoom(joinForm.room_code.toUpperCase())
  joining.value = false
  
  if (result.success) {
    ElMessage.success('加入房间成功')
    router.push(`/room/${result.room.room_code}`)
  } else {
    ElMessage.error(result.message)
  }
}

const joinRoomByCode = async (roomCode) => {
  const result = await roomStore.joinRoom(roomCode)
  if (result.success) {
    router.push(`/room/${result.room.room_code}`)
  } else {
    ElMessage.error(result.message)
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchRooms()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  color: white;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.create-room-card,
.join-room-card {
  margin-bottom: 20px;
}

.rooms-list-card {
  margin-top: 20px;
}

.rooms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

