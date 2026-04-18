import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 标记为管理端
window.__IS_ADMIN__ = true

createApp(App).mount('#app')
