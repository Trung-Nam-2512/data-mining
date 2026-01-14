/**
 * Batch Page - Multiple Images Prediction
 */
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Grid as ImagesIcon, Play, AlertCircle } from 'lucide-react'
import ImageUploader from '../components/ImageUploader'
import PredictionResult from '../components/PredictionResult'
import LoadingSpinner from '../components/LoadingSpinner'
import { predictBatch } from '../services/api'
import { pageVariants, staggerContainer, fadeInUp } from '../utils/constants'
import { revokePreviewURL } from '../utils/helpers'
import toast from 'react-hot-toast'

const BatchPage = () => {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])

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
    setResults([])
  }

  const handleBatchPredict = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Vui lòng chọn ít nhất 1 ảnh')
      return
    }

    if (selectedFiles.length > 5) {
      toast.error('Tối đa 5 ảnh mỗi lần')
      return
    }

    setLoading(true)
    setResults([])

    try {
      const batchResult = await predictBatch(selectedFiles, 3)
      setResults(batchResult.results || [])
      toast.success(`Đã nhận diện ${batchResult.successful}/${batchResult.total_images} ảnh thành công!`)
    } catch (error) {
      console.error('Batch prediction error:', error)
      const errorMsg = error.response?.data?.detail || 'Có lỗi xảy ra khi nhận diện batch'
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
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-400 to-indigo-600 rounded-3xl flex items-center justify-center shadow-2xl">
            <ImagesIcon size={48} className="text-white" />
          </div>
        </motion.div>

        <h1 className="text-5xl font-bold gradient-text">
          Nhận Diện Nhiều Ảnh
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload nhiều ảnh nấm cùng lúc (tối đa 5) để nhận diện hàng loạt
        </p>

        <div className="flex flex-wrap gap-3 justify-center">
          <span className="badge badge-info">
            📦 Batch Processing
          </span>
          <span className="badge badge-info">
            🚀 Max 5 ảnh
          </span>
          <span className="badge badge-info">
            ⚡ Ensemble AI
          </span>
        </div>
      </div>

      {/* Upload Section */}
      <div className="max-w-6xl mx-auto">
        <div className="card p-8">
          <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-blue-600 mt-0.5" />
              <div>
                <p className="font-semibold text-blue-800 mb-1">
                  Lưu ý về Batch Prediction
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Upload tối đa 5 ảnh mỗi lần</li>
                  <li>• Mỗi ảnh sẽ được xử lý độc lập bởi Ensemble</li>
                  <li>• Thời gian xử lý: ~5-10 giây/ảnh</li>
                  <li>• Kết quả được lưu vào lịch sử tự động</li>
                </ul>
              </div>
            </div>
          </div>

          <ImageUploader
            onFileSelect={handleFileSelect}
            maxFiles={5}
            selectedFiles={selectedFiles}
          />

          {selectedFiles.length > 0 && !loading && results.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
                <div>
                  <p className="font-semibold text-gray-800 mb-1">
                    Đã chọn {selectedFiles.length} ảnh
                  </p>
                  <p className="text-sm text-gray-600">
                    Ước tính thời gian: ~{selectedFiles.length * 5}-{selectedFiles.length * 10} giây
                  </p>
                </div>

                <button
                  onClick={handleBatchPredict}
                  disabled={loading}
                  className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play size={24} />
                  Nhận diện {selectedFiles.length} ảnh
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="max-w-6xl mx-auto">
          <div className="card p-12">
            <LoadingSpinner 
              message={`Đang xử lý ${selectedFiles.length} ảnh với Ensemble AI...`} 
              size="lg" 
            />
            <div className="mt-6 max-w-md mx-auto">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '100%' }}
                  transition={{ duration: selectedFiles.length * 7, ease: 'linear' }}
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                />
              </div>
              <p className="text-center text-gray-500 mt-4 text-sm">
                Quá trình này có thể mất vài phút. Vui lòng đợi...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="max-w-7xl mx-auto space-y-8"
        >
          <div className="text-center">
            <h2 className="text-3xl font-bold gradient-text mb-2">
              Kết Quả Nhận Diện
            </h2>
            <p className="text-gray-600">
              Đã xử lý thành công {results.length} ảnh
            </p>
          </div>

          <div className="space-y-8">
            {results.map((result, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
              >
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-gray-800">
                    Ảnh #{index + 1}: {result.filename || previews[index]?.file?.name}
                  </h3>
                </div>
                <PredictionResult
                  result={result}
                  imageUrl={previews[index]?.url}
                  imageFile={selectedFiles[index]}
                />
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <button
              onClick={() => {
                setSelectedFiles([])
                setPreviews([])
                setResults([])
              }}
              className="btn-secondary"
            >
              Nhận diện batch khác
            </button>
          </motion.div>
        </motion.div>
      )}

      {/* Info */}
      {!loading && results.length === 0 && (
        <div className="max-w-4xl mx-auto">
          <div className="card p-8 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
              💡 Mẹo sử dụng Batch Prediction
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-start gap-3">
                <span className="text-2xl">📸</span>
                <div>
                  <p className="font-semibold text-gray-800">Chất lượng ảnh</p>
                  <p className="text-gray-600">Sử dụng ảnh rõ nét, đủ sáng</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🎯</span>
                <div>
                  <p className="font-semibold text-gray-800">Góc chụp</p>
                  <p className="text-gray-600">Chụp từ nhiều góc độ khác nhau</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚖️</span>
                <div>
                  <p className="font-semibold text-gray-800">Kích thước file</p>
                  <p className="text-gray-600">Mỗi ảnh không quá 10MB</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🔄</span>
                <div>
                  <p className="font-semibold text-gray-800">Xử lý song song</p>
                  <p className="text-gray-600">Các ảnh được xử lý tuần tự</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default BatchPage

