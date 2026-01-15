/**
 * Loading Spinner Component
 */
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

const LoadingSpinner = ({ message = 'Đang xử lý...', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center gap-4 py-8"
    >
      <Loader2 className={`${sizeClasses[size]} text-green-600 animate-spin`} />
      {message && (
        <p className="text-gray-600 font-medium">{message}</p>
      )}
    </motion.div>
  )
}

export default LoadingSpinner


