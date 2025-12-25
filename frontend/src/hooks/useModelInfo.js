/**
 * Custom Hook: useModelInfo
 * Fetch and manage model information
 */
import { useState, useEffect } from 'react'
import { getModelInfo } from '../services/api'

export const useModelInfo = () => {
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getModelInfo()
        setModelInfo(data)
      } catch (err) {
        setError(err.message || 'Failed to load model info')
        console.error('Failed to load model info:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchModelInfo()
  }, [])

  return { modelInfo, loading, error }
}



