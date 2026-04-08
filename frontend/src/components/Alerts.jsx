import React from 'react'

export const LoadingSpinner = ({ message = '加载中...' }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p className="text-gray-700 font-medium">{message}</p>
        <p className="text-sm text-gray-500 mt-2">请稍候...</p>
      </div>
    </div>
  )
}

export const ErrorAlert = ({ error, onDismiss }) => {
  if (!error) return null

  return (
    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-4">
      <div className="text-2xl">⚠️</div>
      <div className="flex-1">
        <h3 className="font-semibold text-red-800">出错了</h3>
        <p className="text-red-700 text-sm mt-1">{error}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-red-600 hover:text-red-800 font-bold"
      >
        ✕
      </button>
    </div>
  )
}

export const SuccessAlert = ({ message }) => {
  if (!message) return null

  return (
    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-4">
      <div className="text-2xl">✓</div>
      <div className="flex-1">
        <p className="text-green-700 text-sm">{message}</p>
      </div>
    </div>
  )
}

export default { LoadingSpinner, ErrorAlert, SuccessAlert }
