/**
 * Application Constants
 */

// Model Names
export const MODEL_NAMES = {
  RESNET50: 'resnet50',
  EFFICIENTNET_B0: 'efficientnet_b0',
  MOBILENET_V3_LARGE: 'mobilenet_v3_large',
}

export const MODEL_DISPLAY_NAMES = {
  resnet50: 'ResNet-50',
  efficientnet_b0: 'EfficientNet-B0',
  mobilenet_v3_large: 'MobileNetV3-Large',
}

// File Upload
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const MAX_BATCH_SIZE = 5
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

// Toxicity Info
export const TOXICITY_LABELS = {
  P: { label: 'Độc', color: 'danger', icon: '☠️' },
  E: { label: 'Ăn được', color: 'success', icon: '✅' },
}

// Mushroom Genera
export const ALL_GENERA = [
  'Agaricus',
  'Amanita',
  'Boletus',
  'Cortinarius',
  'Entoloma',
  'Hygrocybe',
  'Lactarius',
  'Russula',
  'Suillus',
  'Exidia',
  'Inocybe',
]

// Navigation Items
export const NAV_ITEMS = [
  { path: '/', label: 'Nhận diện đơn', icon: 'Image' },
  { path: '/batch', label: 'Nhận diện nhiều', icon: 'Images' },
  { path: '/gradcam', label: 'Grad-CAM', icon: 'Eye' },
  { path: '/history', label: 'Lịch sử', icon: 'History' },
]

// Animation Variants for Framer Motion
export const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.3 } },
}

export const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.4 }
  },
}

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 }
  },
}
