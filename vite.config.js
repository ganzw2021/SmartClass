import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const proxy = {
  '/api': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  },
  '/sign': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  },
  '/uploads': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  }
}

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        teacher: resolve(__dirname, 'teacher.html'),
        student: resolve(__dirname, 'student.html'),
        admin: resolve(__dirname, 'admin.html')
      }
    }
  },
  server: {
    host: '0.0.0.0',
    proxy
  }
})
