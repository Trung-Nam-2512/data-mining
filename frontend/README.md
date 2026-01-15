# 🍄 Mushroom Classification - Frontend

Modern, beautiful React application for mushroom classification using Deep Learning ensemble models.

## ✨ Features

### 🎯 Single Prediction
- Upload single mushroom image
- Get prediction from 3-model ensemble
- View individual model predictions
- Toxicity warnings for poisonous mushrooms

### 📦 Batch Prediction
- Upload up to 5 images at once
- Process multiple images efficiently
- View results for all images
- Automatic history saving

### 👁️ Grad-CAM Visualization
- Visualize what AI models "see"
- Generate heatmaps for all 3 models
- Adjustable overlay transparency
- Download visualizations

### 📊 History & Statistics
- View prediction history
- See statistics dashboard
- Top recognized genera chart
- Filter and pagination

## 🛠️ Tech Stack

- **React 18** - Modern React with Hooks
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **React Router** - Client-side routing
- **React Hot Toast** - Beautiful notifications
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Backend API running on port 1356

### Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Create .env file:**
```bash
VITE_API_BASE_URL=http://localhost:1356
VITE_APP_NAME=Mushroom Classification System
VITE_APP_VERSION=1.0.0
```

3. **Start development server:**
```bash
npm run dev
```

4. **Open browser:**
```
http://localhost:3000
```

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Layout.jsx       # Main layout with nav
│   │   ├── ImageUploader.jsx   # Drag & drop uploader
│   │   ├── PredictionResult.jsx # Result display
│   │   └── LoadingSpinner.jsx   # Loading state
│   ├── pages/              # Page components
│   │   ├── HomePage.jsx    # Single prediction
│   │   ├── BatchPage.jsx   # Batch prediction
│   │   ├── GradCAMPage.jsx # Visualization
│   │   └── HistoryPage.jsx # History & stats
│   ├── services/           # API services
│   │   └── api.js          # API client
│   ├── utils/              # Utilities
│   │   ├── constants.js    # App constants
│   │   └── helpers.js      # Helper functions
│   ├── App.jsx             # Main app with routing
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── package.json            # Dependencies
```

## 🎨 Design Features

### Modern UI
- Gradient backgrounds and cards
- Glassmorphism effects
- Smooth animations with Framer Motion
- Responsive design (mobile-first)

### User Experience
- Drag & drop file upload
- Real-time validation
- Toast notifications
- Loading states with progress
- Error handling

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## 🌐 API Integration

### Base URL
```javascript
const API_BASE_URL = 'http://localhost:1356'
```

### Endpoints Used
- `GET /api/v1/health` - Health check
- `GET /api/v1/models/info` - Model information
- `GET /api/v1/models/classes` - Class list
- `POST /api/v1/predict` - Single prediction
- `POST /api/v1/predict/batch` - Batch prediction
- `POST /api/v1/gradcam` - Single Grad-CAM
- `POST /api/v1/gradcam/all` - All models Grad-CAM
- `GET /api/v1/statistics` - Statistics
- `GET /api/v1/history` - History

## 🎯 Key Features Explained

### Ensemble Prediction
- Uses 3 models: ResNet-50, EfficientNet-B0, MobileNetV3-Large
- Soft Voting: Averages probabilities from all models
- Shows individual model predictions
- Top-k predictions display

### Toxicity Detection
- Automatic toxicity classification
- Visual warnings for poisonous mushrooms
- Color-coded badges (red=poisonous, green=edible)

### Grad-CAM
- Gradient-weighted Class Activation Mapping
- Shows which image regions influenced the decision
- Helps understand and debug model predictions
- Downloadable heatmap images

## 🔧 Configuration

### Environment Variables
```
VITE_API_BASE_URL     - Backend API URL
VITE_APP_NAME         - Application name
VITE_APP_VERSION      - Application version
```

### Customization
- **Colors**: Edit `tailwind.config.js`
- **Animations**: Modify `src/utils/constants.js`
- **API timeout**: Adjust in `src/services/api.js`
- **Max batch size**: Change `MAX_BATCH_SIZE` in constants

## 📱 Responsive Design

- **Mobile**: < 768px - Single column, stacked layout
- **Tablet**: 768px - 1024px - 2-column grid
- **Desktop**: > 1024px - Full multi-column layout

## 🐛 Troubleshooting

### Common Issues

**1. API Connection Failed**
- Ensure backend is running on port 1356
- Check VITE_API_BASE_URL in .env
- Verify network connectivity

**2. Images Not Uploading**
- Check file size (max 10MB)
- Verify file format (JPG, PNG, WEBP)
- Clear browser cache

**3. Slow Performance**
- Enable production build
- Check backend server resources
- Optimize image sizes

## 📝 Development

### Code Style
- ESLint for linting
- Prettier for formatting
- Follow React best practices

### Adding New Features
1. Create component in `src/components/`
2. Add page in `src/pages/`
3. Update routing in `App.jsx`
4. Add API calls in `src/services/api.js`

## 🎉 Deployment

### Build Production
```bash
npm run build
```

Builds to `dist/` folder.

### Deploy Options
- **Vercel**: `vercel --prod`
- **Netlify**: Drag & drop `dist/` folder
- **Docker**: Use included Dockerfile (if created)
- **Static hosting**: Upload `dist/` to any web server

### Environment Variables for Production
```
VITE_API_BASE_URL=https://your-backend-api.com
```

## 📄 License

MIT License - Feel free to use for learning and projects

## 🙏 Credits

- **Deep Learning Models**: ResNet, EfficientNet, MobileNet
- **UI Framework**: TailwindCSS
- **Icons**: Lucide React
- **Animations**: Framer Motion

---

Built with ❤️ using React & TailwindCSS


