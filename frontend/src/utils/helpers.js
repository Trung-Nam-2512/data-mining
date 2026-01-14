/**
 * Utility Helper Functions
 */

/**
 * Format confidence percentage
 */
export const formatConfidence = (confidence) => {
  return `${confidence.toFixed(2)}%`
}

/**
 * Format file size to human readable
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Format timestamp to readable date
 */
export const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Get toxicity color class
 */
export const getToxicityColor = (toxicityCode) => {
  return toxicityCode === 'P' ? 'text-red-600' : 'text-green-600'
}

/**
 * Get toxicity badge class
 */
export const getToxicityBadgeClass = (toxicityCode) => {
  return toxicityCode === 'P' ? 'badge-danger' : 'badge-success'
}

/**
 * Get confidence color based on value
 */
export const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return 'text-green-600'
  if (confidence >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

/**
 * Get confidence badge class
 */
export const getConfidenceBadgeClass = (confidence) => {
  if (confidence >= 80) return 'badge-success'
  if (confidence >= 60) return 'badge-warning'
  return 'badge-danger'
}

/**
 * Validate image file
 */
export const validateImage = (file) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  const maxSize = 10 * 1024 * 1024 // 10MB

  if (!file) {
    return { valid: false, error: 'Vui lòng chọn file' }
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Chỉ chấp nhận file ảnh (JPG, PNG, WEBP)' }
  }

  if (file.size > maxSize) {
    return { valid: false, error: 'File không được vượt quá 10MB' }
  }

  return { valid: true }
}

/**
 * Create preview URL from file
 */
export const createPreviewURL = (file) => {
  return URL.createObjectURL(file)
}

/**
 * Revoke preview URL
 */
export const revokePreviewURL = (url) => {
  URL.revokeObjectURL(url)
}

/**
 * Download image from base64
 */
export const downloadBase64Image = (base64Data, filename = 'gradcam.png') => {
  const link = document.createElement('a')
  link.href = `data:image/png;base64,${base64Data}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    console.error('Failed to copy:', err)
    return false
  }
}

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 50) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Format processing time
 */
export const formatProcessingTime = (ms) => {
  if (ms < 1000) {
    return `${Math.round(ms)}ms`
  }
  return `${(ms / 1000).toFixed(2)}s`
}
