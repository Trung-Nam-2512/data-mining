/**
 * Helper Functions
 */

/**
 * Format confidence percentage
 */
export const formatConfidence = (confidence) => {
  return `${confidence.toFixed(2)}%`
}

/**
 * Get toxicity color
 */
export const getToxicityColor = (isPoisonous) => {
  return isPoisonous ? '#f44336' : '#4caf50'
}

/**
 * Validate image file
 */
export const validateImageFile = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  const maxSize = 10 * 1024 * 1024 // 10MB

  if (!validTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Vui lòng chọn file ảnh (JPG, JPEG, PNG)',
    }
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'File quá lớn. Kích thước tối đa: 10MB',
    }
  }

  return { valid: true }
}

/**
 * Create image preview from file
 */
export const createImagePreview = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}



