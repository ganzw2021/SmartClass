import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 标记为教师端，同时清除其他模式标记，防止浏览器缓存导致模式错乱
window.__IS_TEACHER__ = true
window.__IS_ADMIN__ = false
window.__IS_STUDENT__ = false

createApp(App).mount('#app')
