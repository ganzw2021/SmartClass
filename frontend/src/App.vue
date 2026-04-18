<template>
  <div class="min-h-screen flex flex-col">
    <!-- 未登录显示登录页 -->
    <AdminLogin v-if="!isLoggedIn && isAdminMode" @login-success="handleLoginSuccess" />
    <StudentLogin v-else-if="!isLoggedIn && isStudentMode" @login-success="handleLoginSuccess" />
    <TeacherLogin v-else-if="!isLoggedIn" @login-success="handleLoginSuccess" />

    <!-- 已登录显示管理后台 -->
    <template v-else>
      <!-- Header - 根据角色显示不同主题色 -->
      <!-- 桌面端 -->
      <header :class="['sticky top-0 z-50 border-b hidden lg:block', isStudentMode ? 'bg-blue-50 border-blue-100' : isAdminMode ? 'bg-indigo-50 border-indigo-100' : 'bg-white border-green-100']">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div :class="['p-2 rounded-lg text-white', isStudentMode ? 'bg-blue-600' : isAdminMode ? 'bg-indigo-600' : 'bg-[#2d6a4f]']">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-bold text-slate-800 leading-none">江西樟树中医药职业学院</h1>
              <p :class="['text-xs mt-1 font-medium tracking-widest uppercase', isStudentMode ? 'text-blue-600' : isAdminMode ? 'text-indigo-600' : 'text-green-700']">
                {{ isAdminMode ? '管理端' : isStudentMode ? '学生端' : '教师端' }} v8.5
              </p>
            </div>
          </div>

          <nav class="flex h-full no-scrollbar overflow-x-auto">
            <button
              v-for="item in navItems"
              :key="item.id"
              @click="switchModule(item.id)"
              :class="['px-4 h-full flex items-center gap-2 transition-all whitespace-nowrap',
                currentModule === item.id
                  ? (isStudentMode ? 'nav-active text-blue-600 font-bold' : isAdminMode ? 'nav-active text-indigo-600 font-bold' : 'nav-active text-[#2d6a4f] font-bold')
                  : (isStudentMode ? 'text-slate-500 hover:text-blue-600' : isAdminMode ? 'text-slate-500 hover:text-indigo-600' : 'text-slate-500 hover:text-green-700')]">
              <component :is="item.icon" class="w-4 h-4" />
              {{ item.label }}
            </button>
          </nav>

          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">{{ teacherUser?.name || teacherUser?.student_name || teacherUser?.username }}</span>
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-200 text-[10px] font-black uppercase tracking-tighter">
              <span :class="['w-2 h-2 rounded-full', isOnline ? 'bg-green-500' : 'bg-red-400']"></span>
              <span>{{ isOnline ? '在线' : '离线' }}</span>
            </div>
            <button @click="logout" class="text-slate-400 hover:text-red-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 手机端：顶部紧凑导航条 + 底部 TabBar -->
      <header :class="['sticky top-0 z-50 lg:hidden border-b', isStudentMode ? 'bg-blue-50 border-blue-100' : isAdminMode ? 'bg-indigo-50 border-indigo-100' : 'bg-white border-green-100']">
        <!-- 顶部：标题 + 用户信息 -->
        <div class="flex items-center justify-between px-4 h-14">
          <div class="flex items-center gap-2">
            <div :class="['p-1.5 rounded-lg text-white', isStudentMode ? 'bg-blue-600' : isAdminMode ? 'bg-indigo-600' : 'bg-[#2d6a4f]']">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <span class="text-sm font-bold text-slate-800">{{ isAdminMode ? '管理端' : isStudentMode ? '学生端' : '教师端' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 max-w-[100px] truncate">{{ teacherUser?.name || teacherUser?.student_name || teacherUser?.username }}</span>
            <button @click="logout" class="text-slate-400 hover:text-red-500 p-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
        <!-- 底部 TabBar 导航 -->
        <nav :class="['flex border-t', isStudentMode ? 'border-blue-100 bg-blue-50' : isAdminMode ? 'border-indigo-100 bg-indigo-50' : 'border-green-100 bg-white']" style="padding-bottom: env(safe-area-inset-bottom);">
          <button
            v-for="item in navItems"
            :key="item.id"
            @click="switchModule(item.id)"
            :class="['flex-1 flex flex-col items-center justify-center py-2 gap-1 transition-all',
              currentModule === item.id
                ? (isStudentMode ? 'text-blue-600' : isAdminMode ? 'text-indigo-600' : 'text-[#2d6a4f]')
                : 'text-slate-400']">
            <component :is="item.icon" class="w-5 h-5" />
            <span class="text-[11px] font-medium">{{ item.label }}</span>
          </button>
        </nav>
      </header>

      <!-- Main Content - 懒加载模块 -->
      <main class="max-w-7xl mx-auto w-full p-6 flex-grow overflow-x-hidden">
        <KeepAlive>
          <component 
            :is="currentComponent" 
            :key="currentModule"
            :courses="courses"
            :classes="classes"
            @refresh="loadCoursesAndClasses"
          />
        </KeepAlive>
      </main>

      <!-- 通用弹窗 -->
      <Teleport to="body">
        <div v-if="showModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showModal = false">
          <div class="bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl overflow-y-auto max-h-[90vh]">
            <component
              :is="modalComponent"
              v-bind="modalProps"
              @close="showModal = false"
              @confirm="handleModalConfirm"
            />
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw, defineAsyncComponent } from 'vue'
import TeacherLogin from './components/TeacherLogin.vue'
import AdminLogin from './components/AdminLogin.vue'
import StudentLogin from './components/StudentLogin.vue'
import { getTeacherCourses, getClassStudents } from './api.js'

