import axios from 'axios'

const API_BASE = process.env.REACT_APP_API_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export const birdService = {
  // 基础识别
  async predict(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // 带热力图的识别
  async predictWithVisualization(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/predict/with_visualization', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // 获取历史记录
  async getHistory(limit = 20) {
    const response = await api.get('/api/history', {
      params: { limit },
    })
    return response.data
  },

  // 删除单条记录
  async deleteHistory(recordId) {
    const response = await api.delete(`/api/history/${recordId}`)
    return response.data
  },

  // 清空所有历史记录
  async clearHistory() {
    const response = await api.delete('/api/history')
    return response.data
  },

  // 健康检查
  async healthCheck() {
    const response = await api.get('/api/health')
    return response.data
  },

  // 获取API信息
  async getInfo() {
    const response = await api.get('/api/info')
    return response.data
  },
}

export default api
