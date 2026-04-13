import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export const birdService = {
  async analyze(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getHistory(limit = 20) {
    const response = await api.get('/api/history', {
      params: { limit },
    })
    return response.data
  },

  async deleteHistory(recordId) {
    const response = await api.delete(`/api/history/${recordId}`)
    return response.data
  },

  async clearHistory() {
    const response = await api.delete('/api/history')
    return response.data
  },

  async healthCheck() {
    const response = await api.get('/api/health')
    return response.data
  },

  async getInfo() {
    const response = await api.get('/api/info')
    return response.data
  },
}

export default api