// 检测模式（通过入口文件设置的全局标记）
const isAdminMode = window.__IS_ADMIN__ === true
const isTeacherMode = window.__IS_TEACHER__ === true
const isStudentMode = window.__IS_STUDENT__ === true

// 懒加载模块
const CoursesModule = defineAsyncComponent(() => import('./components/CoursesModule.vue'))
const AttendanceModule = defineAsyncComponent(() => import('./components/AttendanceModule.vue'))
const AttendanceReportModule = defineAsyncComponent(() => import('./components/AttendanceReportModule.vue'))
const RandomPicker = defineAsyncComponent(() => import('./components/RandomPicker.vue'))
const TeacherHomeworkModule = defineAsyncComponent(() => import('./components/TeacherHomeworkModule.vue'))
const TeacherRankingModule = defineAsyncComponent(() => import('./components/TeacherRankingModule.vue'))
const TeacherResourcesModule = defineAsyncComponent(() => import('./components/TeacherResourcesModule.vue'))
const SettingsModule = defineAsyncComponent(() => import('./components/SettingsModule.vue'))

// 管理端模块
const AdminDashboardModule = defineAsyncComponent(() => import('./components/AdminDashboardModule.vue'))
const AdminClassesModule = defineAsyncComponent(() => import('./components/AdminClassesModule.vue'))
const AdminTeachersModule = defineAsyncComponent(() => import('./components/AdminTeachersModule.vue'))
const AdminStudentsModule = defineAsyncComponent(() => import('./components/AdminStudentsModule.vue'))

// 学生端模块
const StudentHomeModule = defineAsyncComponent(() => import('./components/StudentHomeModule.vue'))
const StudentHomeworkModule = defineAsyncComponent(() => import('./components/StudentHomeworkModule.vue'))
const StudentRankingModule = defineAsyncComponent(() => import('./components/StudentRankingModule.vue'))
const StudentResourcesModule = defineAsyncComponent(() => import('./components/StudentResourcesModule.vue'))




// 登录状态
const isLoggedIn = ref(false)
const teacherUser = ref(null)

// 根据模式决定 sessionStorage 的 key
const tokenKey = isAdminMode ? 'tc_admin_token' : isStudentMode ? 'tc_student_token' : 'tc_token'
const userKey = isAdminMode ? 'tc_admin_user' : isStudentMode ? 'tc_student_user' : 'tc_teacher'

// 初始化登录状态
const savedToken = sessionStorage.getItem(tokenKey)
const savedUser = sessionStorage.getItem(userKey)
if (savedToken && savedUser) {
  isLoggedIn.value = true
  teacherUser.value = JSON.parse(savedUser)
}

const isOnline = ref(navigator.onLine)

// 课程和班级数据
const courses = ref([])
const classes = ref([])

