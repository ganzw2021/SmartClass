<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-slate-800">课程资源</h2>
    </div>

    <!-- 筛选条件 -->
    <div class="flex flex-wrap gap-4 bg-white p-4 rounded-2xl border border-slate-100">
      <div class="flex flex-col gap-1">
        <label class="text-xs text-slate-500 font-medium">学期</label>
        <select v-model="selectedTerm" @change="loadResources"
          class="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400">
          <option value="">全部学期</option>
          <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-xs text-slate-500 font-medium">课程</label>
        <select v-model="selectedCourse" @change="loadResources"
          class="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400">
          <option value="">全部课程</option>
          <option v-for="c in studentCourses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <!-- 资源列表 -->
    <div v-if="loading" class="text-center py-12 text-slate-400">加载中...</div>
    <div v-else-if="filteredResources.length === 0" class="text-center py-12 text-slate-400 bg-white rounded-2xl border border-slate-100">
      暂无课程资源
    </div>
    <div v-else class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="text-left py-3 px-4 text-slate-500 font-medium">资源名称</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium hidden md:table-cell">课程</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium hidden lg:table-cell">学期</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">大小</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredResources" :key="r.id" class="border-b border-slate-50 hover:bg-slate-50">
            <td class="py-3 px-4">
              <div class="flex items-center gap-3">
                <div :class="['w-10 h-10 rounded-lg flex items-center justify-center text-white flex-shrink-0', getFileColor(r.file_type)]">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="min-w-0">
                  <p class="font-medium text-slate-800 truncate max-w-[200px]" :title="r.title">{{ r.title }}</p>
                  <p v-if="r.description" class="text-xs text-slate-400 truncate max-w-[200px]" :title="r.description">{{ r.description }}</p>
                </div>
              </div>
            </td>
            <td class="py-3 px-4 text-slate-600 text-sm hidden md:table-cell">{{ r.course_name }}</td>
            <td class="py-3 px-4 text-slate-500 text-sm hidden lg:table-cell">{{ r.term }}</td>
            <td class="py-3 px-4 text-slate-500 text-sm">{{ formatFileSize(r.file_size) }}</td>
            <td class="py-3 px-4">
              <button @click="downloadResource(r)"
                class="px-4 py-1.5 rounded-lg text-sm font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors">
                下载
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStudentCourseResources, downloadCourseResource } from '../api.js'

const emit = defineEmits(['message'])

const props = defineProps({
  courses: { type: Array, default: () => [] }
})

const loading = ref(false)
const resources = ref([])
const selectedTerm = ref('')
const selectedCourse = ref('')

// 学生可选的课程（从作业模块传入）
const studentCourses = computed(() => props.courses)

// 学期列表
const terms = computed(() => {
  const set = new Set()
  resources.value.forEach(r => { if (r.term) set.add(r.term) })
  return [...set].sort().reverse()
})

// 筛选后的资源
const filteredResources = computed(() => {
  return resources.value.filter(r => {
    if (selectedTerm.value && r.term !== selectedTerm.value) return false
    if (selectedCourse.value && r.course_id !== selectedCourse.value) return false
    return true
  })
})

async function loadResources() {
  loading.value = true
  try {
    const res = await getStudentCourseResources({})
    resources.value = res.data || []
  } catch (e) {
    emit('message', { type: 'error', text: '加载资源失败' })
  } finally {
    loading.value = false
  }
}

function downloadResource(r) {
  downloadCourseResource(r.id)
}

function getFileColor(ext) {
  const map = {
    '.pdf': 'bg-red-500', '.doc': 'bg-blue-500', '.docx': 'bg-blue-500',
    '.ppt': 'bg-orange-500', '.pptx': 'bg-orange-500', '.xls': 'bg-green-500',
    '.xlsx': 'bg-green-500', '.jpg': 'bg-purple-500', '.jpeg': 'bg-purple-500',
    '.png': 'bg-purple-500', '.mp4': 'bg-pink-500', '.zip': 'bg-yellow-500'
  }
  return map[ext?.toLowerCase()] || 'bg-slate-500'
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

onMounted(loadResources)
</script>
