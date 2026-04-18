<template>
  <div class="space-y-6">
    <!-- 学期 / 课程筛选 -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-blue-50">
      <div class="flex flex-wrap gap-4">
        <!-- 学期选择 -->
        <select
          v-model="selectedTerm"
          @change="onTermChange"
          class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none min-w-[160px]"
        >
          <option value="">全部学期</option>
          <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
        </select>

        <!-- 课程选择 -->
        <select
          v-model="selectedCourseId"
          @change="loadRanking"
          :disabled="!selectedTerm || filteredCourses.length === 0"
          class="border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <option value="">请选择课程</option>
          <option v-for="course in filteredCourses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>

      <p v-if="selectedCourseId" class="mt-3 text-sm text-slate-500">
        当前天梯榜：<span class="font-semibold text-slate-700">{{ selectedCourseName }}</span>
      </p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 天梯榜 -->
    <div v-else-if="rankings.length > 0">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-5 text-white shadow-lg">
          <div class="text-3xl font-black">{{ rankings.length }}</div>
          <div class="text-blue-100 text-sm mt-1">天梯总人数</div>
        </div>
        <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg">
          <div class="text-3xl font-black">{{ myRank ? myRank.rank : '-' }}</div>
          <div class="text-purple-100 text-sm mt-1">我的排名</div>
        </div>
        <div class="bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl p-5 text-white shadow-lg">
          <div class="text-3xl font-black">{{ myRank ? myRank.total_score : 0 }}</div>
          <div class="text-amber-100 text-sm mt-1">我的修为</div>
        </div>
      </div>

      <!-- 前三名 -->
      <div v-if="rankings.length >= 3" class="grid grid-cols-3 gap-4 mb-6">
        <!-- 第二名 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 text-center">
          <div class="text-4xl mb-2">&#127942;</div>
          <p class="font-bold text-slate-700">{{ rankings[1].student_name }}</p>
          <p class="text-lg font-black text-slate-600">{{ rankings[1].total_score }}分</p>
          <div class="mt-1 text-sm text-slate-500">
            当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[1].total_score) }">{{ getRankTitle(rankings[1].total_score) }}</span>
          </div>
        </div>
        <!-- 第一名 -->
        <div class="bg-gradient-to-b from-amber-50 to-white rounded-2xl shadow-lg border border-amber-100 p-5 text-center -mt-4">
          <div class="text-5xl mb-2">&#128081;</div>
          <p class="font-bold text-amber-600">{{ rankings[0].student_name }}</p>
          <p class="text-xl font-black text-amber-500">{{ rankings[0].total_score }}分</p>
          <div class="mt-1 text-sm text-slate-500">
            当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[0].total_score) }">{{ getRankTitle(rankings[0].total_score) }}</span>
          </div>
        </div>
        <!-- 第三名 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 text-center">
          <div class="text-4xl mb-2">&#127941;</div>
          <p class="font-bold text-slate-700">{{ rankings[2].student_name }}</p>
          <p class="text-lg font-black text-orange-400">{{ rankings[2].total_score }}分</p>
          <div class="mt-1 text-sm text-slate-500">
            当前修为：<span class="font-bold" :style="{ color: getRankColor(rankings[2].total_score) }">{{ getRankTitle(rankings[2].total_score) }}</span>
          </div>
        </div>
      </div>

      <!-- 天梯列表 -->
      <div class="bg-white rounded-2xl shadow-sm border border-blue-50 overflow-hidden">
        <div class="p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <h3 class="font-bold text-lg flex items-center gap-2">
            <span>&#127942;</span> 天梯榜
          </h3>
        </div>
        <div class="divide-y divide-slate-100">
          <div
            v-for="(item, idx) in rankings"
            :key="item.student_id"
            :class="['flex items-center justify-between p-4 transition-colors', isMe(item) ? 'bg-blue-50' : 'hover:bg-slate-50']"
          >
            <div class="flex items-center gap-4">
              <div v-if="idx < 3" :class="['w-10 h-10 rounded-full flex items-center justify-center text-lg font-black',
                idx === 0 ? 'bg-amber-400 text-white' :
                idx === 1 ? 'bg-slate-300 text-white' :
                'bg-orange-400 text-white']">
                {{ idx === 0 ? '&#128081;' : idx === 1 ? '&#127942;' : '&#127941;' }}
              </div>
              <div v-else :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-black',
                isMe(item) ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-500']">
                {{ idx + 1 }}
              </div>
              <div>
                <p class="font-bold text-slate-800">
                  {{ item.student_name }}
                  <span v-if="isMe(item)" class="ml-1 text-xs text-blue-600 font-normal">(我)</span>
                </p>
                <p class="text-xs text-slate-400">{{ item.homework_count }}次作业</p>
              </div>
            </div>
            <div class="text-right">
              <p :class="['text-lg font-black', getRankTextColor(idx)]">{{ item.total_score }}</p>
              <p class="text-xs" :style="{ color: getRankColor(item.total_score) }">{{ getRankTitle(item.total_score) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div v-else-if="selectedCourseId" class="bg-white rounded-2xl p-8 text-center text-slate-400">
      <div class="text-4xl mb-2">&#128202;</div>
      <p>该课程暂无天梯数据</p>
    </div>

    <div v-else class="text-center text-slate-400 py-12">
      请选择学期和课程查看天梯榜
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStudentRanking, getStudentCourses } from '../api.js'

const user = ref(JSON.parse(sessionStorage.getItem('tc_student_user') || '{}'))
const courses = ref([])
const terms = ref([])
const rankings = ref([])
const selectedTerm = ref('')
const selectedCourseId = ref('')
const loading = ref(false)

const myRank = computed(() => rankings.value.find(r => r.student_id === user.value?.id) || null)

const filteredCourses = computed(() => {
  if (!selectedTerm.value) return courses.value
  return courses.value.filter(c => c.term === selectedTerm.value)
})

const selectedCourseName = computed(() => {
  const c = courses.value.find(x => x.id === selectedCourseId.value)
  return c ? c.name : ''
})

function isMe(item) {
  return item.student_id === user.value?.id
}

function onTermChange() {
  selectedCourseId.value = ''
  rankings.value = []
}

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

function getRankTextColor(idx) {
  if (idx === 0) return 'text-amber-500'
  if (idx === 1) return 'text-slate-500'
  if (idx === 2) return 'text-orange-400'
  return 'text-slate-600'
}

async function loadCourses() {
  try {
    const res = await getStudentCourses()
    if (res.success) {
      if (res.data && res.data.courses) {
        courses.value = res.data.courses || []
        terms.value = res.data.terms || []
      } else if (Array.isArray(res.data)) {
        courses.value = res.data || []
        // 从课程中提取学期
        const termSet = new Set()
        courses.value.forEach(c => { if (c.term) termSet.add(c.term) })
        terms.value = [...termSet].sort().reverse()
      }
      // 默认选最新学期
      if (terms.value.length > 0) {
        selectedTerm.value = terms.value[0]
      }
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

async function loadRanking() {
  if (!selectedCourseId.value) {
    rankings.value = []
    return
  }
  loading.value = true
  try {
    const res = await getStudentRanking(selectedCourseId.value, selectedTerm.value)
    if (res.success) rankings.value = res.data?.rankings || []
    else rankings.value = []
  } catch (e) {
    rankings.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadCourses()
})
</script>
