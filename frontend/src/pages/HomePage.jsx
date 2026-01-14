/**
 * Home Page - Single Image Prediction
 */
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Play } from 'lucide-react'
import ImageUploader from '../components/ImageUploader'
import PredictionResult from '../components/PredictionResult'
import LoadingSpinner from '../components/LoadingSpinner'
import { predictMushroom } from '../services/api'
import { pageVariants } from '../utils/constants'
import { revokePreviewURL } from '../utils/helpers'
import toast from 'react-hot-toast'

const HomePage = () => {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  // Cleanup preview URLs on unmount
  useEffect(() => {
    return () => {
      previews.forEach(preview => {
        if (preview?.url && preview.url.startsWith('blob:')) {
          revokePreviewURL(preview.url)
        }
      })
    }
  }, []) // Only run on unmount

  const handleFileSelect = (files, newPreviews) => {
    setSelectedFiles(files)
    setPreviews(newPreviews)
    setResult(null)
  }

  const handlePredict = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Vui lòng chọn ảnh trước')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const prediction = await predictMushroom(selectedFiles[0], 3)
      setResult(prediction)
      toast.success('Nhận diện thành công!')
    } catch (error) {
      console.error('Prediction error:', error)
      const errorMsg = error.response?.data?.detail || 'Có lỗi xảy ra khi nhận diện'
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="space-y-8"
    >
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="inline-block"
        >
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-green-400 to-emerald-600 rounded-3xl flex items-center justify-center shadow-2xl">
            <Sparkles size={48} className="text-white" />
          </div>
        </motion.div>

        <h1 className="text-5xl font-bold gradient-text">
          Nhận Diện Nấm Đơn
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload ảnh nấm để AI phân tích và nhận diện chi nấm cùng độ độc tính
        </p>

        <div className="flex flex-wrap gap-3 justify-center">
          <span className="badge badge-info">
            🎯 3 Models Ensemble
          </span>
          <span className="badge badge-info">
            🍄 11 Chi nấm
          </span>
          <span className="badge badge-info">
            ⚡ Real-time
          </span>
        </div>
      </div>

      {/* Upload Section */}
      <div className="max-w-4xl mx-auto">
        <div className="card p-8">
          <ImageUploader
            onFileSelect={handleFileSelect}
            maxFiles={1}
            selectedFiles={selectedFiles}
          />

          {selectedFiles.length > 0 && !loading && !result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 text-center"
            >
              <button
                onClick={handlePredict}
                disabled={loading}
                className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play size={24} />
                Bắt đầu nhận diện
              </button>
            </motion.div>
          )}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="max-w-4xl mx-auto">
          <div className="card p-12">
            <LoadingSpinner message="Đang phân tích ảnh với Ensemble AI..." size="lg" />
            <p className="text-center text-gray-500 mt-4">
              Quá trình này có thể mất 5-10 giây
            </p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && previews.length > 0 && (
        <div className="max-w-6xl mx-auto">
          <PredictionResult
            result={result}
            imageUrl={previews[0].url}
            imageFile={selectedFiles[0]}
          />

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 text-center"
          >
            <button
              onClick={() => {
                // Cleanup preview URLs before resetting
                previews.forEach(preview => {
                  if (preview?.url && preview.url.startsWith('blob:')) {
                    revokePreviewURL(preview.url)
                  }
                })
                setSelectedFiles([])
                setPreviews([])
                setResult(null)
              }}
              className="btn-secondary"
            >
              Nhận diện ảnh khác
            </button>
          </motion.div>
        </div>
      )}

      {/* Info Cards */}
      {!loading && !result && (
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card-hover p-6 text-center"
          >
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-bold text-lg mb-2">Chính xác cao</h3>
            <p className="text-sm text-gray-600">
              Sử dụng 3 mô hình Deep Learning với độ chính xác trên 91%
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card-hover p-6 text-center"
          >
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-bold text-lg mb-2">Nhanh chóng</h3>
            <p className="text-sm text-gray-600">
              Kết quả trả về trong vài giây với Soft Voting Ensemble
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card-hover p-6 text-center"
          >
            <div className="text-4xl mb-3">🛡️</div>
            <h3 className="font-bold text-lg mb-2">An toàn</h3>
            <p className="text-sm text-gray-600">
              Cảnh báo độc tính tự động giúp bảo vệ sức khỏe người dùng
            </p>
          </motion.div>
        </div>
      )}
    </motion.div>
  )
}

export default HomePage
