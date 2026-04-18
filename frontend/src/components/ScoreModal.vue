<template>
  <div>
    <h3 class="text-xl font-black mb-6">评分：{{ studentName }}</h3>
    
    <div class="space-y-6">
      <div>
        <label class="text-xs font-bold text-slate-400 block mb-2">考勤分 (0-20)</label>
        <input 
          v-model.number="formData.att" 
          type="number" 
          min="0" 
          max="20" 
          class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
        >
      </div>
      <div>
        <label class="text-xs font-bold text-slate-400 block mb-2">互动分 (0-10)</label>
        <input 
          v-model.number="formData.interact" 
          type="number" 
          min="0" 
          max="10" 
          class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
        >
      </div>
      <div>
        <label class="text-xs font-bold text-slate-400 block mb-2">作业分 (0-20)</label>
        <input 
          v-model.number="formData.hw" 
          type="number" 
          min="0" 
          max="20" 
          class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
        >
      </div>
    </div>

    <div class="flex gap-4 mt-8">
      <button @click="$emit('close')" class="flex-1 py-4 text-slate-400 font-bold">取消</button>
      <button @click="handleSave" class="flex-1 py-4 btn-green rounded-xl font-bold">保存成绩</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

const props = defineProps({
  student: { type: [Object, String], required: true },
  scores: { type: Object, default: () => ({ att: 20, interact: 0, hw: 20 }) }
})

const emit = defineEmits(['close', 'save'])

const formData = reactive({
  att: props.scores.att ?? 20,
  interact: props.scores.interact ?? 0,
  hw: props.scores.hw ?? 20
})

const studentName = computed(() => {
  return typeof props.student === 'string' ? props.student : (props.student.name || props.student.student_name || '')
})

function handleSave() {
  emit('save', { ...formData })
}
</script>
