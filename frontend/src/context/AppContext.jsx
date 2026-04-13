import React, { createContext, useContext, useState } from 'react'

const AppContext = createContext()

export const AppProvider = ({ children }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [apiHealth, setApiHealth] = useState(null)
  const [apiInfo, setApiInfo] = useState(null)

  const value = {
    loading,
    setLoading,
    error,
    setError,
    clearError: () => setError(null),
    setApiError: (errorMsg) => setError(errorMsg),
    apiHealth,
    setApiHealth,
    apiInfo,
    setApiInfo,
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
