/**
 * Custom Hook: useClasses
 * Fetch and manage classes information
 */
import { useState, useEffect } from 'react'
import { getClasses } from '../services/api'

export const useClasses = () => {
  const [classes, setClasses] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getClasses()
        setClasses(data)
      } catch (err) {
        setError(err.message || 'Failed to load classes')
        console.error('Failed to load classes:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchClasses()
  }, [])

  return { classes, loading, error }
}





