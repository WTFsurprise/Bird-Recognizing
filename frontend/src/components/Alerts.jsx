import React from 'react'

export const LoadingSpinner = ({ message = '加载中...' }) => {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="loading-orbit" />
        <p>{message}</p>
        <span>图片正在解析，千问知识卡片也在同步生成</span>
      </div>
    </div>
  )
}

export const ErrorAlert = ({ error, onDismiss }) => {
  if (!error) return null

  return (
    <div className="inline-alert error">
      <div className="inline-alert-icon">!</div>
      <div className="inline-alert-body">
        <h3>当前请求失败</h3>
        <p>{error}</p>
      </div>
      <button
        onClick={onDismiss}
        className="inline-alert-dismiss"
      >
        关闭
      </button>
    </div>
  )
}

export const SuccessAlert = ({ message }) => {
  if (!message) return null

  return (
    <div className="inline-alert success">
      <div className="inline-alert-icon success">✓</div>
      <div className="inline-alert-body">
        <p>{message}</p>
      </div>
    </div>
  )
}

export default { LoadingSpinner, ErrorAlert, SuccessAlert }
