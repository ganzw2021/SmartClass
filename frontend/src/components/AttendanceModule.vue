<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <!-- 左侧：二维码区域 -->
    <div class="lg:col-span-1 glass-card bg-white p-8 flex flex-col items-center">
      <h3 class="font-bold mb-4 text-slate-700 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        签到二维码
      </h3>

      <!-- 二维码显示区域 -->
      <div :class="[
        'w-full aspect-square max-w-[380px] mx-auto mb-4 rounded-2xl overflow-hidden flex items-center justify-center relative transition-all',
        isAttending
          ? 'bg-white border-4 border-green-500 shadow-lg'
          : 'bg-slate-100 border-4 border-dashed border-slate-300'
      ]">
        <!-- 未开启签到 -->
        <div v-if="!isAttending" class="text-center p-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
          </svg>
          <p class="text-slate-400 text-sm font-medium">开启签到后<br>显示超大二维码</p>
        </div>
        <!-- 开启签到后显示二维码 -->
        <img v-else-if="qrDataUrl" :src="qrDataUrl" class="w-full h-full object-contain p-2" alt="签到二维码" />
        <!-- 加载中 -->
        <div v-else-if="!qrError" class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-green-200 border-t-green-600"></div>
          <span class="text-slate-400 text-sm mt-2">生成中...</span>
        </div>
        <!-- QR 刷新失败提示 -->
        <div v-else class="flex flex-col items-center text-red-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="text-sm mt-2">刷新失败，请检查网络</span>
        </div>
      </div>

      <!-- 签到统计 -->
      <div v-if="isAttending" class="w-full max-w-[300px] mb-4 p-4 bg-green-50 rounded-xl">
        <div class="flex justify-between items-center">
          <span class="text-green-700 font-bold">已签到</span>
          <span class="text-2xl font-black text-green-600">{{ signedCount }} / {{ allStudents.length }}</span>
        </div>
        <div class="w-full h-2 bg-green-200 rounded-full mt-2 overflow-hidden">
          <div class="h-full bg-green-500 transition-all duration-500" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>

      <div class="w-full space-y-4">
        <div class="space-y-3">
          <div>
            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">选择课程</label>
            <select v-model="selectedCourse" @change="onCourseChange" class="w-full border-2 border-slate-50 p-3 rounded-xl outline-none font-bold text-slate-700 bg-slate-50 mt-1 text-sm">
              <option value="">请选择课程</option>
              <option v-for="c in courses" :key="c.id" :value="c.id">[{{ c.term }}] {{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="text-[10px] font-bold uppercase tracking-wider" :class="selectedCourse ? 'text-slate-400' : 'text-slate-300'">授课班级</label>
            <select
              v-model="selectedClass"
              @change="onClassChange"
              :disabled="!selectedCourse"
              class="w-full border-2 border-slate-50 p-3 rounded-xl outline-none font-bold text-slate-700 mt-1 transition-all"
              :class="selectedCourse ? 'bg-slate-50' : 'bg-slate-100 cursor-not-allowed'"
            >
              <option value="">请先选择课程</option>
              <option v-for="c in filteredClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
        </div>
        <button @click="toggleAttendance" class="w-full py-4 btn-green rounded-xl font-bold shadow-lg transition-all active:scale-95 text-base" :class="{ 'bg-red-500 hover:bg-red-600': isAttending }">
          {{ isAttending ? '停止签到' : '开始签到' }}
        </button>
      </div>
    </div>

    <!-- 右侧：待签到名单 -->
    <div class="lg:col-span-2 glass-card bg-white p-8">
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-3">
          <h3 class="font-bold text-slate-700 text-lg">待签到学生</h3>
          <span v-if="unattendedCount > 0" class="bg-red-100 text-red-600 px-4 py-1.5 rounded-full text-lg font-black">
            {{ unattendedCount }}
          </span>
          <span v-else-if="isAttending && allStudents.length > 0 && unattendedCount === 0" class="bg-green-100 text-green-600 px-4 py-1.5 rounded-full text-lg font-black">
            
          </span>
        </div>
        <div v-if="isAttending" class="flex items-center gap-2 text-sm text-green-600 font-bold bg-green-50 px-4 py-2 rounded-full">
          <span class="animate-pulse h-2 w-2 rounded-full bg-green-500"></span>
          实时同步中
        </div>
      </div>

      <!-- 学生名单网格 -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-[480px] overflow-y-auto p-1 no-scrollbar">
        <div v-if="!isAttending" class="col-span-full py-20 text-center text-slate-300 italic">
          请开启签到以显示待签到名单
        </div>
        <div v-else-if="!allStudents.length" class="col-span-full py-20 text-center text-slate-400">
          暂无学生名单
        </div>
        <!-- 未签到学生（只显示未签到的） -->
        <div
          v-for="(student, idx) in unattendStudents"
          :key="'unsigned-' + idx"
          class="bg-white border-2 border-slate-200 p-4 rounded-xl shadow-sm text-slate-700 font-bold text-base cursor-pointer hover:bg-yellow-50 hover:border-yellow-400 hover:shadow-md transition-all active:scale-95"
          @click="handleManualSign(getStudentName(student))"
          title="点击手动签到"
        >
          <div class="flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>{{ getStudentName(student) }}</span>
          </div>
        </div>
      </div>

      <!-- 已签到学生（底部折叠显示） -->
      <div v-if="signedCount > 0 && isAttending" class="mt-6 pt-6 border-t border-slate-100">
        <button @click="showSigned = !showSigned" class="flex items-center gap-2 text-sm text-green-600 font-bold hover:text-green-700">
          <span>已签到 ({{ signedCount }})</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 transition-transform" :class="{ 'rotate-180': showSigned }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div v-if="showSigned" class="mt-3 flex flex-wrap gap-2">
          <span
            v-for="name in displaySignedNames"
            :key="name"
            class="bg-green-100 text-green-700 px-3 py-1.5 rounded-full text-sm font-bold"
          >
            ✓ {{ name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import QRCode from 'qrcode'
import { startAttendance, refreshQRCodeUrl, getCurrentSession, resetAttendance, saveAttendanceReport, getClassStudents, manualSign } from '../api.js'

const props = defineProps({
  classes: { type: Array, default: () => [] },
  courses: { type: Array, default: () => [] }
})

const emit = defineEmits(['sync-complete'])

// 后端地址配置（用于生成二维码 URL）
const BACKEND_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:5000'

// 状态
const selectedCourse = ref('')
const selectedClass = ref('')
const isAttending = ref(false)
const classStudents = ref([])
const showSigned = ref(false)

// 签到相关状态
const currentSessionKey = ref('')
const currentToken = ref('')
const qrDataUrl = ref('')
const signedNames = ref([])
const startedAt = ref(null)

// 保存最后一次签到结果（停止签到后仍显示）
const lastSignedNames = ref([])
const lastAllStudents = ref([])

// 定时器
let qrRefreshTimer = null
let syncTimer = null

// 计算属性
const filteredClasses = computed(() => {
  if (!selectedCourse.value) return []
  const course = props.courses.find(c => c.id === selectedCourse.value)
  return course?.classes || []
})

// 签到中用实时数据，停止签到后用最后一次的结果
const displayStudents = computed(() => {
  if (isAttending.value) return classStudents.value
  return lastAllStudents.value
})

const displaySignedNames = computed(() => {
  if (isAttending.value) return signedNames.value
  return lastSignedNames.value
})

const allStudents = computed(() => displayStudents.value)

const signedCount = computed(() => displaySignedNames.value.length)

const unattendCount = computed(() => {
  return allStudents.value.filter(s => !displaySignedNames.value.includes(getStudentName(s))).length
})

// 只显示未签到的学生
const unattendStudents = computed(() => {
  return allStudents.value.filter(s => !displaySignedNames.value.includes(getStudentName(s)))
})

const progressPercent = computed(() => {
  if (!allStudents.value.length) return 0
  return Math.round((signedCount.value / allStudents.value.length) * 100)
})

function getStudentName(student) {
  return typeof student === 'string' ? student : (student.name || '')
}

function onCourseChange() {
  if (isAttending.value) stopSign()
  selectedClass.value = ''
  classStudents.value = []
  signedNames.value = []
}

async function onClassChange() {
  // 不再选择班级时立即加载，改为点击开始签到时加载
  classStudents.value = []
  signedNames.value = []
}

async function loadClassStudents() {
  if (!selectedClass.value) return
  try {
    const res = await getClassStudents(selectedClass.value)
    classStudents.value = res.data || []
    lastAllStudents.value = [...classStudents.value]  // 保存学生名单
  } catch (e) {
    console.error('加载学生列表失败', e)
    classStudents.value = []
  }
}

// 生成二维码 - 最大化尺寸，最简化
async function generateQRCodeImage(token) {
  try {
    const url = `${BACKEND_BASE}/sign?cid=${selectedCourse.value}&clid=${selectedClass.value}&t=${Date.now()}&token=${token}`
    // 使用低纠错级别 + 充足白色边框，让二维码更简单、更容易扫描
    const dataUrl = await QRCode.toDataURL(url, {
      width: 360,                  // 固定尺寸（显示区域限制）
      margin: 2,                   // 白色边框增加扫描识别率
      errorCorrectionLevel: 'L',   // 低纠错 = 二维码更简单
      color: {
        dark: '#1a1a1a',
        light: '#ffffff'
      }
    })
    qrDataUrl.value = dataUrl
  } catch (e) {
    console.error('生成二维码失败:', e)
  }
}

async function startSign() {
  try {
    const res = await startAttendance(selectedCourse.value, selectedClass.value)
    if (res.success && res.data) {
      currentSessionKey.value = res.data.session_key
      const url = new URL(res.data.qr_url, BACKEND_BASE)
      currentToken.value = url.searchParams.get('token') || ''
      startedAt.value = new Date()
      await generateQRCodeImage(currentToken.value)
      return true
    }
  } catch (e) {
    console.error('开启签到失败', e)
  }
  return false
}

async function stopSign() {
  try {
    await resetAttendance(selectedCourse.value)
  } catch (e) {
    console.warn('重置签到会话失败', e)
  }

  if (currentSessionKey.value) {
    try {
      await saveAttendanceReport({
        course_id: selectedCourse.value,
        class_id: selectedClass.value,
        session_key: currentSessionKey.value,
        started_at: startedAt.value ? startedAt.value.toISOString() : null,
        ended_at: new Date().toISOString()
      })
    } catch (e) {
      console.error('保存考勤报表失败', e)
    }
  }
}

// 1秒刷新二维码
const qrError = ref(false)  // QR 刷新错误标记

async function refreshQR() {
  try {
    const res = await refreshQRCodeUrl(selectedCourse.value, selectedClass.value)
    if (res.success && res.data) {
      const url = new URL(res.data.qr_url, BACKEND_BASE)
      currentToken.value = url.searchParams.get('token') || res.data.token || ''
      currentSessionKey.value = res.data.session_key || currentSessionKey.value
      await generateQRCodeImage(currentToken.value)
      qrError.value = false
    }
  } catch (e) {
    console.error('刷新二维码失败', e)
    qrError.value = true
  }
}

async function syncSignedNames() {
  try {
    const res = await getCurrentSession(selectedCourse.value, selectedClass.value)
    if (res.success && res.data) {
      signedNames.value = res.data.signed_names || []
      lastSignedNames.value = [...signedNames.value]  // 同步保存最后一次结果
      if (res.data.session_key) {
        currentSessionKey.value = res.data.session_key
      }
      emit('sync-complete')
    }
  } catch (e) {
    console.error('同步已签到名单失败', e)
  }
}

async function handleManualSign(studentName) {
  if (!isAttending.value) {
    alert('请先开启签到')
    return
  }
  if (signedNames.value.includes(studentName)) return
  
  try {
    const res = await manualSign(
      selectedCourse.value,
      selectedClass.value,
      studentName,
      currentSessionKey.value
    )
    if (res.success) {
      signedNames.value.push(studentName)
      await syncSignedNames()
    } else {
      alert(res.message || '手动签到失败')
    }
  } catch (e) {
    console.error('手动签到失败', e)
    alert('手动签到失败，请重试')
  }
}

async function toggleAttendance() {
  if (!selectedCourse.value || !selectedClass.value) {
    alert('请先选择有效的课程和班级')
    return
  }

  if (!isAttending.value) {
    // 开始新的签到，清空之前的结果
    lastSignedNames.value = []
    lastAllStudents.value = []
    showSigned.value = false

    // 点击开始签到时才加载班级学生名单
    await loadClassStudents()

    const success = await startSign()
    if (!success) {
      alert('开启签到失败，请重试')
      return
    }

    signedNames.value = []
    isAttending.value = true

    await syncSignedNames()

    // 每1秒刷新二维码
    qrRefreshTimer = setInterval(async () => {
      await refreshQR()
    }, 1000)

    // 3秒同步已签到名单
    syncTimer = setInterval(syncSignedNames, 3000)
  } else {
    // 保存最后一次签到结果
    lastSignedNames.value = [...signedNames.value]
    lastAllStudents.value = [...classStudents.value]

    isAttending.value = false
    clearInterval(qrRefreshTimer)
    clearInterval(syncTimer)
    qrRefreshTimer = null
    syncTimer = null
    await stopSign()
    qrDataUrl.value = ''
    currentSessionKey.value = ''
    currentToken.value = ''
    // 不再清空 signedNames，保留显示
    showSigned.value = true  // 默认展开已签到列表
  }
}

onUnmounted(() => {
  if (isAttending.value) stopSign()
  clearInterval(qrRefreshTimer); qrRefreshTimer = null
  clearInterval(syncTimer); syncTimer = null
})
</script>
