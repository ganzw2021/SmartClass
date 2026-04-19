<template>
  <div class="space-y-5">

    <!-- 标题 + 筛选器 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-1 h-7 rounded-full bg-gradient-to-b from-sky-500 to-emerald-500"></div>
        <h2 class="text-2xl font-bold text-slate-800">考勤统计</h2>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="filterCourse" @change="loadData"
          class="border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400">
          <option value="">全部课程</option>
          <option v-for="c in courseList" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filterClass" @change="loadData"
          class="border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-blue-400">
          <option value="">全部班级</option>
          <option v-for="c in classList" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">数据加载中…</div>

    <template v-else>

      <!-- 考勤列表 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
          <div class="text-sm font-bold text-slate-600">考勤记录列表</div>
          <div class="text-xs text-slate-400">共 {{ tableData.length }} 条记录</div>
        </div>

        <div v-if="tableData.length === 0" class="text-center py-16 text-slate-400 text-sm">暂无考勤数据</div>

        <div v-else class="divide-y divide-slate-50">
          <div v-for="(row, index) in tableData" :key="row.id"
               class="px-5 py-4 flex items-center gap-4 hover:bg-slate-50 transition-colors">
            <!-- 序号 -->
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 text-white flex items-center justify-center text-sm font-bold shrink-0">
              {{ index + 1 }}
            </div>

            <!-- 课程信息 -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-slate-800 truncate">{{ row.course_name }}</div>
              <div class="text-xs text-slate-400 mt-0.5">{{ row.class_name }}</div>
            </div>

            <!-- 考勤数据 -->
            <div class="flex items-center gap-5 text-sm">
              <div class="text-center">
                <div class="text-slate-400 text-xs">总人数</div>
                <div class="font-medium text-slate-600">{{ row.total }}</div>
              </div>
              <div class="text-center">
                <div class="text-slate-400 text-xs">已签到</div>
                <div class="font-medium text-emerald-600">{{ row.signed }}</div>
              </div>
              <div class="text-center">
                <div class="text-slate-400 text-xs">迟到</div>
                <div class="font-medium text-amber-600">{{ row.late }}</div>
              </div>
              <div class="text-center">
                <div class="text-slate-400 text-xs">请假</div>
                <div class="font-medium text-sky-600">{{ row.leave }}</div>
              </div>
              <div class="text-center">
                <div class="text-slate-400 text-xs">缺勤</div>
                <div class="font-medium text-rose-600">{{ row.absent }}</div>
              </div>
            </div>

            <!-- 签到率 -->
            <div class="shrink-0">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold"
                    :class="getRateClass(row.rate)">
                {{ row.rate }}%
              </span>
            </div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminAttendanceStats, getAdminCourseList, getAdminClassList } from '../api.js'

const loading = ref(true)
const filterCourse = ref('')
const filterClass = ref('')
const courseList = ref([])
const classList = ref([])
const tableData = ref([])

function getRateClass(rate) {
  const n = parseFloat(rate)
  if (n >= 90) return 'bg-emerald-50 text-emerald-700'
  if (n >= 70) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

async function loadData() {
  loading.value = true
  try {
    const res = await getAdminAttendanceStats({ course_id: filterCourse.value, class_id: filterClass.value })
    tableData.value = res.data.list || []
  } catch (e) {
    console.error('考勤统计加载失败', e)
  } finally {
    loading.value = false
  }
}

async function loadFilters() {
  try {
    const [cr, cl] = await Promise.all([getAdminCourseList(), getAdminClassList()])
    courseList.value = cr.data || []
    classList.value = cl.data || []
  } catch (e) { console.error('筛选器加载失败', e) }
}

onMounted(async () => {
  await loadFilters()
  await loadData()
})
</script>
