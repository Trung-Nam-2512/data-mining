/**
 * API Service - Centralized API calls for Mushroom Classification
 * Backend: FastAPI on port 1356
 */
import axios from 'axios'

// Use relative path in production (same origin), absolute URL in development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
    (import.meta.env.PROD ? '' : 'http://localhost:1356')

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds for model inference
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor with better error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.data)
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error: No response from server')
        } else {
            // Something else happened
            console.error('Error:', error.message)
        }
        return Promise.reject(error)
    }
)

// ============================================
// Health & Info Endpoints
// ============================================

/**
 * Health check
 */
export const checkHealth = async () => {
    const response = await apiClient.get('/api/v1/health')
    return response.data
}

/**
 * Get model information
 */
export const getModelInfo = async () => {
    const response = await apiClient.get('/api/v1/models/info')
    return response.data
}

/**
 * Get all classes with toxicity info
 */
export const getClasses = async () => {
    const response = await apiClient.get('/api/v1/models/classes')
    return response.data
}

// ============================================
// Prediction Endpoints
// ============================================

/**
 * Single image prediction
 * @param {File} file - Image file
 * @param {number} topK - Number of top predictions to return (default: 3)
 * @returns {Promise} - Prediction result with ensemble and individual models
 */
export const predictMushroom = async (file, topK = 3) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('top_k', topK.toString())

    const response = await apiClient.post('/api/v1/predict', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
    return response.data
}

/**
 * Batch predict multiple images (max 5)
 * @param {File[]} files - Array of image files (max 5)
 * @param {number} topK - Number of top predictions (default: 3)
 * @returns {Promise} - Array of predictions
 */
export const predictBatch = async (files, topK = 3) => {
    if (files.length > 5) {
        throw new Error('Tối đa 5 ảnh mỗi lần')
    }

    const formData = new FormData()
    files.forEach((file) => {
        formData.append('files', file)
    })
    formData.append('top_k', topK.toString())

    const response = await apiClient.post('/api/v1/predict/batch', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for batch
    })
    return response.data
}

// ============================================
// Grad-CAM Endpoints
// ============================================

/**
 * Generate Grad-CAM for specific model
 * @param {File} file - Image file
 * @param {string} modelName - Model name (resnet50, efficientnet_b0, mobilenet_v3_large)
 * @param {number} alpha - Overlay alpha (0-1, default: 0.45)
 * @returns {Promise} - Grad-CAM result with base64 image
 */
export const generateGradCAM = async (file, modelName, alpha = 0.45) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_name', modelName)
    formData.append('alpha', alpha.toString())

    const response = await apiClient.post('/api/v1/gradcam', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
    return response.data
}

/**
 * Generate Grad-CAM for all models
 * @param {File} file - Image file
 * @param {number} alpha - Overlay alpha (0-1, default: 0.45)
 * @returns {Promise} - Grad-CAM results for all models
 */
export const generateGradCAMAll = async (file, alpha = 0.45) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('alpha', alpha.toString())

    const response = await apiClient.post('/api/v1/gradcam/all', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        timeout: 90000, // 90 seconds for all models
    })
    return response.data
}

// ============================================
// History & Statistics Endpoints
// ============================================

/**
 * Get prediction statistics
 * @returns {Promise} - Statistics summary
 */
export const getStatistics = async () => {
    const response = await apiClient.get('/api/v1/statistics')
    return response.data
}

/**
 * Get prediction history
 * @param {number} limit - Number of records (default: 10)
 * @param {number} skip - Skip records for pagination (default: 0)
 * @returns {Promise} - History records
 */
export const getHistory = async (limit = 10, skip = 0) => {
    const response = await apiClient.get('/api/v1/history', {
        params: { limit, skip }
    })
    return response.data
}

// ============================================
// Utilities
// ============================================

/**
 * Validate image file
 * @param {File} file - File to validate
 * @returns {boolean} - Is valid
 */
export const validateImageFile = (file) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!allowedTypes.includes(file.type)) {
        throw new Error('Chỉ chấp nhận file ảnh (JPG, PNG, WEBP)')
    }

    if (file.size > maxSize) {
        throw new Error('File ảnh không được vượt quá 10MB')
    }

    return true
}

export default apiClient
