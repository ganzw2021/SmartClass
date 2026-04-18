<template>
  <div>
    <h3 class="text-xl font-black mb-6">{{ courseData ? '修改课程' : '开设新课程' }}</h3>
    
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="text-xs font-bold text-slate-400 block mb-1">学年</label>
          <select v-model="formData.year" class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none font-bold bg-slate-50">
            <option v-for="yr in yearOptions" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-bold text-slate-400 block mb-1">学期</label>
          <select v-model="formData.term" class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none font-bold bg-slate-50">
            <option value="第1学期">第1学期</option>
            <option value="第2学期">第2学期</option>
          </select>
        </div>
      </div>
      
      <div>
        <label class="text-xs font-bold text-slate-400 block mb-1">课程名称</label>
        <input v-model="formData.name" type="text" placeholder="中医基础理论" class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none">
      </div>

      <!-- 关联班级 -->
      <div>
        <label class="text-xs font-bold text-slate-400 block mb-2">关联班级</label>
        <div class="border-2 border-slate-50 rounded-xl p-3 bg-slate-50 max-h-48 overflow-y-auto">
          <div v-if="loading" class="text-center text-slate-400 py-4">加载中...</div>
          <div v-else-if="!allClasses.length" class="text-center text-slate-400 py-4">暂无可选班级</div>
          <div v-else class="space-y-2">
            <label
              v-for="cls in allClasses"
              :key="cls.id"
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-white cursor-pointer"
            >
              <input
                type="checkbox"
                :value="cls.id"
                v-model="formData.classIds"
                class="w-4 h-4 text-green-600 rounded"
              />
              <span class="flex-1 text-sm">{{ cls.name }}</span>
              <span class="text-xs text-slate-400">{{ cls.student_count }}人</span>
            </label>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-2">已选择 {{ formData.classIds.length }} 个班级</p>
      </div>
    </div>

    <div class="flex gap-4 mt-8">
      <button @click="$emit('close')" class="flex-1 py-4 text-slate-400 font-bold">取消</button>
      <button @click="handleSave" class="flex-1 py-4 btn-green rounded-xl font-bold shadow-lg">确认{{ courseData ? '修改' : '创建' }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { createCourse as apiCreateCourse, updateCourse as apiUpdateCourse, getAllClasses } from '../api.js'

const props = defineProps({
  courseData: { type: Object, default: null }
})

const emit = defineEmits(['close', 'success'])

const loading = ref(true)
const allClasses = ref([])

const currentYear = new Date().getFullYear()
const yearOptions = computed(() => {
  return [-1, 0, 1, 2].map(i => `${currentYear + i}-${currentYear + i + 1}学年`)
})

const formData = reactive({
  name: props.courseData?.name || '',
  year: props.courseData?.term?.split(' ')[0] || `${currentYear}-${currentYear + 1}学年`,
  term: props.courseData?.term?.split(' ')[1] || '第1学期',
  classIds: []
})

// 加载班级列表
async function loadClasses() {
  loading.value = true
  try {
    const res = await getAllClasses()
    if (res.success) {
      allClasses.value = res.data || []
    }
  } catch (e) {
    console.error('加载班级失败', e)
  }
  loading.value = false
}

// 加载已关联班级
function loadCourseClasses() {
  if (props.courseData?.classes) {
    formData.classIds = props.courseData.classes.map(c => c.id)
  }
}

onMounted(async () => {
  await loadClasses()
  loadCourseClasses()
})

async function handleSave() {
  if (!formData.name.trim()) {
    alert('请输入课程名称')
    return
  }
  
  const term = `${formData.year} ${formData.term}`
  
  try {
    const data = {
      name: formData.name.trim(),
      term,
      class_ids: formData.classIds
    }
    if (props.courseData) {
      await apiUpdateCourse(props.courseData.id, data)
    } else {
      await apiCreateCourse(data)
    }
    emit('success', formData)
  } catch (e) {
    alert(e.response?.data?.message || '保存失败')
  }
}
</script>
