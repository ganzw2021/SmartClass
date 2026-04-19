<template>
  <div class="space-y-6">

    <!-- 标题 + 筛选器 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-1 h-7 rounded-full bg-gradient-to-b from-pink-500 to-purple-500"></div>
        <h2 class="text-2xl font-bold text-slate-800">作业统计</h2>
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

    <!-- 顶部汇总 KPI -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div v-for="kpi in summary" :key="kpi.label"
        class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 flex flex-col items-center gap-1 border-l-4"
        :class="kpi.borderClass">
        <div class="text-3xl font-bold font-mono text-slate-800">{{ kpi.value }}</div>
        <div class="text-xs text-slate-400">{{ kpi.label }}</div>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center py-16 text-slate-400 text-sm">数据加载中…</div>

    <template v-else>

      <!-- 第一行图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- 提交率横向条形 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">各作业提交率（%）</div>
          <div ref="submitRateChart" style="height:300px;"></div>
        </div>
        <!-- 平均分横向条形 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">各作业平均分</div>
          <div ref="avgScoreChart" style="height:300px;"></div>
        </div>
      </div>

      <!-- 第二行图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- 分数段堆叠 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">分数段分布</div>
          <div ref="scoreDistChart" style="height:260px;"></div>
        </div>
        <!-- 班级提交率 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">班级作业提交率对比</div>
          <div ref="classRateChart" style="height:260px;"></div>
        </div>
      </div>

      <!-- 作业明细表格 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">作业明细（共 {{ tableData.length }} 项）</div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-slate-50 border-b border-slate-100">
                <th class="text-left py-3 px-4 text-slate-500 font-medium">作业名称</th>
                <th class="text-left py-3 px-4 text-slate-500 font-medium">班级</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">应交</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">已交</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">提交率</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">平均分</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">最高分</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">最低分</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id"
                class="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td class="py-3 px-4 font-medium text-slate-700">{{ row.title }}</td>
                <td class="py-3 px-4 text-slate-500">{{ row.class_name }}</td>
                <td class="py-3 px-4 text-center text-slate-400">{{ row.total_stu }}</td>
                <td class="py-3 px-4 text-center font-mono text-slate-600">{{ row.sub_cnt }}</td>
                <td class="py-3 px-4 text-center">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                    :class="getRateBadge(row.rate)">{{ row.rate }}%</span>
                </td>
                <td class="py-3 px-4 text-center font-mono text-amber-600">{{ row.avg_score != null ? row.avg_score : '—' }}</td>
                <td class="py-3 px-4 text-center font-mono text-emerald-600">{{ row.max_score != null ? row.max_score : '—' }}</td>
                <td class="py-3 px-4 text-center font-mono text-rose-600">{{ row.min_score != null ? row.min_score : '—' }}</td>
              </tr>
              <tr v-if="tableData.length === 0">
                <td colspan="8" class="py-12 text-center text-slate-400">暂无作业数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAdminHomeworkStats, getAdminCourseList, getAdminClassList } from '../api.js'

const loading = ref(true)
const filterCourse = ref('')
const filterClass = ref('')
const courseList = ref([])
const classList = ref([])
const tableData = ref([])

const summary = ref([
  { label: '作业总数',   value: 0, borderClass: 'border-l-pink-500' },
  { label: '总提交数',   value: 0, borderClass: 'border-l-emerald-500' },
  { label: '平均提交率', value: '0%', borderClass: 'border-l-sky-500' },
  { label: '平均得分',   value: '0',  borderClass: 'border-l-amber-500' },
])

const submitRateChart = ref(null)
const avgScoreChart = ref(null)
const scoreDistChart = ref(null)
const classRateChart = ref(null)
let charts = []

