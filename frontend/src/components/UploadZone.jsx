import React, { useRef, useState } from 'react'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE = 50 * 1024 * 1024

export const UploadZone = ({ previewUrl, fileName, onFileSelected, disabled = false, statusText = '' }) => {
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const validateFile = (file) => {
    if (!file) {
      return 'Please choose an image file'
    }

    if (!ACCEPTED_TYPES.includes(file.type)) {
      return 'Only JPEG, PNG, and WebP images are supported'
    }

    if (file.size > MAX_SIZE) {
      return 'Image size must be 50MB or less'
    }

    return null
  }

  const emitFile = (file) => {
    const message = validateFile(file)
    if (message) {
      onFileSelected(null, message)
      return
    }

    onFileSelected(file, null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    emitFile(event.dataTransfer.files?.[0])
  }

  const handleInputChange = (event) => {
    emitFile(event.target.files?.[0])
  }

  return (
    <div className="upload-shell">
      <div
        className={`upload-zone ${isDragging ? 'is-dragging' : ''} ${disabled ? 'is-disabled' : ''}`}
        onDragEnter={(event) => {
          event.preventDefault()
          if (!disabled) {
            setIsDragging(true)
          }
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={(event) => {
          event.preventDefault()
          setIsDragging(false)
        }}
        onDrop={handleDrop}
        onClick={() => {
          if (!disabled) {
            fileInputRef.current?.click()
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleInputChange}
          className="hidden"
          disabled={disabled}
        />

        {previewUrl ? (
          <div className="upload-preview">
            <img src={previewUrl} alt="preview" className="upload-preview-image" />
            <div className="upload-preview-meta">
              <p className="upload-preview-title">{fileName || 'Image Selected'}</p>
              <p className="upload-preview-text">Click or drag to replace the image</p>
              {disabled && statusText && (
                <div className="upload-inline-status" role="status" aria-live="polite">
                  <span className="upload-inline-status-dot" />
                  <span>{statusText}</span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="upload-empty">
            <div className="upload-icon">📷</div>
            <h3>Drop the image here</h3>
            <p>Or click anywhere to choose a bird photo</p>
            <span>Supports JPEG, PNG, WebP, max 50MB</span>
            {disabled && statusText && (
              <div className="upload-inline-status" role="status" aria-live="polite">
                <span className="upload-inline-status-dot" />
                <span>{statusText}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadZone
