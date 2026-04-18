<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-slate-800">系统概览</h2>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.teachers }}</p>
            <p class="text-sm text-slate-500">教师</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.students }}</p>
            <p class="text-sm text-slate-500">学生</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.classes }}</p>
            <p class="text-sm text-slate-500">班级</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-800">{{ stats.courses }}</p>
            <p class="text-sm text-slate-500">课程</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 最近考勤 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 class="font-bold text-slate-700 mb-4">快捷操作</h3>
        <div class="space-y-3">
          <router-link to="?module=classes" class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors">
            <div class="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-slate-700">班级管理</p>
              <p class="text-xs text-slate-400">查看/编辑班级和学生</p>
            </div>
          </router-link>
          <router-link to="?module=teachers" class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors">
            <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-slate-700">教师管理</p>
              <p class="text-xs text-slate-400">添加/编辑/删除教师账号</p>
            </div>
          </router-link>
          <router-link to="?module=students" class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors">
            <div class="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-slate-700">学生账号</p>
              <p class="text-xs text-slate-400">批量创建账号/重置密码</p>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
        <h3 class="font-bold text-slate-700 mb-4">系统信息</h3>
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-slate-500">系统版本</span>
            <span class="font-medium text-slate-700">智慧课堂 v8.5</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">数据库</span>
            <span class="font-medium text-slate-700">MySQL 8.0</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">后端框架</span>
            <span class="font-medium text-slate-700">Flask</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">前端框架</span>
            <span class="font-medium text-slate-700">Vue 3 + Vite</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminStats } from '../api.js'

const stats = ref({ teachers: 0, students: 0, classes: 0, courses: 0 })

onMounted(async () => {
  try {
    const res = await getAdminStats()
    if (res.data) stats.value = res.data
  } catch (e) {
    console.error('加载统计失败', e)
  }
})
</script>
