<template>
  <div class="glass-card bg-white p-8">
    <h3 class="font-bold text-slate-800 mb-6 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
      </svg>
      系统连接设置
    </h3>
    
    <div class="space-y-4">
      <div>
        <label class="block text-xs font-bold text-slate-400 mb-2">后端 API 地址</label>
        <input 
          v-model="settings.api" 
          type="text" 
          placeholder="http://192.168.x.x:3000" 
          class="w-full border-2 border-green-50 p-4 rounded-xl outline-none"
        >
      </div>
      
      <div>
        <label class="block text-xs font-bold text-slate-400 mb-2">
          教师唯一标识 (Teacher Token)
          <span class="ml-2 text-green-600 font-normal normal-case">— 多老师并发时用于隔离数据，请勿与他人共享</span>
        </label>
        <div class="flex gap-2">
          <input 
            v-model="settings.teacherId" 
            type="text" 
            placeholder="自动生成" 
            class="flex-1 border-2 border-green-50 p-4 rounded-xl outline-none font-mono text-sm text-slate-500"
          >
          <button @click="regenerateTeacherId" class="px-4 py-2 border-2 border-green-100 rounded-xl text-xs font-bold text-green-700 hover:bg-green-50 transition-colors whitespace-nowrap">
            重新生成
          </button>
        </div>
        <p class="text-xs text-slate-400 mt-1">首次使用会自动生成，保存后固定不变。如需在多台设备共享同一老师身份，可手动复制此值。</p>
      </div>
      
      <button @click="saveSettings" class="w-full mt-4 py-4 btn-green rounded-xl font-bold transition-all">
        保存设置
      </button>
      
      <p v-if="saveTip" class="text-center text-xs text-green-600 font-bold mt-3 opacity-100 transition-opacity">
        {{ saveTip }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const settings = ref({
  api: '',
  teacherId: ''
})

const saveTip = ref('')

onMounted(() => {
  // 加载本地设置
  const saved = localStorage.getItem('tc_settings')
  if (saved) {
    try {
      settings.value = JSON.parse(saved)
    } catch (e) {}
  }
  
  // 如果没有 teacherId，自动生成
  if (!settings.value.teacherId) {
    regenerateTeacherId()
  }
})

function regenerateTeacherId() {
  const newId = 'teacher_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8)
  settings.value.teacherId = newId
}

function saveSettings() {
  localStorage.setItem('tc_settings', JSON.stringify(settings.value))
  saveTip.value = '已成功保存设置'
  setTimeout(() => { saveTip.value = '' }, 3000)
}
</script>
