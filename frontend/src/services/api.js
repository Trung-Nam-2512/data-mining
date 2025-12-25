/**
 * API Service - Centralized API calls
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // Add auth token if needed
        // const token = localStorage.getItem('token')
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle common errors
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.data)
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error:', error.request)
        } else {
            // Something else happened
            console.error('Error:', error.message)
        }
        return Promise.reject(error)
    }
)

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
    const response = await apiClient.get('/api/v1/model/info')
    return response.data
}

/**
 * Get all classes
 */
export const getClasses = async () => {
    const response = await apiClient.get('/api/v1/classes')
    return response.data
}

/**
 * Predict mushroom from image
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
 * Batch predict multiple images
 */
export const predictBatch = async (files, topK = 3) => {
    const formData = new FormData()
    files.forEach((file) => {
        formData.append('files', file)
    })
    formData.append('top_k', topK.toString())

    const response = await apiClient.post('/api/v1/predict/batch', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
    return response.data
}

export default apiClient

