import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 标记为学生端
window.__IS_STUDENT__ = true

createApp(App).mount('#app')
