/**
 * Sidebar Component - Model Info and Classes List
 */
import { Info } from 'lucide-react'
import { useModelInfo } from '../hooks/useModelInfo'
import { useClasses } from '../hooks/useClasses'
import { getToxicityColor } from '../utils/helpers'
import './Sidebar.css'

const Sidebar = () => {
  const { modelInfo, loading: modelLoading } = useModelInfo()
  const { classes, loading: classesLoading } = useClasses()

  return (
    <aside className="sidebar">
      {/* Model Info Card */}
      <div className="info-card">
        <h3>
          <Info size={20} />
          Thông tin Model
        </h3>
        {modelLoading ? (
          <p>Đang tải thông tin...</p>
        ) : modelInfo ? (
          <div className="info-content">
            <p><strong>Backbone:</strong> {modelInfo.backbone}</p>
            <p><strong>Số classes:</strong> {modelInfo.num_classes}</p>
            <p><strong>Phase:</strong> {modelInfo.phase}</p>
            <p><strong>Device:</strong> {modelInfo.device}</p>
          </div>
        ) : (
          <p>Không thể tải thông tin model</p>
        )}
      </div>

      {/* Classes List Card */}
      {classes && (
        <div className="info-card">
          <h3>Danh sách Classes</h3>
          <div className="classes-list">
            {classes.classes.map((cls) => (
              <div
                key={cls.genus}
                className="class-item"
                style={{
                  borderLeft: `4px solid ${getToxicityColor(cls.is_poisonous)}`,
                }}
              >
                <span className="class-name">{cls.genus}</span>
                <span
                  className={`toxicity-badge ${
                    cls.is_poisonous ? 'poisonous' : 'edible'
                  }`}
                >
                  {cls.is_poisonous ? '⚠️ Độc' : '✅ Ăn được'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  )
}

export default Sidebar










