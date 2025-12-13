import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5000,
    allowedHosts: true,
    proxy: {
      '/api': 'http://localhost:8001',
      '/predict': 'http://localhost:8001',
      '/feedback': 'http://localhost:8001',
      '/stats': 'http://localhost:8001',
      '/static': 'http://localhost:8001'
    }
  }
})
