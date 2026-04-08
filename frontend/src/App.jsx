import React, { useState, useEffect } from 'react'
import { AppProvider, useApp } from '@/context/AppContext'
import UploadZone from '@/components/UploadZone'
import ResultCard from '@/components/ResultCard'
import HistoryPanel from '@/components/HistoryPanel'
import { LoadingSpinner, ErrorAlert } from '@/components/Alerts'
import { birdService } from '@/api/birdService'

const AppContent = () => {
  const { loading, error, setApiError, clearError, setApiHealth } = useApp()
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('upload') // upload, result, history

  useEffect(() => {
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const health = await birdService.healthCheck()
      setApiHealth(health)
    } catch (err) {
      setApiError('无法连接到后端API，请确保服务器正在运行')
    }
  }

  const handleUploadSuccess = (data) => {
    setResult(data)
    setActiveTab('result')
  }

  const handleRetry = () => {
    setResult(null)
    setActiveTab('upload')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">🐦 鸟类识别平台</h1>
          <p className="text-blue-100 text-lg">使用深度学习自动识别你上传的鸟类图片</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <ErrorAlert
            error={error}
            onDismiss={clearError}
          />
        )}

        {/* 主容器 */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 左侧主内容区域 */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {/* 标签栏 */}
              <div className="flex gap-2 bg-white/20 backdrop-blur-md rounded-lg p-1 w-fit">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`px-6 py-2 rounded-md font-medium transition-all ${
                    activeTab === 'upload'
                      ? 'bg-white text-blue-600 shadow-lg'
                      : 'text-white hover:bg-white/10'
                  }`}
                >
                  📤 上传
                </button>
                {result && (
                  <button
                    onClick={() => setActiveTab('result')}
                    className={`px-6 py-2 rounded-md font-medium transition-all ${
                      activeTab === 'result'
                        ? 'bg-white text-blue-600 shadow-lg'
                        : 'text-white hover:bg-white/10'
                    }`}
                  >
                    📊 结果
                  </button>
                )}
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-6 py-2 rounded-md font-medium transition-all ${
                    activeTab === 'history'
                      ? 'bg-white text-blue-600 shadow-lg'
                      : 'text-white hover:bg-white/10'
                  }`}
                >
                  📜 历史
                </button>
              </div>

              {/* 内容区域 */}
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                {activeTab === 'upload' && (
                  <UploadZone onUploadSuccess={handleUploadSuccess} />
                )}

                {activeTab === 'result' && (
                  <div>
                    <ResultCard result={result} />
                    <button
                      onClick={handleRetry}
                      className="mt-6 btn-primary w-full text-center"
                    >
                      📤 上传新图片
                    </button>
                  </div>
                )}

                {activeTab === 'history' && <HistoryPanel />}
              </div>
            </div>
          </div>

          {/* 右侧信息面板 */}
          <div className="lg:col-span-1">
            <div className="bg-white/20 backdrop-blur-md rounded-2xl p-6 text-white space-y-6 sticky top-8">
              <div>
                <h3 className="text-lg font-bold mb-3">📋 使用说明</h3>
                <ul className="text-sm space-y-2 opacity-90">
                  <li>✓ 支持 JPEG, PNG, WebP 格式</li>
                  <li>✓ 最大文件 50 MB</li>
                  <li>✓ 支持 313 种鸟类识别</li>
                  <li>✓ 返回 Top-3 预测结果</li>
                  <li>✓ 提供热力图可视化</li>
                </ul>
              </div>

              <div className="border-t border-white/30 pt-6">
                <h3 className="text-lg font-bold mb-3">🔗 API 信息</h3>
                <div className="text-sm space-y-2 opacity-90">
                  <div className="flex items-center gap-2">
                    <span>服务器状态:</span>
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  </div>
                  <p className="text-xs text-gray-200 break-all">
                    {process.env.REACT_APP_API_URL ||
                      import.meta.env.VITE_API_URL ||
                      'http://localhost:8000'}
                  </p>
                </div>
              </div>

              <div className="border-t border-white/30 pt-6">
                <h3 className="text-sm font-bold mb-2">💡 关于模型</h3>
                <p className="text-xs opacity-90">
                  采用 Swin Transformer 架构，在 15,650 张鸟类图片上训练，验证集准确率 65.43%。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 加载动画 */}
      {loading && <LoadingSpinner message="正在识别中..." />}
    </div>
  )
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}

export default App
