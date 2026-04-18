<template>
  <div>
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold border-l-4 border-green-600 pl-3 text-slate-800">教学课程管理</h3>
      <button @click="openCreateModal" class="btn-green px-6 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        开设新课程
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
      <div v-if="!courses.length" class="col-span-full py-10 text-center text-slate-400">
        暂无课程，请点击"开设新课程"创建
      </div>

      <div 
        v-for="course in courses" 
        :key="course.id" 
        class="glass-card bg-white p-6 border-t-4 border-indigo-600"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <h4 class="font-black text-slate-800 text-lg">{{ course.name }}</h4>
            <span class="bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded text-[10px] font-bold mt-1 inline-block">
              {{ course.term || course.year_term || '未设置学期' }}
            </span>
          </div>
          <div class="flex gap-2">
            <button @click="openEditModal(course)" class="text-slate-300 hover:text-indigo-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="handleDelete(course.id)" class="text-slate-300 hover:text-red-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
        <div class="mt-3">
          <p class="text-xs text-slate-500 mb-1">
            {{ course.class_count ? `关联 ${course.class_count} 个班级` : '未关联班级' }}
          </p>
          <div v-if="course.classes?.length" class="flex flex-wrap gap-1">
            <span 
              v-for="cls in course.classes" 
              :key="cls.id"
              class="text-[10px] bg-green-50 text-green-700 px-2 py-0.5 rounded"
            >
              {{ cls.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 课程弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showModal = false">
        <div class="bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
          <CourseModal 
            v-if="showModal"
            :course-data="editingCourse"
            @close="closeModal"
            @success="handleSuccess"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTeacherCourses, deleteCourse } from '../api.js'
import CourseModal from './CourseModal.vue'

const emit = defineEmits(['refresh'])

const courses = ref([])
const showModal = ref(false)
const editingCourse = ref(null)

async function loadCourses() {
  try {
    const res = await getTeacherCourses()
    if (res.success) {
      // API 返回 {courses: [...], terms: [...]} 或直接是课程数组
      if (Array.isArray(res.data)) {
        courses.value = res.data || []
      } else {
        courses.value = res.data?.courses || []
      }
      emit('refresh')
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

function openCreateModal() {
  editingCourse.value = null
  showModal.value = true
}

function openEditModal(course) {
  editingCourse.value = course
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingCourse.value = null
}

function handleSuccess() {
  closeModal()
  loadCourses()
}

async function handleDelete(id) {
  if (confirm('确定删除课程？')) {
    try {
      const res = await deleteCourse(id)
      if (res.success) {
        loadCourses()
      } else {
        alert(res.message || '删除失败')
      }
    } catch (e) {
      alert('删除失败')
    }
  }
}

onMounted(() => {
  loadCourses()
})
</script>
