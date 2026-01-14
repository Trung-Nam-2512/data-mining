/**
 * Prediction Result Card Component
 */
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Award, AlertTriangle, CheckCircle2, Brain,
    TrendingUp, Clock, Layers, Eye, Download
} from 'lucide-react'
import {
    formatConfidence,
    getToxicityBadgeClass,
    formatProcessingTime,
    downloadBase64Image
} from '../utils/helpers'
import { MODEL_DISPLAY_NAMES } from '../utils/constants'
import { generateGradCAMAll } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import toast from 'react-hot-toast'

const PredictionResult = ({ result, imageUrl, imageFile }) => {
    const {
        ensemble_prediction,
        individual_models = [],
        top_predictions = [],
        processing_time_ms
    } = result

    const isPoison = ensemble_prediction.toxicity.code === 'P'

    // Grad-CAM state
    const [showGradCAM, setShowGradCAM] = useState(false)
    const [gradcamLoading, setGradcamLoading] = useState(false)
    const [gradcamResults, setGradcamResults] = useState(null)

    // Handle Grad-CAM generation
    const handleGenerateGradCAM = async () => {
        if (!imageFile) {
            toast.error('Không thể tạo Grad-CAM: thiếu file ảnh')
            return
        }

        setGradcamLoading(true)
        try {
            const response = await generateGradCAMAll(imageFile, 0.45)
            console.log('Grad-CAM response:', response)
            // Backend returns { success: true, results: {...} }
            setGradcamResults(response.results || response)
            setShowGradCAM(true)
            toast.success('Đã tạo Grad-CAM thành công!')
        } catch (error) {
            console.error('Grad-CAM error:', error)
            toast.error('Có lỗi khi tạo Grad-CAM')
        } finally {
            setGradcamLoading(false)
        }
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
        >
            {/* Main Result Card */}
            <div className={`card p-8 ${isPoison ? 'border-red-300' : 'border-green-300'}`}>
                <div className="flex flex-col md:flex-row gap-8">
                    {/* Image Preview */}
                    {imageUrl && (
                        <div className="flex-shrink-0">
                            <div className="w-full md:w-64 aspect-square rounded-xl overflow-hidden border-4 border-gray-200 shadow-lg">
                                <img
                                    src={imageUrl}
                                    alt="Mushroom"
                                    className="w-full h-full object-cover"
                                />
                            </div>
                        </div>
                    )}

                    {/* Prediction Info */}
                    <div className="flex-1 space-y-6">
                        {/* Header */}
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="flex items-center gap-3 mb-2">
                                    <Award size={32} className="text-green-600" />
                                    <h3 className="text-3xl font-bold gradient-text">
                                        Kết quả Ensemble
                                    </h3>
                                </div>
                                <p className="text-gray-600">
                                    Kết quả tổng hợp từ {individual_models.length} mô hình AI
                                </p>
                            </div>

                            {processing_time_ms && (
                                <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
                                    <Clock size={18} className="text-blue-600" />
                                    <span className="text-sm font-semibold text-gray-700">
                                        {formatProcessingTime(processing_time_ms)}
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Main Prediction */}
                        <div className={`p-6 rounded-2xl ${isPoison ? 'bg-red-50 border-2 border-red-300' : 'bg-green-50 border-2 border-green-300'}`}>
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    {isPoison ? (
                                        <AlertTriangle size={32} className="text-red-600" />
                                    ) : (
                                        <CheckCircle2 size={32} className="text-green-600" />
                                    )}
                                    <div>
                                        <h4 className="text-2xl font-bold text-gray-800">
                                            {ensemble_prediction.genus}
                                        </h4>
                                        <p className="text-sm text-gray-600">Chi nấm được nhận diện</p>
                                    </div>
                                </div>

                                <span className={`badge ${getToxicityBadgeClass(ensemble_prediction.toxicity.code)} text-lg px-4 py-2`}>
                                    {ensemble_prediction.toxicity.icon} {ensemble_prediction.toxicity.label}
                                </span>
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="flex-1">
                                    <div className="flex justify-between mb-2">
                                        <span className="text-sm font-medium text-gray-700">Độ tin cậy</span>
                                        <span className="text-sm font-bold text-gray-800">
                                            {formatConfidence(ensemble_prediction.confidence)}
                                        </span>
                                    </div>
                                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${ensemble_prediction.confidence}%` }}
                                            transition={{ duration: 1, ease: 'easeOut' }}
                                            className={`h-full ${isPoison ? 'bg-gradient-to-r from-red-500 to-rose-600' : 'bg-gradient-to-r from-green-500 to-emerald-600'}`}
                                        />
                                    </div>
                                </div>
                            </div>

                            {isPoison && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="mt-4 p-4 bg-red-100 border-l-4 border-red-500 rounded-lg"
                                >
                                    <p className="text-sm font-semibold text-red-800 flex items-center gap-2">
                                        <AlertTriangle size={16} />
                                        ⚠️ CẢNH BÁO: Nấm này có độc tính! Không nên sử dụng làm thực phẩm.
                                    </p>
                                </motion.div>
                            )}

                            {/* Validation Warning - Low Confidence / Not a Mushroom */}
                            {result.validation?.warning_message && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`mt-4 p-4 rounded-lg border-l-4 ${result.validation.is_likely_mushroom === false
                                        ? 'bg-orange-100 border-orange-500'
                                        : 'bg-yellow-100 border-yellow-500'
                                        }`}
                                >
                                    <p className={`text-sm font-semibold flex items-start gap-2 ${result.validation.is_likely_mushroom === false
                                        ? 'text-orange-800'
                                        : 'text-yellow-800'
                                        }`}>
                                        <AlertTriangle size={18} className="mt-0.5 flex-shrink-0" />
                                        <span>{result.validation.warning_message}</span>
                                    </p>
                                    {result.validation.is_likely_mushroom === false && (
                                        <div className="mt-3 text-xs text-orange-700 space-y-1">
                                            <p className="font-medium">💡 Gợi ý:</p>
                                            <ul className="list-disc list-inside space-y-1 ml-2">
                                                <li>Đảm bảo ảnh chụp đúng đối tượng là nấm</li>
                                                <li>Ảnh phải rõ nét, đủ sáng, không bị mờ</li>
                                                <li>Chụp từ nhiều góc độ khác nhau</li>
                                                <li>Tránh ảnh có nhiều vật thể khác trong khung hình</li>
                                            </ul>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </div>

                        {/* Top Predictions */}
                        {top_predictions.length > 1 && (
                            <div>
                                <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                                    <TrendingUp size={18} />
                                    Các dự đoán khác
                                </h5>
                                <div className="space-y-2">
                                    {top_predictions.slice(1).map((pred, index) => (
                                        <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                            <span className="text-sm font-medium text-gray-500 w-6">
                                                #{pred.rank}
                                            </span>
                                            <span className="flex-1 font-semibold text-gray-800">
                                                {pred.genus}
                                            </span>
                                            <span className="text-sm text-gray-600">
                                                {formatConfidence(pred.confidence)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Individual Model Predictions */}
            {individual_models.length > 0 && (
                <div className="card p-6">
                    <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Layers size={24} className="text-blue-600" />
                        Dự đoán từng mô hình
                    </h4>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {individual_models.map((model, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 }}
                                className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
                            >
                                <div className="flex items-center gap-2 mb-3">
                                    <Brain size={20} className="text-blue-600" />
                                    <span className="font-bold text-gray-800 text-sm">
                                        {MODEL_DISPLAY_NAMES[model.model] || model.model}
                                    </span>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Dự đoán:</span>
                                        <span className="font-semibold text-gray-800">{model.genus}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Tin cậy:</span>
                                        <span className="font-semibold text-gray-800">
                                            {formatConfidence(model.confidence)}
                                        </span>
                                    </div>

                                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden mt-2">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${model.confidence}%` }}
                                            transition={{ duration: 0.8, delay: index * 0.1 }}
                                            className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                                        />
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Grad-CAM Section */}
            {imageFile && (
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Eye size={24} className="text-purple-600" />
                            <h4 className="text-xl font-bold text-gray-800">Grad-CAM Visualization</h4>
                        </div>
                        {!showGradCAM && (
                            <button
                                onClick={handleGenerateGradCAM}
                                disabled={gradcamLoading}
                                className="btn-primary"
                            >
                                {gradcamLoading ? (
                                    <><LoadingSpinner size="sm" /> Đang tạo...</>
                                ) : (
                                    <><Eye size={20} /> Tạo Grad-CAM</>
                                )}
                            </button>
                        )}
                    </div>

                    <p className="text-sm text-gray-600 mb-4">
                        Xem vùng mà AI chú ý khi phân loại nấm này
                    </p>

                    <AnimatePresence>
                        {showGradCAM && gradcamResults && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4"
                            >
                                {Object.entries(gradcamResults).map(([modelName, data], index) => {
                                    // Skip if no gradcam data or failed
                                    if (!data || !data.success || !data.gradcam_base64) {
                                        console.warn(`Skipping ${modelName}: No Grad-CAM data`)
                                        return null
                                    }

                                    return (
                                        <motion.div
                                            key={modelName}
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border-2 border-purple-200"
                                        >
                                            <div className="flex items-center justify-between mb-3">
                                                <h5 className="font-bold text-gray-800">
                                                    {MODEL_DISPLAY_NAMES[modelName] || modelName}
                                                </h5>
                                                <button
                                                    onClick={() => downloadBase64Image(data.gradcam_base64, `gradcam_${modelName}.png`)}
                                                    className="btn-icon text-purple-600 hover:text-purple-800"
                                                    title="Tải xuống"
                                                >
                                                    <Download size={18} />
                                                </button>
                                            </div>

                                            <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 mb-3">
                                                <img
                                                    src={`data:image/png;base64,${data.gradcam_base64}`}
                                                    alt={`Grad-CAM ${modelName}`}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>

                                            <div className="text-xs space-y-1">
                                                <div className="flex justify-between">
                                                    <span className="text-gray-600">Dự đoán:</span>
                                                    <span className="font-semibold text-gray-800">{data.predicted_class || 'N/A'}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-gray-600">Tin cậy:</span>
                                                    <span className="font-semibold text-gray-800">
                                                        {data.confidence != null ? data.confidence.toFixed(1) : '0.0'}%
                                                    </span>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )
                                })}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            )}
        </motion.div>
    )
}

export default PredictionResult

