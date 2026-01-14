/**
 * Grad-CAM Page - Model Visualization
 */
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Download, Layers, Sparkles } from 'lucide-react'
import ImageUploader from '../components/ImageUploader'
import LoadingSpinner from '../components/LoadingSpinner'
import { generateGradCAMAll } from '../services/api'
import { pageVariants, MODEL_DISPLAY_NAMES } from '../utils/constants'
import { downloadBase64Image } from '../utils/helpers'
import toast from 'react-hot-toast'

const GradCAMPage = () => {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [gradcamResults, setGradcamResults] = useState(null)
  const [alpha, setAlpha] = useState(0.45)

  const handleFileSelect = (files, newPreviews) => {
    setSelectedFiles(files)
    setPreviews(newPreviews)
    setGradcamResults(null)
  }

  const handleGenerateGradCAM = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Vui lòng chọn ảnh trước')
      return
    }

    setLoading(true)
    setGradcamResults(null)

    try {
      const response = await generateGradCAMAll(selectedFiles[0], alpha)
      console.log('Grad-CAM response:', response)
      // Backend returns { success: true, results: {...} }
      setGradcamResults(response.results || response)
      toast.success('Đã tạo Grad-CAM cho tất cả models!')
    } catch (error) {
      console.error('Grad-CAM error:', error)
      const errorMsg = error.response?.data?.detail || 'Có lỗi xảy ra khi tạo Grad-CAM'
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = (modelName, base64Image) => {
    const filename = `gradcam_${modelName}_${Date.now()}.png`
    downloadBase64Image(base64Image, filename)
    toast.success(`Đã tải xuống ${filename}`)
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
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-400 to-pink-600 rounded-3xl flex items-center justify-center shadow-2xl">
            <Eye size={48} className="text-white" />
          </div>
        </motion.div>

        <h1 className="text-5xl font-bold gradient-text">
          Grad-CAM Visualization
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Trực quan hóa các vùng quan trọng mà model AI tập trung khi đưa ra quyết định
        </p>

        <div className="flex flex-wrap gap-3 justify-center">
          <span className="badge badge-info">
            🔍 Explainable AI
          </span>
          <span className="badge badge-info">
            🎨 Heatmap Overlay
          </span>
          <span className="badge badge-info">
            📊 3 Models
          </span>
        </div>
      </div>

      {/* Upload Section */}
      <div className="max-w-4xl mx-auto">
        <div className="card p-8">
          <div className="mb-6 p-4 bg-purple-50 border-l-4 border-purple-500 rounded-lg">
            <div className="flex items-start gap-3">
              <Sparkles size={20} className="text-purple-600 mt-0.5" />
              <div>
                <p className="font-semibold text-purple-800 mb-1">
                  Grad-CAM là gì?
                </p>
                <p className="text-sm text-purple-700">
                  Grad-CAM (Gradient-weighted Class Activation Mapping) là kỹ thuật trực quan hóa 
                  giúp hiểu model AI "nhìn" vào đâu khi phân loại. Vùng màu đỏ là nơi model chú ý nhiều nhất.
                </p>
              </div>
            </div>
          </div>

          <ImageUploader
            onFileSelect={handleFileSelect}
            maxFiles={1}
            selectedFiles={selectedFiles}
          />

          {/* Alpha Slider */}
          {selectedFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-6 bg-gray-50 rounded-xl"
            >
              <label className="block mb-3">
                <span className="font-semibold text-gray-700">
                  Độ trong suốt overlay (Alpha): {alpha.toFixed(2)}
                </span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={alpha}
                  onChange={(e) => setAlpha(parseFloat(e.target.value))}
                  className="w-full mt-2 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Trong suốt</span>
                  <span>Đậm</span>
                </div>
              </label>

              <button
                onClick={handleGenerateGradCAM}
                disabled={loading}
                className="btn-primary w-full text-lg py-4 mt-4"
              >
                <Eye size={24} />
                Tạo Grad-CAM
              </button>
            </motion.div>
          )}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="max-w-4xl mx-auto">
          <div className="card p-12">
            <LoadingSpinner message="Đang tạo Grad-CAM cho 3 models..." size="lg" />
            <p className="text-center text-gray-500 mt-4">
              Quá trình này có thể mất 10-20 giây
            </p>
          </div>
        </div>
      )}

      {/* Results */}
      {gradcamResults && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto space-y-8"
        >
          <div className="text-center">
            <h2 className="text-3xl font-bold gradient-text mb-2">
              Kết Quả Grad-CAM
            </h2>
            <p className="text-gray-600">
              Trực quan hóa từ 3 models khác nhau
            </p>
          </div>

          {/* Original Image */}
          {previews.length > 0 && (
            <div className="card p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                Ảnh gốc
              </h3>
              <div className="flex justify-center">
                <div className="w-full max-w-md aspect-square rounded-xl overflow-hidden border-4 border-gray-200 shadow-lg">
                  <img
                    src={previews[0].url}
                    alt="Original"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Grad-CAM Results */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {Object.entries(gradcamResults).map(([modelName, data], index) => {
              // Skip if no valid data
              if (!data || !data.success || !data.gradcam_base64) {
                console.warn(`Skipping ${modelName}: No valid Grad-CAM data`)
                return null
              }
              
              return (
              <motion.div
                key={modelName}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="card p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Layers size={20} className="text-purple-600" />
                    <h3 className="font-bold text-lg text-gray-800">
                      {MODEL_DISPLAY_NAMES[modelName] || modelName}
                    </h3>
                  </div>

                  <button
                    onClick={() => handleDownload(modelName, data.gradcam_base64)}
                    className="btn-icon text-gray-600 hover:text-purple-600"
                    title="Tải xuống"
                  >
                    <Download size={20} />
                  </button>
                </div>

                {/* Grad-CAM Image */}
                <div className="aspect-square rounded-xl overflow-hidden border-2 border-gray-200 shadow-lg mb-4">
                  <img
                    src={`data:image/png;base64,${data.gradcam_base64}`}
                    alt={`Grad-CAM ${modelName}`}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Prediction Info */}
                <div className="space-y-2 bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Dự đoán:</span>
                    <span className="font-bold text-gray-800">{data.predicted_class || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Độ tin cậy:</span>
                    <span className="font-bold text-gray-800">
                      {data.confidence != null ? data.confidence.toFixed(2) : '0.0'}%
                    </span>
                  </div>

                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${data.confidence || 0}%` }}
                      transition={{ duration: 0.8, delay: index * 0.1 }}
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-600"
                    />
                  </div>
                </div>
              </motion.div>
              )
            })}
          </div>

          {/* Info Card */}
          <div className="card p-8 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
              🎨 Cách đọc Grad-CAM
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🔴</span>
                <div>
                  <p className="font-semibold text-gray-800">Vùng đỏ - Quan trọng nhất</p>
                  <p className="text-gray-600">Model chú ý mạnh vào vùng này khi phân loại</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🟡</span>
                <div>
                  <p className="font-semibold text-gray-800">Vùng vàng - Trung bình</p>
                  <p className="text-gray-600">Model cũng xem xét vùng này nhưng ít hơn</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🔵</span>
                <div>
                  <p className="font-semibold text-gray-800">Vùng xanh - Ít quan trọng</p>
                  <p className="text-gray-600">Vùng này ít ảnh hưởng đến quyết định</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-2xl">✨</span>
                <div>
                  <p className="font-semibold text-gray-800">So sánh models</p>
                  <p className="text-gray-600">Các model có thể chú ý vào các vùng khác nhau</p>
                </div>
              </div>
            </div>
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
                setGradcamResults(null)
              }}
              className="btn-secondary"
            >
              Tạo Grad-CAM cho ảnh khác
            </button>
          </motion.div>
        </motion.div>
      )}

      {/* Info */}
      {!loading && !gradcamResults && (
        <div className="max-w-4xl mx-auto">
          <div className="card p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">
              🤔 Tại sao cần Grad-CAM?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4">
                <div className="text-4xl mb-3">🔍</div>
                <h4 className="font-bold mb-2">Minh bạch</h4>
                <p className="text-sm text-gray-600">
                  Hiểu rõ AI đang "nhìn" vào đâu để đưa ra quyết định
                </p>
              </div>
              <div className="text-center p-4">
                <div className="text-4xl mb-3">🎯</div>
                <h4 className="font-bold mb-2">Tin cậy</h4>
                <p className="text-sm text-gray-600">
                  Xác minh model chú ý đúng vào đặc điểm quan trọng
                </p>
              </div>
              <div className="text-center p-4">
                <div className="text-4xl mb-3">🔬</div>
                <h4 className="font-bold mb-2">Debug</h4>
                <p className="text-sm text-gray-600">
                  Phát hiện lỗi khi model chú ý sai vùng
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default GradCAMPage