// 加载课程和班级
async function loadCoursesAndClasses() {
  try {
    const res = await getTeacherCourses()
    if (res.data) {
      // API 返回 {courses: [...], terms: [...]} 或直接是课程数组
      const coursesData = Array.isArray(res.data) ? res.data : (res.data?.courses || res.data)
      courses.value = coursesData
      // 从课程中提取所有班级
      const allClasses = []
      for (const course of coursesData) {
        if (course.classes) {
          for (const cls of course.classes) {
            if (!allClasses.find(c => c.id === cls.id)) {
              allClasses.push({
                ...cls,
                students: []
              })
            }
          }
        }
      }
      classes.value = allClasses
      
      // 加载每个班级的学生数据
      for (const cls of allClasses) {
        try {
          const stuRes = await getClassStudents(cls.id)
          if (stuRes.success && stuRes.data) {
            cls.students = stuRes.data
          }
        } catch (e) {
          console.error(`加载班级 ${cls.id} 学生失败`, e)
        }
      }
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

// 导航配置（根据模式切换）
const teacherNavItems = [
  { id: 'courses', label: '课程', component: CoursesModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>' }) },
  { id: 'attendance', label: '考勤', component: AttendanceModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" /></svg>' }) },
  { id: 'attendance_report', label: '考勤报表', component: AttendanceReportModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>' }) },
  { id: 'random', label: '点名', component: RandomPicker, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>' }) },
  { id: 'homework', label: '作业', component: TeacherHomeworkModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>' }) },
  { id: 'ranking', label: '天梯榜', component: TeacherRankingModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' }) },
  { id: 'resources', label: '资源', component: TeacherResourcesModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>' }) },
]

const adminNavItems = [
  { id: 'dashboard', label: '概览', component: AdminDashboardModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>' }) },
  { id: 'classes', label: '班级管理', component: AdminClassesModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>' }) },
  { id: 'teachers', label: '教师管理', component: AdminTeachersModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }) },
  { id: 'students', label: '学生账号', component: AdminStudentsModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }) },
]

const studentNavItems = [
  { id: 'home', label: '首页', component: StudentHomeModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>' }) },
  { id: 'homework', label: '作业', component: StudentHomeworkModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>' }) },
  { id: 'resources', label: '资源', component: StudentResourcesModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>' }) },
  { id: 'ranking', label: '天梯榜', component: StudentRankingModule, icon: markRaw({ template: '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' }) },
]

const navItems = isAdminMode ? adminNavItems : isStudentMode ? studentNavItems : teacherNavItems

// 管理端默认选中的模块
const defaultModule = isAdminMode ? 'dashboard' : isStudentMode ? 'home' : 'courses'
const currentModule = ref(savedToken ? defaultModule : defaultModule)

// 弹窗状态
const showModal = ref(false)
const modalComponent = ref(null)
const modalProps = ref({})

// 当前组件
const currentComponent = computed(() => {
  const item = navItems.find(n => n.id === currentModule.value)
  return item?.component || (isAdminMode ? AdminDashboardModule : isStudentMode ? StudentHomeModule : CoursesModule)
})

// 切换模块
function switchModule(id) {
  currentModule.value = id
}

// 登录成功
function handleLoginSuccess(user) {
  isLoggedIn.value = true
  teacherUser.value = user
  if (!isStudentMode) {
    loadCoursesAndClasses()
  }
}

// 登出
function logout() {
  sessionStorage.removeItem(tokenKey)
  sessionStorage.removeItem(userKey)
  isLoggedIn.value = false
  teacherUser.value = null
}

// 弹窗处理
function openCourseModal(courseData = null) {
  modalComponent.value = markRaw(defineAsyncComponent(() => import('./components/CourseModal.vue')))
  modalProps.value = { courseData }
  showModal.value = true
}

function openScoreModal(student, currentScores) {
  modalComponent.value = markRaw(defineAsyncComponent(() => import('./components/ScoreModal.vue')))
  modalProps.value = { student, scores: currentScores }
  showModal.value = true
}

function handleModalConfirm(data) {
  showModal.value = false
}

// 网络状态监听
window.addEventListener('online', () => isOnline.value = true)
window.addEventListener('offline', () => isOnline.value = false)

// 检查登录状态
onMounted(() => {
  if (isAdminMode) {
    const token = sessionStorage.getItem('tc_admin_token')
    const user = sessionStorage.getItem('tc_admin_user')
    if (token && user) {
      try {
        teacherUser.value = JSON.parse(user)
        isLoggedIn.value = true
      } catch (e) {
        sessionStorage.removeItem('tc_admin_token')
        sessionStorage.removeItem('tc_admin_user')
      }
    }
  } else if (isStudentMode) {
    const token = sessionStorage.getItem('tc_student_token')
    const user = sessionStorage.getItem('tc_student_user')
    if (token && user) {
      try {
        teacherUser.value = JSON.parse(user)
        isLoggedIn.value = true
      } catch (e) {
        sessionStorage.removeItem('tc_student_token')
        sessionStorage.removeItem('tc_student_user')
      }
    }
  } else {
    const token = sessionStorage.getItem('tc_token')
    const user = sessionStorage.getItem('tc_teacher')
    if (token && user) {
      try {
        teacherUser.value = JSON.parse(user)
        isLoggedIn.value = true
        loadCoursesAndClasses()
      } catch (e) {
        sessionStorage.removeItem('tc_token')
        sessionStorage.removeItem('tc_teacher')
      }
    }
  }
})

// 暴露弹窗方法供子组件使用
defineExpose({ openCourseModal, openScoreModal })
</script>
