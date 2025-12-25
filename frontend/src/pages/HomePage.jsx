/**
 * Home Page - Main prediction page
 */
import { useState } from 'react'
import { Loader, AlertTriangle } from 'lucide-react'
import ImageUpload from '../components/ImageUpload'
import PredictionResults from '../components/PredictionResults'
import { predictMushroom } from '../services/api'
import './HomePage.css'

const HomePage = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState(null)

  const handleFileSelect = (file, previewUrl) => {
    setSelectedFile(file)
    setPreview(previewUrl)
    setPrediction(null)
    setError(null)
  }

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('Vui lòng chọn ảnh trước')
      return
    }

    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const result = await predictMushroom(selectedFile, 3)
      setPrediction(result)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Có lỗi xảy ra khi nhận diện. Vui lòng thử lại.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="home-page">
      <div className="prediction-area">
        <ImageUpload
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
          preview={preview}
        />

        {selectedFile && (
          <button
            className="btn-predict"
            onClick={handlePredict}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader className="spinner" />
                Đang xử lý...
              </>
            ) : (
              '🔍 Nhận diện'
            )}
          </button>
        )}

        {error && (
          <div className="alert alert-error">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}

        {prediction && <PredictionResults prediction={prediction} />}
      </div>
    </div>
  )
}

export default HomePage



