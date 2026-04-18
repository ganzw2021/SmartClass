<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-slate-800">课程资源</h2>
      <button @click="showUploadModal = true" class="btn-green px-5 py-2.5 rounded-xl text-sm font-bold">
        + 上传资源
      </button>
    </div>

    <!-- 筛选条件 -->
    <div class="flex flex-wrap gap-4 bg-white p-4 rounded-2xl border border-slate-100">
      <div class="flex flex-col gap-1">
        <label class="text-xs text-slate-500 font-medium">学期</label>
        <select v-model="selectedTerm" @change="loadResources"
          class="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-green-400">
          <option value="">全部学期</option>
          <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-xs text-slate-500 font-medium">课程</label>
        <select v-model="selectedCourse" @change="loadResources"
          class="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-green-400">
          <option value="">全部课程</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <!-- 资源列表 -->
    <div v-if="loading" class="text-center py-12 text-slate-400">加载中...</div>
    <div v-else-if="filteredResources.length === 0" class="text-center py-12 text-slate-400 bg-white rounded-2xl border border-slate-100">
      暂无课程资源，点击右上角上传
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="r in filteredResources" :key="r.id"
        class="bg-white rounded-2xl border border-slate-100 p-5 hover:shadow-md transition-shadow">
        <!-- 文件图标 -->
        <div class="flex items-start gap-4">
          <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-white', getFileColor(r.file_type)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-slate-800 truncate" :title="r.title">{{ r.title }}</h3>
            <p class="text-sm text-slate-500 mt-1">{{ r.course_name }}</p>
            <div class="flex items-center gap-2 mt-2 text-xs text-slate-400">
              <span>{{ r.term }}</span>
              <span>•</span>
              <span>{{ formatFileSize(r.file_size) }}</span>
              <span>•</span>
              <span>{{ formatDate(r.created_at) }}</span>
            </div>
          </div>
        </div>
        <!-- 操作按钮 -->
        <div class="flex items-center gap-2 mt-4 pt-4 border-t border-slate-50">
          <button @click="downloadResource(r)" class="flex-1 py-2 rounded-lg text-sm font-medium bg-green-50 text-green-700 hover:bg-green-100 transition-colors">
            下载
          </button>
          <button @click="deleteResource(r)" class="px-4 py-2 rounded-lg text-sm font-medium bg-red-50 text-red-600 hover:bg-red-100 transition-colors">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showUploadModal = false">
        <div class="bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl">
          <h3 class="text-xl font-bold text-slate-800 mb-6">上传课程资源</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">课程 *</label>
              <select v-model="uploadForm.course_id" @change="onCourseChange"
                class="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-green-400">
                <option value="">请选择课程</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">资源标题 *</label>
              <input v-model="uploadForm.title" type="text" placeholder="输入资源标题"
                class="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-green-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">资源描述</label>
              <textarea v-model="uploadForm.description" rows="3" placeholder="可选，描述资源内容"
                class="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-green-400 resize-none"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">选择文件 *</label>
              <div @click="$refs.fileInput.click()"
                class="w-full border-2 border-dashed border-slate-200 rounded-xl p-8 text-center cursor-pointer hover:border-green-400 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 mx-auto text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16.6 7c-.11.38-.224.765-.33 1.155m-1.44 2.39A6 6 0 0014.94 19H5.06a6 6 0 00-4.498 1.378L2.38 20.702 4.06 21a8 8 0 009.74-4.08" />
                </svg>
                <p class="mt-2 text-sm text-slate-500">{{ selectedFile ? selectedFile.name : '点击选择文件或拖拽到此处' }}</p>
                <p class="mt-1 text-xs text-slate-400">支持 PDF、Word、PPT、图片等常见格式</p>
              </div>
              <input ref="fileInput" type="file" class="hidden" @change="onFileSelected" />
              <!-- 已选文件预览 -->
              <div v-if="selectedFile" class="mt-2 flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-green-800 truncate">{{ selectedFile.name }}</p>
                  <p class="text-xs text-green-600">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
                <button @click="clearSelectedFile" class="text-green-600 hover:text-green-800">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div class="flex gap-3 mt-8">
            <button @click="showUploadModal = false" class="flex-1 py-3 rounded-xl border border-slate-200 text-slate-600 font-medium hover:bg-slate-50 transition-colors">
              取消
            </button>
            <button @click="uploadResource" :disabled="uploading || !uploadForm.course_id || !uploadForm.title || !selectedFile"
              class="flex-1 py-3 rounded-xl bg-[#2d6a4f] text-white font-medium hover:bg-[#245a3f] transition-colors disabled:opacity-50">
              {{ uploading ? '上传中...' : '确认上传' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCourseResources, uploadCourseResource, deleteCourseResource, downloadCourseResource } from '../api.js'

const props = defineProps({
  courses: { type: Array, default: () => [] }
})

const emit = defineEmits(['message'])

// 状态
const loading = ref(false)
const resources = ref([])
const selectedTerm = ref('')
const selectedCourse = ref('')
const uploading = ref(false)
const showUploadModal = ref(false)
const selectedFile = ref(null)

// 上传表单
const uploadForm = ref({
  course_id: '',
  course_name: '',
  term: ''
})

// 学期列表
const terms = computed(() => {
  const set = new Set()
  props.courses.forEach(c => { if (c.term) set.add(c.term) })
  return [...set].sort()
})

// 筛选后的资源
const filteredResources = computed(() => {
  return resources.value.filter(r => {
    if (selectedTerm.value && r.term !== selectedTerm.value) return false
    if (selectedCourse.value && r.course_id !== selectedCourse.value) return false
    return true
  })
})

// 加载资源
async function loadResources() {
  loading.value = true
  try {
    const res = await getCourseResources({})
    resources.value = res.data || []
  } catch (e) {
    emit('message', { type: 'error', text: '加载资源失败' })
  } finally {
    loading.value = false
  }
}

// 选择课程
function onCourseChange() {
  const c = props.courses.find(x => x.id === uploadForm.value.course_id)
  if (c) {
    uploadForm.value.course_name = c.name
    uploadForm.value.term = c.term || ''
  }
}

// 选择文件
function onFileSelected(e) {
  const file = e.target.files[0]
  selectedFile.value = file
  console.log('文件选择:', file?.name, file?.size)
}

// 清除已选文件
function clearSelectedFile() {
  selectedFile.value = null
  if (window.$refs && window.$refs.fileInput) {
    window.$refs.fileInput.value = ''
  }
  // 通过 DOM 重置 input
  const input = document.querySelector('input[type="file"]')
  if (input) input.value = ''
}

// 上传资源
async function uploadResource() {
  if (!uploadForm.value.course_id || !uploadForm.value.title || !selectedFile.value) {
    emit('message', { type: 'error', text: '请填写完整信息并选择文件' })
    return
  }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('course_id', uploadForm.value.course_id)
    fd.append('course_name', uploadForm.value.course_name)
    fd.append('term', uploadForm.value.term)
    fd.append('title', uploadForm.value.title)
    fd.append('description', uploadForm.value.description || '')
    fd.append('file', selectedFile.value)
    await uploadCourseResource(fd)
    emit('message', { type: 'success', text: '上传成功' })
    showUploadModal.value = false
    uploadForm.value = { course_id: '', course_name: '', term: '' }
    selectedFile.value = null
    if (window.__fileInput__) window.__fileInput__.value = ''
    loadResources()
  } catch (e) {
    emit('message', { type: 'error', text: '上传失败' })
  } finally {
    uploading.value = false
  }
}

// 下载资源
function downloadResource(r) {
  downloadCourseResource(r.id)
}

// 删除资源
async function deleteResource(r) {
  if (!confirm(`确定删除「${r.title}」吗？`)) return
  try {
    await deleteCourseResource(r.id)
    emit('message', { type: 'success', text: '已删除' })
    loadResources()
  } catch (e) {
    emit('message', { type: 'error', text: '删除失败' })
  }
}

// 工具函数
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

function formatDate(str) {
  if (!str) return ''
  return str.slice(0, 10)
}

onMounted(loadResources)
</script>
