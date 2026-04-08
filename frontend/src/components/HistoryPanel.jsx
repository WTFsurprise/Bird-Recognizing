import React, { useEffect, useState } from 'react'
import { useApp } from '@/context/AppContext'
import { birdService } from '@/api/birdService'

export const HistoryPanel = () => {
  const { history, setLoading, setApiError, clearError } = useApp()
  const [localHistory, setLocalHistory] = useState([])

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      clearError()
      const result = await birdService.getHistory(50)
      if (result.success) {
        setLocalHistory(result.data)
      }
    } catch (err) {
      setApiError('加载历史记录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('确定删除此记录吗？')) return

    try {
      setLoading(true)
      clearError()
      const result = await birdService.deleteHistory(recordId)
      if (result.success) {
        setLocalHistory(localHistory.filter(r => r.id !== recordId))
      }
    } catch (err) {
      setApiError('删除记录失败')
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = async () => {
    if (!window.confirm('确定清空所有历史记录吗？')) return

    try {
      setLoading(true)
      clearError()
      const result = await birdService.clearHistory()
      if (result.success) {
        setLocalHistory([])
      }
    } catch (err) {
      setApiError('清空历史记录失败')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return isoString
    }
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">识别历史</h2>
        {localHistory.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="btn-danger text-sm"
          >
            清空历史
          </button>
        )}
      </div>

      {localHistory.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">暂无历史记录</p>
          <p className="text-gray-400 mt-2">上传图片后会显示识别历史</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {localHistory.map((record) => (
            <div
              key={record.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1">
                <p className="font-medium text-gray-800">{record.species}</p>
                <div className="flex items-center gap-4 mt-1">
                  <p className="text-sm text-gray-600">
                    置信度: {(record.confidence * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDate(record.timestamp)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDeleteRecord(record.id)}
                className="ml-4 px-3 py-1 text-sm bg-red-100 text-red-600 rounded hover:bg-red-200 transition-colors"
              >
                删除
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default HistoryPanel
