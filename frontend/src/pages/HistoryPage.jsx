/**
 * History Page - Prediction History & Statistics
 */
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  History as HistoryIcon, BarChart3, TrendingUp, 
  AlertTriangle, CheckCircle, Clock, RefreshCw 
} from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { getHistory, getStatistics } from '../services/api'
import { pageVariants, staggerContainer, fadeInUp } from '../utils/constants'
import { formatDate, formatConfidence, getToxicityBadgeClass } from '../utils/helpers'
import toast from 'react-hot-toast'

const HistoryPage = () => {
  const [loading, setLoading] = useState(true)
  const [statistics, setStatistics] = useState(null)
  const [history, setHistory] = useState([])
  const [limit, setLimit] = useState(10)
  const [skip, setSkip] = useState(0)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [stats, historyData] = await Promise.all([
        getStatistics(),
        getHistory(limit, skip)
      ])
      setStatistics(stats)
      setHistory(historyData.predictions || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
      toast.error('Không thể tải dữ liệu lịch sử')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [limit, skip])

  const loadMore = () => {
    setSkip(skip + limit)
  }

  if (loading && !statistics) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner message="Đang tải dữ liệu..." size="lg" />
      </div>
    )
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
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-orange-400 to-red-600 rounded-3xl flex items-center justify-center shadow-2xl">
            <HistoryIcon size={48} className="text-white" />
          </div>
        </motion.div>

        <h1 className="text-5xl font-bold gradient-text">
          Lịch Sử & Thống Kê
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Xem lại các lần nhận diện trước đây và thống kê tổng quan
        </p>

        <button
          onClick={fetchData}
          className="btn-secondary"
        >
          <RefreshCw size={20} />
          Làm mới
        </button>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <motion.div variants={fadeInUp} className="card p-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
                <BarChart3 size={28} className="text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Tổng predictions</p>
                <p className="text-3xl font-bold text-gray-800">
                  {statistics.total_predictions || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div variants={fadeInUp} className="card p-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-red-100 rounded-xl flex items-center justify-center">
                <AlertTriangle size={28} className="text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Nấm độc</p>
                <p className="text-3xl font-bold text-gray-800">
                  {statistics.poisonous_count || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div variants={fadeInUp} className="card p-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center">
                <CheckCircle size={28} className="text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Nấm ăn được</p>
                <p className="text-3xl font-bold text-gray-800">
                  {statistics.edible_count || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div variants={fadeInUp} className="card p-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center">
                <TrendingUp size={28} className="text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Tin cậy TB</p>
                <p className="text-3xl font-bold text-gray-800">
                  {statistics.avg_confidence ? statistics.avg_confidence.toFixed(1) : 0}%
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Top Genera Chart */}
      {statistics && statistics.top_genera && statistics.top_genera.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8"
        >
          <h3 className="text-2xl font-bold text-gray-800 mb-6">
            📊 Top Chi Nấm Được Nhận Diện
          </h3>
          <div className="space-y-4">
            {statistics.top_genera.map((item, index) => {
              const maxCount = statistics.top_genera[0]?.count || 1
              const percentage = (item.count / maxCount) * 100

              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-gray-800">
                      {index + 1}. {item.genus}
                    </span>
                    <span className="text-gray-600">
                      {item.count} lần ({((item.count / statistics.total_predictions) * 100).toFixed(1)}%)
                    </span>
                  </div>
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.8, delay: index * 0.1 }}
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-600"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* History List */}
      <div className="card p-8">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">
          📜 Lịch Sử Nhận Diện Gần Đây
        </h3>

        {history.length === 0 ? (
          <div className="text-center py-12">
            <HistoryIcon size={64} className="text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              Chưa có lịch sử nhận diện
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Thực hiện nhận diện để xem lịch sử tại đây
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-6 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-200 hover:border-green-300 hover:shadow-md transition-all"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Main Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-xl font-bold text-gray-800">
                        {item.prediction?.genus || item.ensemble_prediction?.genus || item.predicted_genus || 'N/A'}
                      </h4>
                      {(() => {
                        // Determine toxicity code
                        let toxicityCode = 'E'
                        let toxicityIcon = '✅'
                        let toxicityLabel = 'Ăn được'
                        
                        if (item.prediction?.is_poisonous) {
                          toxicityCode = 'P'
                          toxicityIcon = '☠️'
                          toxicityLabel = 'Độc'
                        } else if (item.prediction?.toxicity === 'Độc') {
                          toxicityCode = 'P'
                          toxicityIcon = '☠️'
                          toxicityLabel = 'Độc'
                        } else if (item.ensemble_prediction?.toxicity?.code) {
                          toxicityCode = item.ensemble_prediction.toxicity.code
                          toxicityIcon = item.ensemble_prediction.toxicity.icon || (toxicityCode === 'P' ? '☠️' : '✅')
                          toxicityLabel = item.ensemble_prediction.toxicity.label
                        } else if (item.toxicity_code) {
                          toxicityCode = item.toxicity_code
                          toxicityIcon = toxicityCode === 'P' ? '☠️' : '✅'
                          toxicityLabel = toxicityCode === 'P' ? 'Độc' : 'Ăn được'
                        }
                        
                        return (
                          <span className={`badge ${getToxicityBadgeClass(toxicityCode)}`}>
                            {toxicityIcon} {toxicityLabel}
                          </span>
                        )
                      })()}
                    </div>

                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <TrendingUp size={16} />
                        Tin cậy: {formatConfidence(
                          item.prediction?.confidence || 
                          item.ensemble_prediction?.confidence || 
                          item.confidence || 
                          0
                        )}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={16} />
                        {formatDate(item.timestamp)}
                      </span>
                      {(item.image_filename || item.filename) && (
                        <span className="text-gray-500">
                          📁 {item.image_filename || item.filename}
                        </span>
                      )}
                    </div>

                    {/* Individual Models */}
                    {item.individual_models && item.individual_models.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.individual_models.map((model, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-md"
                          >
                            {model.model}: {model.genus} ({model.confidence.toFixed(1)}%)
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Confidence Bar */}
                  <div className="w-full md:w-32">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-600"
                        style={{ width: `${item.prediction?.confidence || item.ensemble_prediction?.confidence || item.confidence || 0}%` }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Load More */}
        {history.length > 0 && history.length >= limit && (
          <div className="mt-6 text-center">
            <button
              onClick={loadMore}
              className="btn-secondary"
            >
              Xem thêm
            </button>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default HistoryPage

