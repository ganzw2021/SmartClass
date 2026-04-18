<template>
  <div class="flex flex-col items-center">
    <div 
      class="w-80 h-48 glass-card bg-white flex items-center justify-center text-4xl font-black text-green-800 shadow-2xl mb-12 border-4 border-green-200 tracking-widest text-center px-4 transition-all"
      :class="{ 'scale-110 text-red-600': showResult }"
    >
      {{ displayName }}
    </div>
    
    <div class="flex flex-col items-center gap-4 w-full max-w-sm">
      <label class="text-[10px] font-bold text-slate-400 uppercase w-full text-left">选择班级</label>
      <select v-model="selectedClass" class="w-full border-2 border-green-50 p-4 rounded-2xl outline-none font-bold text-center">
        <option value="">请选择班级</option>
        <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <button 
        @click="doRandom" 
        :disabled="!selectedClass || !students.length"
        class="w-full py-5 btn-green rounded-full text-xl font-black shadow-xl mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        开始随机抽取
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  classes: { type: Array, default: () => [] }
})

const selectedClass = ref('')
const displayName = ref('药都点兵')
const showResult = ref(false)

const currentClass = computed(() => {
  return props.classes.find(c => c.id === selectedClass.value)
})

const students = computed(() => {
  if (!currentClass.value) return []
  return currentClass.value.students || []
})

function doRandom() {
  if (!students.value.length) {
    alert('该班级无学生名册')
    return
  }
  
  let count = 0
  const total = 20
  const interval = setInterval(() => {
    const randomStudent = students.value[Math.floor(Math.random() * students.value.length)]
    displayName.value = typeof randomStudent === 'string' ? randomStudent : randomStudent.name
    
    count++
    if (count > total) {
      clearInterval(interval)
      showResult.value = true
      setTimeout(() => { showResult.value = false }, 1000)
    }
  }, 50)
}
</script>
