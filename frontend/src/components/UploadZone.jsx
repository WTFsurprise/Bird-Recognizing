import React, { useState, useRef } from 'react'
import { useApp } from '@/context/AppContext'
import { birdService } from '@/api/birdService'

export const UploadZone = ({ onUploadSuccess }) => {
  const [preview, setPreview] = useState(null)
  const [fileName, setFileName] = useState('')
  const { setLoading, setApiError, clearError } = useApp()
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = async (file) => {
    if (!file) return

    // 验证文件类型
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setApiError('仅支持 JPEG, PNG, WebP 格式的图片')
      return
    }

    // 验证文件大小（50MB）
    if (file.size > 50 * 1024 * 1024) {
      setApiError('文件大小不能超过 50MB')
      return
    }

    clearError()
    setFileName(file.name)

    // 显示预览
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreview(e.target.result)
    }
    reader.readAsDataURL(file)

    // 发送识别请求
    await sendPrediction(file)
  }

  const sendPrediction = async (file) => {
    try {
      setLoading(true)
      const result = await birdService.predictWithVisualization(file)
      if (result.success) {
        onUploadSuccess(result.data)
      } else {
        setApiError(result.error || '识别失败')
      }
    } catch (err) {
      setApiError(err.response?.data?.error || '网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInputChange = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  return (
    <div className="w-full">
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
          }
        `}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileInputChange}
          className="hidden"
        />

        {preview ? (
          <div className="space-y-4">
            <img
              src={preview}
              alt="Preview"
              className="h-48 w-48 object-cover rounded-lg mx-auto"
            />
            <p className="text-gray-700 font-medium">{fileName}</p>
            <p className="text-sm text-gray-500">点击或拖拽来修改图片</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl">🖼️</div>
            <div>
              <p className="text-xl font-semibold text-gray-700">上传鸟类图片</p>
              <p className="text-gray-500 mt-2">拖拽图片到这里，或点击选择</p>
            </div>
            <p className="text-xs text-gray-400">支持 JPEG · PNG · WebP，最大 50MB</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadZone
