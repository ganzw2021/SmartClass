import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 标记为教师端
window.__IS_TEACHER__ = true

createApp(App).mount('#app')
