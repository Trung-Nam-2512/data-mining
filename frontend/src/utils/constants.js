/**
 * Application Constants
 */

export const TOXICITY_COLORS = {
  POISONOUS: '#f44336',
  EDIBLE: '#4caf50',
}

export const TOXICITY_LABELS = {
  POISONOUS: '⚠️ Độc',
  EDIBLE: '✅ Ăn được',
}

export const API_ENDPOINTS = {
  HEALTH: '/api/v1/health',
  MODEL_INFO: '/api/v1/model/info',
  CLASSES: '/api/v1/classes',
  PREDICT: '/api/v1/predict/predict',
  PREDICT_BATCH: '/api/v1/predict/batch',
}

export const FILE_TYPES = {
  IMAGE: ['image/jpeg', 'image/jpg', 'image/png'],
}

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const MAX_BATCH_FILES = 10








