<template>
  <div>
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold border-l-4 border-green-600 pl-3 text-slate-800">课程管理</h3>
    </div>

    <!-- 课程列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
      <div v-if="!courses.length" class="col-span-full py-10 text-center text-slate-400">
        暂无课程
      </div>

      <div
        v-for="course in courses"
        :key="course.id"
        class="glass-card bg-white p-6 border-t-4 border-blue-500 shadow-sm"
      >
        <h4 class="font-black text-slate-800 text-lg">{{ course.name }}</h4>
        <p class="text-xs text-slate-400 mt-1">学期：{{ course.term || '未设置' }}</p>
        <p class="text-xs text-slate-400 mt-1">任课教师：{{ course.teacher_name || '未分配' }}</p>
        <p class="text-xs text-slate-400 mt-1">关联班级：{{ course.class_count || 0 }} 个</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminCourses } from '../admin-api.js'

const courses = ref([])

async function loadCourses() {
  try {
    const res = await getAdminCourses()
    if (res.success) {
      courses.value = res.data || []
    }
  } catch (e) {
    console.error('加载课程失败:', e)
  }
}

onMounted(() => {
  loadCourses()
})
</script>
