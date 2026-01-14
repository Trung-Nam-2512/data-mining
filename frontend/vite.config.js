import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:1356',
        changeOrigin: true,
      }
    }
  },
  // Build configuration for production
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // Ensure relative paths for assets
    rollupOptions: {
      output: {
        // Use relative paths for assets
        assetFileNames: 'assets/[name].[hash].[ext]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js',
      }
    }
  },
  // Base path - use relative path for production
  base: './'
})










