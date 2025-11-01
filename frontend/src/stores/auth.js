import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  async function login(username, password) {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return { success: true }
    } catch (error) {
      return { 
      success: false, 
      message: error.response?.data?.detail || '登录失败' 
    }
    }
  }
  
  async function register(userData) {
    try {
      await api.post('/auth/register', userData)
      return { success: true, message: '注册成功，请登录' }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '注册失败' 
      }
    }
  }
  
  async function fetchUserInfo() {
    try {
      const response = await api.get('/users/me')
      user.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }
  
  // 初始化时获取用户信息
  if (token.value) {
    fetchUserInfo()
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    fetchUserInfo,
    logout
  }
})

