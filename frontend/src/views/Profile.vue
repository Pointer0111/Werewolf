<template>
  <div class="profile-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>个人中心</h2>
          <el-button @click="$router.push('/home')">返回大厅</el-button>
        </div>
      </el-header>
      
      <el-main>
        <div class="profile-content">
          <el-card>
            <template #header>
              <span>个人信息</span>
            </template>
            <div v-if="user">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
                <el-descriptions-item label="昵称">{{ user.nickname || '未设置' }}</el-descriptions-item>
                <el-descriptions-item label="总游戏数">{{ user.total_games || 0 }}</el-descriptions-item>
                <el-descriptions-item label="胜利次数">{{ user.win_games || 0 }}</el-descriptions-item>
                <el-descriptions-item label="胜率">
                  <el-tag :type="getWinRateType(user.win_rate)">
                    {{ (user.win_rate * 100).toFixed(1) }}%
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <el-divider />
              
              <el-form :model="updateForm" label-width="100px" style="max-width: 500px">
                <el-form-item label="修改昵称">
                  <el-input v-model="updateForm.nickname" placeholder="请输入新昵称" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleUpdate">更新信息</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()
const user = ref(null)
const updateForm = reactive({
  nickname: ''
})

const getWinRateType = (rate) => {
  if (rate >= 0.6) return 'success'
  if (rate >= 0.4) return 'warning'
  return 'danger'
}

const loadUserInfo = async () => {
  await authStore.fetchUserInfo()
  user.value = authStore.user
  updateForm.nickname = user.value?.nickname || ''
}

const handleUpdate = async () => {
  try {
    const response = await api.put('/users/me', updateForm)
    ElMessage.success('更新成功')
    await loadUserInfo()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-container {
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

.profile-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
</style>

