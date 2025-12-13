import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: true,
    proxy: {
      '/predict': 'http://localhost:8000',
      '/feedback': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
      '/static': 'http://localhost:8000'
    }
  }
})
