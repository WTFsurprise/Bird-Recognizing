import React, { createContext, useContext, useState, useCallback } from 'react'

const AppContext = createContext()

export const AppProvider = ({ children }) => {
  const [predictions, setPredictions] = useState([])
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiHealth, setApiHealth] = useState(null)

  const addPrediction = useCallback((prediction) => {
    setPredictions([prediction, ...predictions])
  }, [predictions])

  const clearPredictions = useCallback(() => {
    setPredictions([])
  }, [])

  const addHistoryRecord = useCallback((record) => {
    setHistory([record, ...history])
  }, [history])

  const removeHistoryRecord = useCallback((recordId) => {
    setHistory(history.filter(r => r.id !== recordId))
  }, [history])

  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])

  const setApiError = useCallback((errorMsg) => {
    setError(errorMsg)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const value = {
    predictions,
    addPrediction,
    clearPredictions,
    history,
    addHistoryRecord,
    removeHistoryRecord,
    clearHistory,
    loading,
    setLoading,
    error,
    setApiError,
    clearError,
    apiHealth,
    setApiHealth,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
