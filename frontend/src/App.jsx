/**
 * Main App Component with Routing
 */
import { Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import BatchPage from './pages/BatchPage'
import GradCAMPage from './pages/GradCAMPage'
import HistoryPage from './pages/HistoryPage'

function App() {
  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/batch" element={<BatchPage />} />
          <Route path="/gradcam" element={<GradCAMPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </AnimatePresence>
    </Layout>
  )
}

export default App
