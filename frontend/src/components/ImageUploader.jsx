/**
 * Image Uploader Component with Drag & Drop and Camera Capture
 */
import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, X, Image as ImageIcon, Camera } from 'lucide-react'
import { validateImage, createPreviewURL, formatFileSize, revokePreviewURL } from '../utils/helpers'
import CameraCapture from './CameraCapture'
import toast from 'react-hot-toast'

const ImageUploader = ({ onFileSelect, maxFiles = 1, selectedFiles = [] }) => {
    const [dragActive, setDragActive] = useState(false)
    const [previews, setPreviews] = useState([])
    const [showCamera, setShowCamera] = useState(false)
    const fileInputRef = useRef(null)

    // Cleanup preview URLs on unmount
    useEffect(() => {
        return () => {
            // Cleanup all preview URLs when component unmounts
            // Use a ref or current state to avoid stale closure
            setPreviews(currentPreviews => {
                currentPreviews.forEach(preview => {
                    if (preview?.url && preview.url.startsWith('blob:')) {
                        revokePreviewURL(preview.url)
                    }
                })
                return currentPreviews // Don't change state, just cleanup
            })
        }
    }, []) // Only run on unmount

    // Check if camera is available
    const isCameraAvailable = typeof navigator !== 'undefined' &&
        navigator.mediaDevices &&
        navigator.mediaDevices.getUserMedia

    const handleFiles = (files) => {
        const fileArray = Array.from(files)

        // Validate max files
        if (fileArray.length + selectedFiles.length > maxFiles) {
            toast.error(`Chỉ được chọn tối đa ${maxFiles} ảnh`)
            return
        }

        // Validate each file
        const validFiles = []
        const newPreviews = []

        for (const file of fileArray) {
            const validation = validateImage(file)
            if (!validation.valid) {
                toast.error(validation.error)
                continue
            }

            validFiles.push(file)
            newPreviews.push({
                file,
                url: createPreviewURL(file),
            })
        }

        if (validFiles.length > 0) {
            setPreviews([...previews, ...newPreviews])
            onFileSelect([...selectedFiles, ...validFiles], [...previews, ...newPreviews])
        }
    }

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files)
        }
    }

    const handleChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files)
        }
    }

    const handleRemove = (index) => {
        // Revoke URL before removing
        if (previews[index]?.url && previews[index].url.startsWith('blob:')) {
            revokePreviewURL(previews[index].url)
        }

        const newPreviews = previews.filter((_, i) => i !== index)
        const newFiles = selectedFiles.filter((_, i) => i !== index)
        setPreviews(newPreviews)
        onFileSelect(newFiles, newPreviews)
    }

    const handleClick = () => {
        fileInputRef.current?.click()
    }

    const handleCameraCapture = (file, previewUrl) => {
        // Validate file
        const validation = validateImage(file)
        if (!validation.valid) {
            toast.error(validation.error)
            return
        }

        // Check max files
        if (selectedFiles.length + 1 > maxFiles) {
            toast.error(`Chỉ được chọn tối đa ${maxFiles} ảnh`)
            return
        }

        // Add to selected files and previews
        const newPreviews = [...previews, { file, url: previewUrl }]
        const newFiles = [...selectedFiles, file]

        setPreviews(newPreviews)
        onFileSelect(newFiles, newPreviews)
    }

    return (
        <div className="space-y-4">
            {/* Upload Area */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`upload-area ${dragActive ? 'dragover' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple={maxFiles > 1}
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    onChange={handleChange}
                    className="hidden"
                />

                <div className="flex flex-col items-center gap-4">
                    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                        <Upload size={40} className="text-green-600" />
                    </div>

                    <div className="text-center">
                        <p className="text-lg font-semibold text-gray-700 mb-2">
                            Kéo thả ảnh vào đây hoặc chọn từ thiết bị
                        </p>
                        <p className="text-sm text-gray-500">
                            Hỗ trợ: JPG, PNG, WEBP (Max: 10MB)
                            {maxFiles > 1 && ` • Tối đa ${maxFiles} ảnh`}
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-3 justify-center">
                        <button
                            type="button"
                            onClick={handleClick}
                            className="btn-secondary"
                        >
                            <ImageIcon size={20} />
                            Chọn từ thiết bị
                        </button>

                        {isCameraAvailable && maxFiles === 1 && (
                            <button
                                type="button"
                                onClick={() => setShowCamera(true)}
                                className="btn-primary"
                            >
                                <Camera size={20} />
                                Chụp từ camera
                            </button>
                        )}
                    </div>
                </div>
            </motion.div>

            {/* Preview Grid */}
            {previews.length > 0 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"
                >
                    {previews.map((preview, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            className="relative group"
                        >
                            <div className="aspect-square rounded-xl overflow-hidden border-2 border-gray-200 hover:border-green-500 transition-all">
                                <img
                                    src={preview.url}
                                    alt={preview.file.name}
                                    className="w-full h-full object-cover"
                                />
                            </div>

                            {/* Remove Button */}
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    handleRemove(index)
                                }}
                                className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg hover:bg-red-600"
                            >
                                <X size={16} />
                            </button>

                            {/* File Info */}
                            <div className="mt-2 text-xs text-gray-600 text-center truncate">
                                {preview.file.name}
                            </div>
                            <div className="text-xs text-gray-400 text-center">
                                {formatFileSize(preview.file.size)}
                            </div>
                        </motion.div>
                    ))}
                </motion.div>
            )}

            {/* Camera Capture Modal */}
            {showCamera && (
                <CameraCapture
                    onCapture={handleCameraCapture}
                    onClose={() => setShowCamera(false)}
                />
            )}
        </div>
    )
}

export default ImageUploader

