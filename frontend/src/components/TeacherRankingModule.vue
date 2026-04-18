<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-slate-800">天梯榜</h2>
    </div>

    <!-- 学期 / 课程 / 班级 筛选 -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
      <div class="flex flex-wrap gap-4">
        <!-- 学期选择 -->
        <select
          v-model="selectedTerm"
          @change="onTermChange"
          class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-[#2d6a4f] focus:ring-2 focus:ring-[#2d6a4f]/20 outline-none min-w-[160px]"
        >
          <option value="">全部学期</option>
          <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
        </select>

        <!-- 课程选择 -->
        <select
          v-model="selectedCourseId"
          @change="onCourseChange"
          :disabled="!selectedTerm || filteredCourses.length === 0"
          class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-[#2d6a4f] focus:ring-2 focus:ring-[#d6a4f]/20 outline-none min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option value="">请选择课程</option>
          <option v-for="course in filteredCourses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>

        <!-- 班级选择 -->
        <select
          v-model="selectedClassId"
          @change="loadRanking"
          :disabled="!selectedCourseId || filteredClasses.length === 0"
          class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-[#2d6a4f] focus:ring-2 focus:ring-[#2d6a4f]/20 outline-none min-w-[180px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option value="">请选择班级</option>
          <option v-for="cls in filteredClasses" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
      </div>

      <!-- 提示：选了什么 -->
      <p v-if="selectedCourseId && selectedClassId" class="mt-3 text-sm text-slate-500">
        当前天梯榜：<span class="font-semibold text-slate-700">{{ selectedCourseName }}</span>
        × <span class="font-semibold text-slate-700">{{ selectedClassName }}</span>
      </p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-[#2d6a4f] border-t-transparent rounded-full"></div>
    </div>

    <!-- 天梯榜统计 -->
    <div v-else-if="rankings.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl p-5 text-white shadow-lg">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <div>
            <p class="text-white/80 text-sm">最高分</p>
            <p class="text-2xl font-black">{{ maxScore }}分</p>
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl p-5 text-white shadow-lg">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p class="text-white/80 text-sm">上榜人数</p>
            <p class="text-2xl font-black">{{ rankings.length }}人</p>
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-violet-400 to-purple-500 rounded-2xl p-5 text-white shadow-lg">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <p class="text-white/80 text-sm">平均分</p>
            <p class="text-2xl font-black">{{ avgScore }}分</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 天梯榜列表 -->
    <div v-else-if="selectedClassId" class="bg-white rounded-2xl p-8 text-center text-slate-400">
      暂无天梯榜数据
    </div>

    <div v-else class="text-center text-slate-400 py-12">
      请依次选择学期、课程、班级查看天梯榜
    </div>

    <!-- 排行榜 -->
    <div v-if="rankings.length > 0" class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-[#2d6a4f] to-emerald-600 text-white">
        <h3 class="font-bold text-lg flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          天梯排行榜
        </h3>
      </div>

      <!-- 前三名特别展示 -->
      <div v-if="rankings.length >= 3" class="p-6 bg-gradient-to-b from-slate-50 to-white">
        <div class="flex items-end justify-center gap-4">
          <!-- 第二名 -->
          <div class="text-center flex-1">
            <div class="w-16 h-16 mx-auto bg-gradient-to-br from-slate-300 to-slate-400 rounded-full flex items-center justify-center text-white text-2xl font-black shadow-lg mb-2">
              {{ rankings[1].student_name?.charAt(0) || '?' }}
            </div>
            <div class="w-12 h-8 mx-auto bg-slate-300 rounded-t-lg flex items-center justify-center">
              <span class="text-lg">&#127942;</span>
            </div>
            <p class="font-bold text-slate-700 mt-1">{{ rankings[1].student_name }}</p>
            <p class="text-sm text-slate-500">{{ rankings[1].total_score }}分</p>
            <div class="mt-1 text-xs text-slate-500">
              当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[1].total_score) }">{{ getRankTitle(rankings[1].total_score) }}</span>
            </div>
          </div>
          <!-- 第一名 -->
          <div class="text-center flex-1">
            <div class="w-20 h-20 mx-auto bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-xl mb-2 ring-4 ring-amber-200">
              {{ rankings[0].student_name?.charAt(0) || '?' }}
            </div>
            <div class="w-16 h-10 mx-auto bg-gradient-to-b from-amber-400 to-orange-500 rounded-t-lg flex items-center justify-center">
              <span class="text-2xl">&#128081;</span>
            </div>
            <p class="font-bold text-amber-600 mt-1">{{ rankings[0].student_name }}</p>
            <p class="text-lg font-black text-amber-600">{{ rankings[0].total_score }}分</p>
            <div class="mt-1 text-sm text-slate-500">
              当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[0].total_score) }">{{ getRankTitle(rankings[0].total_score) }}</span>
            </div>
          </div>
          <!-- 第三名 -->
          <div class="text-center flex-1">
            <div class="w-16 h-16 mx-auto bg-gradient-to-br from-orange-300 to-orange-400 rounded-full flex items-center justify-center text-white text-2xl font-black shadow-lg mb-2">
              {{ rankings[2].student_name?.charAt(0) || '?' }}
            </div>
            <div class="w-12 h-8 mx-auto bg-orange-300 rounded-t-lg flex items-center justify-center">
              <span class="text-lg">&#127941;</span>
            </div>
            <p class="font-bold text-slate-700 mt-1">{{ rankings[2].student_name }}</p>
            <p class="text-sm text-slate-500">{{ rankings[2].total_score }}分</p>
            <div class="mt-1 text-xs text-slate-500">
              当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[2].total_score) }">{{ getRankTitle(rankings[2].total_score) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 完整排名列表 -->
      <div class="divide-y divide-slate-100">
        <div
          v-for="(item, idx) in rankings"
          :key="item.student_id"
          class="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-sm font-black',
              idx === 0 ? 'bg-amber-100 text-amber-600' :
              idx === 1 ? 'bg-slate-100 text-slate-600' :
              idx === 2 ? 'bg-orange-100 text-orange-600' :
              'bg-slate-50 text-slate-500']">
              {{ idx + 1 }}
            </div>
            <div>
              <p class="font-bold text-slate-800">{{ item.student_name }}</p>
              <p class="text-xs text-slate-400">作业数：{{ item.homework_count }}</p>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <div class="text-sm text-slate-500">
              当前修为：<span class="font-bold" :style="{ color: getRankColor(item.total_score) }">{{ getRankTitle(item.total_score) }}</span>
            </div>
            <span :class="['text-xl font-black',
              idx === 0 ? 'text-amber-500' :
              idx === 1 ? 'text-slate-500' :
              idx === 2 ? 'text-orange-400' :
              'text-slate-600']">
              {{ item.total_score }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getClassRanking, getTeacherCourses } from '../api.js'

