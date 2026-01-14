/**
 * Camera Capture Component
 * Allows users to capture photos directly from their device camera
 */
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, X, RotateCcw, Check, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const CameraCapture = ({ onCapture, onClose }) => {
  const [stream, setStream] = useState(null)
  const [facingMode, setFacingMode] = useState('environment') // 'environment' = back, 'user' = front
  const [error, setError] = useState(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [capturedImage, setCapturedImage] = useState(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)

  // Start camera stream
  useEffect(() => {
    let isMounted = true
    
    startCamera().catch(() => {
      // Error already handled in startCamera
    })
    
    return () => {
      isMounted = false
      stopCamera()
      // Also cleanup captured image URL if exists
      if (capturedImage?.previewUrl) {
        URL.revokeObjectURL(capturedImage.previewUrl)
      }
    }
  }, [facingMode])

  const startCamera = async () => {
    try {
      setError(null)
      setIsLoading(true)
      
      // Stop existing stream if any
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }

      // Request camera access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      })

      setStream(mediaStream)
      
      // Attach stream to video element
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
        
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().then(() => {
            setIsLoading(false)
          }).catch(() => {
            setIsLoading(false)
          })
        }
      }
    } catch (err) {
      console.error('Camera error:', err)
      let errorMessage = 'Không thể truy cập camera'
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMessage = 'Vui lòng cho phép truy cập camera trong cài đặt trình duyệt'
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMessage = 'Không tìm thấy camera trên thiết bị này'
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMessage = 'Camera đang được sử dụng bởi ứng dụng khác'
      } else if (err.name === 'OverconstrainedError') {
        errorMessage = 'Camera không hỗ trợ yêu cầu này'
      }
      
      setError(errorMessage)
      setIsLoading(false)
      toast.error(errorMessage)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const switchCamera = () => {
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment')
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    setIsCapturing(true)

    try {
      const video = videoRef.current
      const canvas = canvasRef.current
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw video frame to canvas
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // Convert to blob
      canvas.toBlob((blob) => {
        if (blob) {
          // Create File object from blob
          const file = new File([blob], `camera_${Date.now()}.jpg`, {
            type: 'image/jpeg',
            lastModified: Date.now()
          })
          
          // Create preview URL
          const previewUrl = URL.createObjectURL(blob)
          
          setCapturedImage({ file, previewUrl })
          setIsCapturing(false)
          
          toast.success('Đã chụp ảnh thành công!')
        }
      }, 'image/jpeg', 0.95) // 95% quality
    } catch (err) {
      console.error('Capture error:', err)
      toast.error('Có lỗi khi chụp ảnh')
      setIsCapturing(false)
    }
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    if (videoRef.current && stream) {
      videoRef.current.play()
    }
  }

  const confirmPhoto = () => {
    if (capturedImage) {
      onCapture(capturedImage.file, capturedImage.previewUrl)
      stopCamera()
      onClose()
    }
  }

  const handleClose = () => {
    stopCamera()
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage.previewUrl)
    }
    onClose()
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black flex items-center justify-center"
      >
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 z-10 w-12 h-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
        >
          <X size={24} className="text-white" />
        </button>

        {/* Camera View */}
        {!capturedImage ? (
          <div className="relative w-full h-full flex flex-col">
            {/* Video Preview */}
            <div className="flex-1 relative overflow-hidden">
              {error ? (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                  <div className="text-center p-6 max-w-md">
                    <AlertCircle size={64} className="text-red-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Lỗi Camera</h3>
                    <p className="text-gray-300 mb-4">{error}</p>
                    <button
                      onClick={startCamera}
                      className="btn-primary"
                    >
                      Thử lại
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
                      <div className="text-center">
                        <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                        <p className="text-white text-lg">Đang khởi động camera...</p>
                      </div>
                    </div>
                  )}
                  
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                    onClick={(e) => e.stopPropagation()}
                  />
                  
                  {/* Instructions Overlay */}
                  {!isLoading && stream && (
                    <div className="absolute top-20 left-0 right-0 px-4">
                      <div className="max-w-md mx-auto bg-black/60 backdrop-blur-md rounded-lg p-3 text-center">
                        <p className="text-white text-sm">
                          📸 Đưa nấm vào khung hình và nhấn nút chụp
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Camera Controls Overlay */}
                  <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent">
                    <div className="flex items-center justify-center gap-4">
                      {/* Switch Camera Button */}
                      <button
                        onClick={switchCamera}
                        disabled={isLoading}
                        className="w-14 h-14 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center hover:bg-white/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title={facingMode === 'environment' ? 'Chuyển sang camera trước' : 'Chuyển sang camera sau'}
                      >
                        <RotateCcw size={24} className="text-white" />
                      </button>

                      {/* Capture Button */}
                      <button
                        onClick={capturePhoto}
                        disabled={isCapturing || !stream || isLoading}
                        className="w-20 h-20 bg-white rounded-full flex items-center justify-center border-4 border-gray-300 hover:scale-110 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                      >
                        {isCapturing ? (
                          <div className="w-12 h-12 border-4 border-gray-400 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Camera size={32} className="text-gray-800" />
                        )}
                      </button>

                      {/* Placeholder for symmetry */}
                      <div className="w-14 h-14" />
                    </div>
                    
                    {/* Tips */}
                    {!isLoading && stream && (
                      <div className="mt-4 text-center">
                        <p className="text-white/80 text-xs">
                          💡 Đảm bảo ảnh rõ nét, đủ sáng và nấm ở giữa khung hình
                        </p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        ) : (
          /* Captured Image Preview */
          <div className="relative w-full h-full flex flex-col items-center justify-center bg-gray-900 p-4">
            <div className="max-w-2xl w-full">
              <img
                src={capturedImage.previewUrl}
                alt="Captured"
                className="w-full rounded-xl shadow-2xl mb-6"
              />
              
              <div className="flex gap-4 justify-center">
                <button
                  onClick={retakePhoto}
                  className="btn-secondary text-white border-white/30 hover:bg-white/10"
                >
                  <RotateCcw size={20} />
                  Chụp lại
                </button>
                
                <button
                  onClick={confirmPhoto}
                  className="btn-primary"
                >
                  <Check size={20} />
                  Sử dụng ảnh này
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Hidden Canvas for Capture */}
        <canvas ref={canvasRef} className="hidden" />
      </motion.div>
    </AnimatePresence>
  )
}

export default CameraCapture

