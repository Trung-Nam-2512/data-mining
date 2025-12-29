/**
 * Image Upload Component
 */
import { useState } from 'react'
import { Upload } from 'lucide-react'
import { validateImageFile, createImagePreview } from '../utils/helpers'
import './ImageUpload.css'

const ImageUpload = ({ onFileSelect, selectedFile, preview }) => {
  const [error, setError] = useState(null)

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file
    const validation = validateImageFile(file)
    if (!validation.valid) {
      setError(validation.error)
      return
    }

    setError(null)

    // Create preview
    try {
      const previewUrl = await createImagePreview(file)
      onFileSelect(file, previewUrl)
    } catch (err) {
      setError('Không thể đọc file ảnh')
    }
  }

  const handleRemove = () => {
    onFileSelect(null, null)
    setError(null)
  }

  return (
    <div className="upload-section">
      <div className="upload-box">
        {preview ? (
          <div className="image-preview">
            <img src={preview} alt="Preview" />
            <button className="btn-remove" onClick={handleRemove}>
              Xóa ảnh
            </button>
          </div>
        ) : (
          <label className="upload-label">
            <Upload size={48} />
            <span>Chọn ảnh nấm để nhận diện</span>
            <span className="upload-hint">Hỗ trợ: JPG, JPEG, PNG</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="file-input"
            />
          </label>
        )}
      </div>

      {error && (
        <div className="upload-error">
          {error}
        </div>
      )}
    </div>
  )
}

export default ImageUpload