const props = defineProps({
  classes: { type: Array, default: () => [] }
})

const teacherCourses = ref([])
const terms = ref([])
const selectedTerm = ref('')
const selectedCourseId = ref('')
const selectedClassId = ref('')
const rankings = ref([])
const loading = ref(false)

// 过滤后的课程（根据选中的学期）
const filteredCourses = computed(() => {
  if (!selectedTerm.value) return teacherCourses.value
  return teacherCourses.value.filter(c => c.term === selectedTerm.value)
})

// 过滤后的班级（根据选中的课程）
const filteredClasses = computed(() => {
  if (!selectedCourseId.value) return []
  const course = teacherCourses.value.find(c => c.id === selectedCourseId.value)
  if (!course || !course.classes) return []
  const classIds = course.classes.map(cls => cls.id)
  return props.classes.filter(cls => classIds.includes(cls.id))
})

// 当前选中课程的名称
const selectedCourseName = computed(() => {
  const c = teacherCourses.value.find(x => x.id === selectedCourseId.value)
  return c ? c.name : ''
})

// 当前选中班级的中文名
const selectedClassName = computed(() => {
  const cls = props.classes.find(x => x.id === selectedClassId.value)
  return cls ? cls.name : ''
})

// 学期变更时：清空课程和班级
function onTermChange() {
  selectedCourseId.value = ''
  selectedClassId.value = ''
  rankings.value = []
}

// 课程变更时：清空班级和排名
function onCourseChange() {
  selectedClassId.value = ''
  rankings.value = []
}

// 获取修为称号
function getRankTitle(score) {
  if (score >= 1300) return '红尘仙'
  if (score >= 1200) return '仙帝'
  if (score >= 1100) return '仙皇'
  if (score >= 1000) return '仙王'
  if (score >= 900) return '仙人'
  if (score >= 800) return '碎虚'
  if (score >= 700) return '炼虚'
  if (score >= 600) return '化神'
  if (score >= 500) return '元婴'
  if (score >= 400) return '金丹'
  if (score >= 300) return '筑基'
  if (score >= 200) return '练气'
  if (score >= 100) return '淬体'
  return '凡人'
}

// 获取修为文字颜色
function getRankColor(score) {
  if (score >= 1300) return '#dc2626'
  if (score >= 1200) return '#ea580c'
  if (score >= 1100) return '#d946ef'
  if (score >= 1000) return '#9333ea'
  if (score >= 900) return '#8b5cf6'
  if (score >= 800) return '#6366f1'
  if (score >= 700) return '#0ea5e9'
  if (score >= 600) return '#06b6d4'
  if (score >= 500) return '#14b8a6'
  if (score >= 400) return '#22c55e'
  if (score >= 300) return '#eab308'
  if (score >= 200) return '#f97316'
  if (score >= 100) return '#78716c'
  return '#9ca3af'
}

// 计算属性
const maxScore = computed(() => {
  if (rankings.value.length === 0) return 0
  return Math.max(...rankings.value.map(r => r.total_score || 0))
})

const avgScore = computed(() => {
  if (rankings.value.length === 0) return 0
  const sum = rankings.value.reduce((acc, r) => acc + (r.total_score || 0), 0)
  return Math.round(sum / rankings.value.length)
})

// 加载天梯榜
async function loadRanking() {
  if (!selectedCourseId.value || !selectedClassId.value) {
    rankings.value = []
    return
  }

  loading.value = true
  try {
    const res = await getClassRanking(selectedCourseId.value, selectedClassId.value)
    if (res.success) {
      rankings.value = res.data || []
    } else {
      rankings.value = []
    }
  } catch (e) {
    console.error('加载天梯榜失败', e)
    rankings.value = []
  } finally {
    loading.value = false
  }
}

// 加载课程列表（首次加载所有数据）
async function loadCourses() {
  try {
    const res = await getTeacherCourses()
    if (res.success) {
      // API 返回 {courses: [...], terms: [...]} 或直接是课程数组
      if (Array.isArray(res.data)) {
        teacherCourses.value = res.data
      } else {
        teacherCourses.value = res.data.courses || []
        terms.value = res.data.terms || []
      }
      // 如果有 terms 且没选过学期，默认选最新学期
      if (terms.value.length > 0 && !selectedTerm.value) {
        selectedTerm.value = terms.value[0]
      }
    }
  } catch (e) {
    console.error('加载课程列表失败', e)
  }
}

onMounted(() => {
  loadCourses()
})
</script>
