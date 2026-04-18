<template>
  <div class="min-h-screen flex flex-col">
    <!-- 未登录显示登录页 -->
    <LoginPage v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

    <!-- 已登录显示管理后台 -->
    <template v-else>
      <!-- Header -->
      <header class="bg-white border-b border-green-100 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="bg-[#2d6a4f] p-2 rounded-lg text-white">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-bold text-slate-800 leading-none">江西樟树中医药职业学院</h1>
              <p class="text-xs text-green-700 mt-1 font-medium">智慧课堂管理系统</p>
            </div>
          </div>

          <nav class="hidden lg:flex h-full no-scrollbar overflow-x-auto">
            <button
              v-for="item in navItems"
              :key="item.id"
              @click="switchModule(item.id)"
              :class="['px-4 h-full flex items-center gap-2 transition-all whitespace-nowrap',
                currentModule === item.id ? 'nav-active text-[#2d6a4f] font-bold' : 'text-slate-500 hover:text-green-700']">
              <component :is="item.icon" class="w-4 h-4" />
              {{ item.label }}
            </button>
          </nav>

          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">{{ adminUser?.username }}</span>
            <button @click="logout" class="text-slate-400 hover:text-red-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- Main Content - 懒加载模块 -->
      <main class="max-w-7xl mx-auto w-full p-6 flex-grow overflow-x-hidden">
        <KeepAlive>
          <component :is="currentComponent" :key="currentModule" />
        </KeepAlive>
      </main>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw, defineAsyncComponent } from 'vue'
import LoginPage from './components/LoginPage.vue'

// 懒加载模块
const AdminClassModule = defineAsyncComponent(() => import('./components/AdminClassModule.vue'))
const TeacherModule = defineAsyncComponent(() => import('./components/TeacherModule.vue'))
const CourseModule = defineAsyncComponent(() => import('./components/CourseModule.vue'))
const AttendanceModule = defineAsyncComponent(() => import('./components/AttendanceModule.vue'))

// 登录状态
const isLoggedIn = ref(false)
const adminUser = ref(null)
const currentModule = ref('classes')

// 导航配置
const navItems = [
  { id: 'classes', label: '班级管理', component: AdminClassModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }) },
  { id: 'teachers', label: '教师管理', component: TeacherModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }) },
  { id: 'courses', label: '课程管理', component: CourseModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>' }) },
  { id: 'attendance', label: '考勤记录', component: AttendanceModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>' }) },
]

// 当前组件
const currentComponent = computed(() => {
  const item = navItems.find(n => n.id === currentModule.value)
  return item?.component || AdminClassModule
})

// 切换模块
function switchModule(id) {
  currentModule.value = id
}

// 登录成功
function handleLoginSuccess(user) {
  isLoggedIn.value = true
  adminUser.value = user
}

// 登出
function logout() {
  sessionStorage.removeItem('tc_admin_token')
  sessionStorage.removeItem('tc_admin_user')
  isLoggedIn.value = false
  adminUser.value = null
}

// 检查登录状态
onMounted(() => {
  const token = sessionStorage.getItem('tc_admin_token')
  const user = sessionStorage.getItem('tc_admin_user')
  if (token && user) {
    try {
      adminUser.value = JSON.parse(user)
      isLoggedIn.value = true
    } catch (e) {
      sessionStorage.removeItem('tc_admin_token')
      sessionStorage.removeItem('tc_admin_user')
    }
  }
})
</script>
