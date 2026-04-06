import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
        modifyVars: {
          // 暗色主题配置 - 探案类应用专属暗黑风格
          'primary-color': '#722ed1', // 紫色主色调，符合悬疑探案氛围
          'success-color': '#52c41a',
          'warning-color': '#faad14',
          'error-color': '#f5222d',
          'font-size-base': '14px',
          'border-radius-base': '8px',
          'body-background': '#0a0a0a', // 深色背景
          'component-background': '#141414', // 组件背景
          'text-color': 'rgba(255, 255, 255, 0.88)',
          'text-color-secondary': 'rgba(255, 255, 255, 0.65)',
          'border-color-base': '#303030',
          'border-color-split': '#232323',
          'background-color-light': '#1e1e1e',
          'item-hover-bg': '#1e1e1e',
          'input-bg': '#1e1e1e',
          'select-background': '#1e1e1e',
          'modal-bg': '#141414',
          'card-background': '#141414',
        },
      },
    },
  },
})
