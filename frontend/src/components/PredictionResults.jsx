/**
 * Prediction Results Component
 */
import { AlertTriangle, CheckCircle } from 'lucide-react'
import { getToxicityColor, formatConfidence } from '../utils/helpers'
import './PredictionResults.css'

const PredictionResults = ({ prediction }) => {
  if (!prediction || !prediction.success) return null

  const { best_prediction, top_predictions } = prediction
  const isPoisonous = best_prediction.toxicity.is_poisonous

  return (
    <div className="results">
      {/* Best Prediction Card */}
      <div
        className="prediction-card"
        style={{
          borderColor: getToxicityColor(isPoisonous),
        }}
      >
        <div className="prediction-header">
          {isPoisonous ? <AlertTriangle /> : <CheckCircle />}
          <h2>Kết quả Nhận diện</h2>
        </div>
        <div className="prediction-content">
          <div className="prediction-main">
            <h3>{best_prediction.genus}</h3>
            <p className="confidence">
              Độ tin cậy: {formatConfidence(best_prediction.confidence)}
            </p>
          </div>
          <div
            className="toxicity-warning"
            style={{
              backgroundColor: isPoisonous ? '#ffebee' : '#e8f5e9',
              color: getToxicityColor(isPoisonous),
            }}
          >
            <strong>{best_prediction.toxicity.warning}</strong>
            <p>{best_prediction.toxicity.toxicity_description}</p>
          </div>
        </div>
      </div>

      {/* Top Predictions */}
      <div className="top-predictions">
        <h3>Top {top_predictions.length} Dự đoán</h3>
        <div className="predictions-list">
          {top_predictions.map((pred, idx) => (
            <div key={idx} className="prediction-item">
              <div className="pred-rank">#{pred.rank}</div>
              <div className="pred-details">
                <div className="pred-genus">{pred.genus}</div>
                <div className="pred-confidence">
                  {formatConfidence(pred.confidence)}
                </div>
                <div
                  className={`pred-toxicity ${
                    pred.toxicity.is_poisonous ? 'poisonous' : 'edible'
                  }`}
                >
                  {pred.toxicity.is_poisonous ? '⚠️ Độc' : '✅ Ăn được'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PredictionResults