function getRateBadge(rate) {
  const n = parseFloat(rate)
  if (n >= 90) return 'bg-emerald-50 text-emerald-700'
  if (n >= 70) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

function disposeCharts() { charts.forEach(c => c.dispose()); charts = [] }

function initSubmitRateChart(data) {
  if (!submitRateChart.value) return
  const ins = echarts.init(submitRateChart.value)
  charts.push(ins)
  const names = data.map(d => d.title)
  const values = data.map(d => parseFloat(d.rate))
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 10, bottom: 40 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 40, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#ec489944' }, fillerColor: 'rgba(236,72,138,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', max: 100,
      axisLabel: { color: '#94a3b8', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 10, formatter: v => v.length > 8 ? v.slice(0,8)+'…' : v } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 16,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#10b981' : v >= 70 ? '#f59e0b' : '#ef4444'
        return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', color: '#64748b', fontSize: 10, formatter: p => p.value + '%' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/><b style="color:#ec4899">${p.value}%</b>` }
  })
}

function initAvgScoreChart(data) {
  if (!avgScoreChart.value) return
  const ins = echarts.init(avgScoreChart.value)
  charts.push(ins)
  const names = data.map(d => d.title)
  const values = data.map(d => d.avg_score ?? 0)
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 10, bottom: 40 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 40, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#f59e0b44' }, fillerColor: 'rgba(245,158,11,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 10, formatter: v => v.length > 8 ? v.slice(0,8)+'…' : v } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 16,
      itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[
        {offset:0,color:'#f59e0b44'},{offset:1,color:'#f59e0b'}]), borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', color: '#64748b', fontSize: 10,
        formatter: p => p.value > 0 ? p.value.toFixed(1) : '—' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/>平均分 <b style="color:#f59e0b">${p.value.toFixed(1)}</b>` }
  })
}

function initScoreDistChart(data) {
  if (!scoreDistChart.value) return
  const ins = echarts.init(scoreDistChart.value)
  charts.push(ins)
  const names = data.map(d => d.title.length > 8 ? d.title.slice(0,8)+'…' : d.title)
  const segKeys = ['excellent', 'good', 'pass', 'fail']
  const segLabels = ['优秀(90+)', '良好(70-89)', '及格(60-69)', '不及格(<60)']
  const segColors = ['#10b981', '#6366f1', '#f59e0b', '#ef4444']
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' } },
    legend: { data: segLabels, textStyle: { color: '#64748b', fontSize: 10 }, top: 4 },
    grid: { left: 16, right: 16, top: 40, bottom: 50 },
    xAxis: { type: 'category', data: names,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 20 },
      axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false } },
    yAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { show: false } },
    series: segKeys.map((k, i) => ({
      name: segLabels[i], type: 'bar', stack: 'total',
      data: data.map(d => d.dist[k] || 0),
      itemStyle: { color: segColors[i] + 'cc', borderRadius: i === 3 ? [4,4,0,0] : 0 },
      label: { show: false }
    }))
  })
}

function initClassRateChart(data) {
  if (!classRateChart.value) return
  const ins = echarts.init(classRateChart.value)
  charts.push(ins)
  const names = data.map(d => d.name.replace('2025级',''))
  const values = data.map(d => parseFloat(d.rate))
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 16, right: 60, top: 20, bottom: 50 },
    xAxis: { type: 'category', data: names,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 20 },
      axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false } },
    yAxis: { type: 'value', max: 100,
      axisLabel: { color: '#94a3b8', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { show: false } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 32,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#10b981' : v >= 70 ? '#6366f1' : '#f59e0b'
        return new echarts.graphic.LinearGradient(0,1,0,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [4,4,0,0] },
      label: { show: true, position: 'top', color: '#64748b', fontSize: 9, formatter: p => p.value + '%' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/>提交率 <b style="color:#6366f1">${p.value}%</b>` }
  })
}

async function loadData() {
  loading.value = true
  disposeCharts()
  try {
    const res = await getAdminHomeworkStats({ course_id: filterCourse.value, class_id: filterClass.value })
    const d = res.data
    summary.value[0].value = d.total_hw
    summary.value[1].value = d.total_subs
    summary.value[2].value = d.avg_rate + '%'
    summary.value[3].value = d.avg_score
    tableData.value = d.list || []
    await nextTick()
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    initSubmitRateChart(d.list || [])
    initAvgScoreChart(d.list || [])
    initScoreDistChart(d.list || [])
    initClassRateChart(d.class_rates || [])
  } catch (e) {
    console.error('作业统计加载失败', e)
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

function handleResize() { charts.forEach(c => c.resize()) }

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await loadFilters()
  await loadData()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>
