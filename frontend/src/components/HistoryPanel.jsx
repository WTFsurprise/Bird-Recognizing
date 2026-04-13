import React, { useEffect, useState } from 'react'
import { useApp } from '@/context/AppContext'
import { birdService } from '@/api/birdService'

const formatDate = (isoString) => {
  try {
    return new Date(isoString).toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoString
  }
}

export const HistoryPanel = ({ refreshSignal = 0 }) => {
  const { setLoading, setApiError, clearError } = useApp()
  const [history, setHistory] = useState([])

  const loadHistory = async () => {
    try {
      setLoading(true)
      clearError()
      const result = await birdService.getHistory(50)
      if (result.success) {
        setHistory(result.data || [])
      }
    } catch (error) {
      setApiError('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [refreshSignal])

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('Confirm to delete this record?')) {
      return
    }

    try {
      setLoading(true)
      clearError()
      const result = await birdService.deleteHistory(recordId)
      if (result.success) {
        setHistory((current) => current.filter((item) => item.id !== recordId))
      }
    } catch (error) {
      setApiError('Failed to delete record')
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = async () => {
    if (!window.confirm('Confirm to clear all history records?')) {
      return
    }

    try {
      setLoading(true)
      clearError()
      const result = await birdService.clearHistory()
      if (result.success) {
        setHistory([])
      }
    } catch (error) {
      setApiError('Failed to clear history')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="glass-panel history-panel">
      <div className="section-heading history-heading">
        <div>
          <p className="eyebrow">History</p>
          <h3>Recent Analyses</h3>
        </div>
        <button className="ghost-button" onClick={handleClearHistory} disabled={history.length === 0}>
          Clear History
        </button>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <p>No History Yet</p>
          <span>Each recognition run will be kept here with a summary and top-3 candidates.</span>
        </div>
      ) : (
        <div className="history-list">
          {history.map((record) => (
            <article className="history-item" key={record.id}>
              <div className="history-item-main">
                <div className="history-item-title-row">
                  <h4>{record.species}</h4>
                  <span>{(Number(record.confidence || 0) * 100).toFixed(1)}%</span>
                </div>
                <p>{record.summary || 'No summary'}</p>
                <div className="history-item-meta">
                  <span>{formatDate(record.timestamp)}</span>
                  <span>{record.model_ready ? 'Real Model' : 'Demo Mode'}</span>
                  <span>{record.agent_enabled ? 'Qwen Enabled' : 'Local Fallback'}</span>
                </div>
              </div>

              <div className="history-item-actions">
                <button className="history-delete-button" onClick={() => handleDeleteRecord(record.id)}>
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default HistoryPanel
