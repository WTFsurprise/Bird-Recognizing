import React, { useEffect, useRef, useState } from 'react'
import { AppProvider, useApp } from '@/context/AppContext'
import UploadZone from '@/components/UploadZone'
import ResultCard from '@/components/ResultCard'
import HistoryPanel from '@/components/HistoryPanel'
import { LoadingSpinner, ErrorAlert } from '@/components/Alerts'
import { birdService } from '@/api/birdService'

const AppContent = () => {
  const { loading, setLoading, error, setApiError, clearError, setApiHealth, setApiInfo, apiHealth } = useApp()
  const [analysis, setAnalysis] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [fileName, setFileName] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [historyRefreshSignal, setHistoryRefreshSignal] = useState(0)
  const previewRef = useRef('')

  useEffect(() => {
    initializeDashboard()
    return () => {
      if (previewRef.current) {
        URL.revokeObjectURL(previewRef.current)
      }
    }
  }, [])

  const initializeDashboard = async () => {
    try {
      const [health, info] = await Promise.all([
        birdService.healthCheck(),
        birdService.getInfo(),
      ])
      setApiHealth(health)
      setApiInfo(info)
    } catch (error) {
      setApiError('Cannot connect to the backend API, please make sure the service is running.')
    }
  }

  const analyzeFile = async (file) => {
    setLoading(true)
    try {
      clearError()
      const response = await birdService.analyze(file)
      if (response.success) {
        setAnalysis(response.data)
        setHistoryRefreshSignal((current) => current + 1)
      } else {
        setApiError(response.error || 'Analysis failed')
      }
    } catch (error) {
      setApiError(error.response?.data?.error || 'Network error, please try again later')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelected = async (file, message) => {
    if (message) {
      setApiError(message)
      return
    }

    if (!file) {
      return
    }

    clearError()
    setSelectedFile(file)
    setFileName(file.name)

    if (previewRef.current) {
      URL.revokeObjectURL(previewRef.current)
    }

    const objectUrl = URL.createObjectURL(file)
    previewRef.current = objectUrl
    setPreviewUrl(objectUrl)
    setAnalysis(null)
    await analyzeFile(file)
  }

  const handleReset = () => {
    setAnalysis(null)
    setSelectedFile(null)
    setFileName('')
    clearError()

    if (previewRef.current) {
      URL.revokeObjectURL(previewRef.current)
      previewRef.current = ''
    }

    setPreviewUrl('')
  }

  const statusCards = [
    {
      label: 'Backend Status',
      value: apiHealth?.status === 'healthy' ? 'Online' : 'Unknown',
      tone: apiHealth?.status === 'healthy' ? 'positive' : 'neutral',
    },
    {
      label: 'Bird CV Model',
      value: apiHealth?.model_loaded ? 'Ready' : 'Demo Mode',
      tone: apiHealth?.model_loaded ? 'positive' : 'warning',
    },
    {
      label: 'Qwen Agent',
      value: apiHealth?.agent_ready ? 'Enabled' : 'Fallback',
      tone: apiHealth?.agent_ready ? 'positive' : 'warning',
    },
  ]

  return (
    <div className="app-shell">
      <div className="app-backdrop app-backdrop-one" />
      <div className="app-backdrop app-backdrop-two" />
      <div className="app-backdrop app-backdrop-three" />

      <main className="app-container">
        <header className="hero-panel glass-panel">
          <div className="hero-copy">
            <p className="eyebrow">Bird Discovery Platform</p>
            <h1>Bird Identification & Knowledge Studio</h1>
            <p className="hero-description">
              Upload a bird photo and the backend will identify it first, then use Qwen to generate species knowledge, observation tips, and conservation notes.
            </p>

            <div className="hero-actions">
              <button className="primary-button" onClick={() => selectedFile && analyzeFile(selectedFile)} disabled={!selectedFile || loading}>
                Reanalyze Current Image
              </button>
              <button className="ghost-button" onClick={handleReset} disabled={loading && !analysis}>
                Clear Result
              </button>
            </div>
          </div>

          <div className="hero-stats">
            {statusCards.map((card) => (
              <div key={card.label} className={`status-card ${card.tone}`}>
                <span>{card.label}</span>
                <strong>{card.value}</strong>
              </div>
            ))}
          </div>
        </header>

        {error && <ErrorAlert error={error} onDismiss={clearError} />}

        <div className="dashboard-grid">
          <section className="main-column">
            <section className="glass-panel upload-panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Upload Image</p>
                  <h3>Drag or Click to Select a Bird Photo</h3>
                </div>
              </div>

              <UploadZone
                previewUrl={previewUrl}
                fileName={fileName}
                onFileSelected={handleFileSelected}
                disabled={loading}
                statusText={loading ? 'Image submitted, identifying bird now...' : ''}
              />

              {loading && (
                <div className="upload-progress-banner" role="status" aria-live="polite">
                  <div className="upload-progress-dot" />
                  <div>
                    <strong>Identifying Image</strong>
                    <p>Model inference and knowledge generation in progress, please wait.</p>
                  </div>
                </div>
              )}

              <div className="upload-footer">
                <div>
                  <span className="upload-footer-label">Current File</span>
                  <strong>{fileName || 'Not selected'}</strong>
                </div>
                <div className="upload-footer-actions">
                  <button className="ghost-button" onClick={handleReset} disabled={loading}>
                    Reset
                  </button>
                </div>
              </div>
            </section>

            <section className="result-area">
              {analysis ? (
                <ResultCard result={analysis} />
              ) : (
                <section className="glass-panel empty-analysis-panel">
                  <div className="empty-state">
                    <p>No Analysis Yet</p>
                    <span>After uploading an image, model results and knowledge cards will appear here.</span>
                  </div>
                </section>
              )}
            </section>

            <HistoryPanel refreshSignal={historyRefreshSignal} />
          </section>
        </div>
      </main>

      {loading && <LoadingSpinner message="Identifying image and preparing knowledge cards..." />}
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
