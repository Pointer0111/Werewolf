import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useRoomStore = defineStore('room', () => {
  const rooms = ref([])
  const currentRoom = ref(null)
  const wsConnection = ref(null)
  
  async function fetchRooms() {
    try {
      const response = await api.get('/rooms/')
      rooms.value = response.data
    } catch (error) {
      console.error('获取房间列表失败:', error)
    }
  }
  
  async function createRoom(roomData) {
    try {
      const response = await api.post('/rooms/', roomData)
      currentRoom.value = response.data
      return { success: true, room: response.data }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '创建房间失败' 
      }
    }
  }
  
  async function joinRoom(roomCode) {
    try {
      const response = await api.post('/rooms/join', { room_code: roomCode })
      currentRoom.value = response.data
      return { success: true, room: response.data }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '加入房间失败' 
      }
    }
  }
  
  async function getRoom(roomCode) {
    try {
      const response = await api.get(`/rooms/${roomCode}`)
      currentRoom.value = response.data
      return response.data
    } catch (error) {
      console.error('获取房间信息失败:', error)
      return null
    }
  }
  
  function connectWebSocket(roomCode, token) {
    const wsUrl = `ws://localhost:8000/ws/room/${roomCode}?token=${token}`
    wsConnection.value = new WebSocket(wsUrl)
    
    wsConnection.value.onopen = () => {
      console.log('WebSocket连接已建立')
    }
    
    wsConnection.value.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
    
    wsConnection.value.onclose = () => {
      console.log('WebSocket连接已关闭')
    }
    
    return wsConnection.value
  }
  
  function disconnectWebSocket() {
    if (wsConnection.value) {
      wsConnection.value.close()
      wsConnection.value = null
    }
  }
  
  function sendMessage(message) {
    if (wsConnection.value && wsConnection.value.readyState === WebSocket.OPEN) {
      wsConnection.value.send(JSON.stringify(message))
    }
  }
  
  return {
    rooms,
    currentRoom,
    wsConnection,
    fetchRooms,
    createRoom,
    joinRoom,
    getRoom,
    connectWebSocket,
    disconnectWebSocket,
    sendMessage
  }
})

