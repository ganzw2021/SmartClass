<template>
  <div>
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold border-l-4 border-green-600 pl-3 text-slate-800">班级管理</h3>
      <button @click="openClassModal()" class="btn-green px-6 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        添加班级
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-3 gap-4 mt-6">
      <div class="glass-card bg-white p-6 text-center">
        <div class="text-3xl font-black text-[#2d6a4f]">{{ stats.total_classes }}</div>
        <div class="text-xs text-slate-400 mt-1">班级总数</div>
      </div>
      <div class="glass-card bg-white p-6 text-center">
        <div class="text-3xl font-black text-[#2d6a4f]">{{ stats.total_students }}</div>
        <div class="text-xs text-slate-400 mt-1">学生总数</div>
      </div>
      <div class="glass-card bg-white p-6 text-center">
        <div class="text-3xl font-black text-[#2d6a4f]">{{ stats.total_teachers }}</div>
        <div class="text-xs text-slate-400 mt-1">教师总数</div>
      </div>
    </div>

    <!-- 班级列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
      <div v-if="!classes.length" class="col-span-full py-10 text-center text-slate-400">
        暂无班级，请点击"添加班级"创建
      </div>

      <div
        v-for="cls in classes"
        :key="cls.id"
        class="glass-card bg-white p-6 border-t-4 border-green-600 shadow-sm"
      >
        <div class="flex justify-between items-start">
          <div>
            <h4 class="font-black text-slate-800 text-lg">{{ cls.name }}</h4>
            <p class="text-xs text-slate-500 mt-1">{{ cls.student_count || 0 }} 名学生</p>
          </div>
          <div class="flex gap-2">
            <button @click="openClassModal(cls)" class="text-green-600 hover:text-green-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="deleteClassHandler(cls.id)" class="text-slate-300 hover:text-red-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-4">点击编辑按钮管理班级学生</p>
      </div>
    </div>

    <!-- 班级弹窗（包含学生管理） -->
    <ClassModal
      v-if="showClassModal"
      :classData="editingClass"
      @close="showClassModal = false"
      @save="handleSaveClass"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminClasses, getStats, deleteClass as delClass } from '../admin-api.js'
import ClassModal from './ClassModal.vue'

const emit = defineEmits(['refresh'])

// 状态
const classes = ref([])
const stats = ref({ total_classes: 0, total_students: 0, total_teachers: 0 })
const showClassModal = ref(false)
const editingClass = ref(null)

// 加载数据
async function loadClasses() {
  try {
    const res = await getAdminClasses()
    if (res.success) {
      classes.value = res.data || []
    }
  } catch (e) {
    console.error('加载班级失败:', e)
  }
}

async function loadStats() {
  try {
    const res = await getStats()
    if (res.success) {
      stats.value = res.data || stats.value
    }
  } catch (e) {
    console.error('加载统计失败:', e)
  }
}

async function loadAll() {
  await Promise.all([loadClasses(), loadStats()])
}

// 班级操作
function openClassModal(cls = null) {
  editingClass.value = cls
  showClassModal.value = true
}

async function handleSaveClass() {
  showClassModal.value = false
  await loadClasses()
  await loadStats()
  emit('refresh')
}

async function deleteClassHandler(id) {
  if (!confirm('确定删除班级？')) return
  try {
    await delClass(id)
    await loadClasses()
    await loadStats()
  } catch (e) {
    alert(e.response?.data?.message || '删除失败')
  }
}

onMounted(() => {
  loadAll()
})
</script>
