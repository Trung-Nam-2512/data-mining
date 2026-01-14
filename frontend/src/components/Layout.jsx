/**
 * Main Layout Component with Navbar and Sidebar
 */
import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Image, Grid, Eye, History, Menu, X,
    Activity, Database, Layers
} from 'lucide-react'
import { checkHealth, getModelInfo } from '../services/api'
import toast from 'react-hot-toast'

const navItems = [
    { path: '/', label: 'Nhận diện đơn', icon: Image, description: 'Phân loại một ảnh nấm' },
    { path: '/batch', label: 'Nhận diện nhiều', icon: Grid, description: 'Phân loại nhiều ảnh cùng lúc (max 5)' },
    { path: '/gradcam', label: 'Grad-CAM', icon: Eye, description: 'Trực quan hóa quyết định của model' },
    { path: '/history', label: 'Lịch sử & Thống kê', icon: History, description: 'Xem lịch sử và thống kê' },
]

const Layout = ({ children }) => {
    const location = useLocation()
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [healthStatus, setHealthStatus] = useState(null)
    const [modelInfo, setModelInfo] = useState(null)

    useEffect(() => {
        // Check health on mount
        const checkBackendHealth = async () => {
            try {
                const health = await checkHealth()
                setHealthStatus(health)

                if (health.models_loaded) {
                    const info = await getModelInfo()
                    setModelInfo(info)
                }
            } catch (error) {
                console.error('Health check failed:', error)
                toast.error('Không thể kết nối đến backend')
            }
        }

        checkBackendHealth()
    }, [])

    const isActivePath = (path) => location.pathname === path

    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 via-white to-green-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md shadow-md border-b border-gray-200 sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-3 group">
                            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                                <span className="text-2xl">🍄</span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold gradient-text">
                                    Mushroom Classifier
                                </h1>
                                <p className="text-xs text-gray-600">
                                    AI-Powered Mushroom Recognition
                                </p>
                            </div>
                        </Link>

                        {/* Health Status */}
                        <div className="hidden md:flex items-center gap-4">
                            {healthStatus && (
                                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg">
                                    <Activity
                                        size={18}
                                        className={healthStatus.models_loaded ? 'text-green-600 animate-pulse' : 'text-red-600'}
                                    />
                                    <span className="text-sm font-semibold text-gray-700">
                                        {healthStatus.models_loaded ? 'Online' : 'Offline'}
                                    </span>
                                </div>
                            )}

                            {modelInfo && (
                                <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
                                    <Layers size={18} className="text-blue-600" />
                                    <span className="text-sm font-semibold text-gray-700">
                                        {modelInfo.num_models} Models
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Sidebar - Desktop */}
                <aside className="hidden md:block w-72 bg-white/50 backdrop-blur-sm border-r border-gray-200 p-6 overflow-y-auto">
                    <nav className="space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon
                            const active = isActivePath(item.path)

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-start gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${active
                                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                                        : 'hover:bg-gray-100 text-gray-700'
                                        }`}
                                >
                                    <Icon
                                        size={24}
                                        className={active ? '' : 'group-hover:scale-110 transition-transform'}
                                    />
                                    <div>
                                        <div className="font-semibold">{item.label}</div>
                                        <div className={`text-xs mt-1 ${active ? 'text-white/90' : 'text-gray-500'}`}>
                                            {item.description}
                                        </div>
                                    </div>
                                </Link>
                            )
                        })}
                    </nav>

                    {/* Model Info Card */}
                    {modelInfo && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-8 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
                        >
                            <div className="flex items-center gap-2 mb-3">
                                <Database size={18} className="text-blue-600" />
                                <h3 className="font-semibold text-gray-800">Ensemble Info</h3>
                            </div>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Type:</span>
                                    <span className="font-semibold text-gray-800">{modelInfo.ensemble_type}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Models:</span>
                                    <span className="font-semibold text-gray-800">{modelInfo.num_models}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Classes:</span>
                                    <span className="font-semibold text-gray-800">{modelInfo.num_classes}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Device:</span>
                                    <span className="font-semibold text-gray-800 uppercase">{modelInfo.device}</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </aside>

                {/* Sidebar - Mobile */}
                {sidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="md:hidden fixed inset-0 bg-black/50 z-40"
                        onClick={() => setSidebarOpen(false)}
                    >
                        <motion.aside
                            initial={{ x: -300 }}
                            animate={{ x: 0 }}
                            exit={{ x: -300 }}
                            className="w-72 bg-white h-full p-6 overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <nav className="space-y-2">
                                {navItems.map((item) => {
                                    const Icon = item.icon
                                    const active = isActivePath(item.path)

                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            onClick={() => setSidebarOpen(false)}
                                            className={`flex items-start gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${active
                                                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                                                : 'hover:bg-gray-100 text-gray-700'
                                                }`}
                                        >
                                            <Icon size={24} />
                                            <div>
                                                <div className="font-semibold">{item.label}</div>
                                                <div className={`text-xs mt-1 ${active ? 'text-white/90' : 'text-gray-500'}`}>
                                                    {item.description}
                                                </div>
                                            </div>
                                        </Link>
                                    )
                                })}
                            </nav>
                        </motion.aside>
                    </motion.div>
                )}

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto">
                    <div className="container mx-auto px-4 py-8 max-w-7xl">
                        {children}
                    </div>
                </main>
            </div>

            {/* Footer */}
            <footer className="bg-white/80 backdrop-blur-md border-t border-gray-200 py-6">
                <div className="container mx-auto px-4 text-center">
                    <p className="text-gray-600">
                        © 2026 Nhóm 1 •{' '}
                        <span className="font-semibold text-green-600">
                            Mushroom Classification System
                        </span>
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                        ResNet-50 • EfficientNet-B0 • MobileNetV3-Large
                    </p>
                </div>
            </footer>
        </div>
    )
}

export default Layout

