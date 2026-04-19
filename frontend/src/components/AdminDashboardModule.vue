<template>
  <div class="space-y-6">

    <!-- 顶部标题 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-1 h-7 rounded-full bg-gradient-to-b from-blue-500 to-indigo-500"></div>
        <h2 class="text-2xl font-bold text-slate-800">概览</h2>
      </div>
      <div class="text-xs text-slate-400">{{ currentTime }}</div>
    </div>

    <!-- KPI 统计行（可点击跳转） -->
    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
      <div v-for="kpi in kpiCards" :key="kpi.label"
           class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 flex flex-col items-center gap-1 select-none transition-all duration-200"
           :class="kpi.module ? 'cursor-pointer hover:shadow-md hover:-translate-y-0.5' : ''"
           @click="kpi.module && $emit('navigate', kpi.module)">
        <div class="text-3xl font-bold font-mono text-slate-800 tabular-nums">
          <span v-if="animDone">{{ kpi.value }}</span>
          <span v-else class="animating">{{ kpi.display }}</span>
        </div>
        <div class="text-xs text-slate-400 font-medium">{{ kpi.label }}</div>
        <div class="w-8 h-0.5 rounded-full mt-1" :class="kpi.bgClass"></div>
        <div v-if="kpi.module" class="text-[10px] text-slate-300 mt-0.5">点击查看 →</div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- 班级学生人数 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 lg:col-span-2">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">班级学生人数分布</div>
        <div ref="barChart" style="height:280px;"></div>
      </div>

      <!-- 考勤状态 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">考勤状态分布</div>
        <div ref="donutChart" style="height:280px;"></div>
      </div>
    </div>

    <!-- 第二行 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- 作业提交数 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 lg:col-span-2">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">各作业提交人数</div>
        <div ref="hwChart" style="height:280px;"></div>
      </div>

      <!-- 课程作业量 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">课程作业量</div>
        <div ref="polarChart" style="height:280px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAdminDashboard } from '../api.js'

const emit = defineEmits(['navigate'])

const currentTime = ref('')
let timerId = null
function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
}

const animDone = ref(false)
const kpiCards = ref([
  { label: '教 师', key: 'teachers',   value: 0, display: 0, module: 'teachers',            bgClass: 'bg-blue-500' },
  { label: '学 生', key: 'students',  value: 0, display: 0, module: 'students',           bgClass: 'bg-emerald-500' },
  { label: '班 级', key: 'classes',   value: 0, display: 0, module: 'classes',            bgClass: 'bg-purple-500' },
  { label: '课 程', key: 'courses',   value: 0, display: 0, module: null,                bgClass: 'bg-amber-500' },
  { label: '作 业', key: 'homework', value: 0, display: 0, module: 'homework_stats',     bgClass: 'bg-pink-500' },
  { label: '提 交', key: 'submissions', value: 0, display: 0, module: 'homework_stats', bgClass: 'bg-teal-500' },
  { label: '考 勤', key: 'attendance', value: 0, display: 0, module: 'attendance_stats', bgClass: 'bg-sky-500' },
])

const barChart = ref(null)
const donutChart = ref(null)
const hwChart = ref(null)
const polarChart = ref(null)
let charts = []

const lightColors = ['#6366f1','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316','#ec4899']

function initBarChart(data) {
  if (!barChart.value) return
  const ins = echarts.init(barChart.value)
  charts.push(ins)
  const names = data.map(d => d.name)
  const values = data.map(d => d.count)
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 10, bottom: 40 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 40, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(values.length,1) * 100)),
        handleStyle: { color: '#6366f144' }, fillerColor: 'rgba(99,102,241,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 11 } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: {
        color: (p) => new echarts.graphic.LinearGradient(0,0,1,0,[
          { offset: 0, color: lightColors[p.dataIndex % lightColors.length] + '44' },
          { offset: 1, color: lightColors[p.dataIndex % lightColors.length] }
        ]),
        borderRadius: [0, 6, 6, 0]
      },
      label: { show: true, position: 'right', color: '#64748b', fontSize: 11, formatter: '{c} 人' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/><b style="color:#6366f1">${p.value}</b> 人`
    }
  })
}

function initDonutChart(data) {
  if (!donutChart.value) return
  const ins = echarts.init(donutChart.value)
  charts.push(ins)
  const colorMap = { '已签到': '#10b981', '缺勤': '#ef4444', '迟到': '#f59e0b', '请假': '#6366f1' }
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${p.name}<br/><b style="color:${p.color}">${p.value}</b> 人次`
    },
    legend: { orient: 'vertical', right: 0, top: 'middle', textStyle: { color: '#64748b', fontSize: 11 } },
    series: [{
      type: 'pie', radius: ['48%', '70%'], center: ['38%', '50%'],
      data: data.map(d => ({ name: d.name, value: d.value, itemStyle: { color: colorMap[d.name] || '#6366f1' } })),
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(99,102,241,0.2)' } }
    }]
  })
}

function initHwChart(data) {
  if (!hwChart.value) return
  const ins = echarts.init(hwChart.value)
  charts.push(ins)
  const names = data.map(d => d.name)
  const values = data.map(d => d.count)
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 10, bottom: 40 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 40, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(values.length,1) * 100)),
        handleStyle: { color: '#8b5cf644' }, fillerColor: 'rgba(139,92,246,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 10, formatter: v => v.length > 10 ? v.slice(0,10)+'…' : v } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0,0,1,0,[
          { offset: 0, color: '#8b5cf644' }, { offset: 1, color: '#8b5cf6' }]),
        borderRadius: [0, 6, 6, 0]
      },
      label: { show: true, position: 'right', color: '#64748b', fontSize: 11, formatter: '{c} 人' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/><b style="color:#8b5cf6">${p.value}</b> 人`
    }
  })
}

function initPolarChart(data) {
  if (!polarChart.value) return
  const ins = echarts.init(polarChart.value)
  charts.push(ins)
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' } },
    angleAxis: {
      type: 'category',
      data: data.map(d => d.name.length > 8 ? d.name.slice(0,8)+'…' : d.name),
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    radiusAxis: {
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    polar: { radius: '62%', center: ['50%','52%'] },
    series: [{
      type: 'bar', data: data.map(d => d.count),
      coordinateSystem: 'polar', roundCap: true,
      itemStyle: { color: (p) => lightColors[p.dataIndex % lightColors.length], opacity: 0.85 },
      label: { show: true, position: 'middle', color: '#fff', fontSize: 11, formatter: '{c}' }
    }]
  })
}

function animateCounters() {
  const duration = 1200, steps = 40, interval = duration / steps
  let step = 0
  const timer = setInterval(() => {
    step++
    const ease = 1 - Math.pow(1 - step / steps, 3)
    kpiCards.value.forEach(card => { card.display = Math.round(card.value * ease) })
    if (step >= steps) {
      kpiCards.value.forEach(card => { card.display = card.value })
      animDone.value = true
      clearInterval(timer)
    }
  }, interval)
}

function handleResize() { charts.forEach(c => c.resize()) }

onMounted(async () => {
  updateTime()
  timerId = setInterval(updateTime, 1000)
  window.addEventListener('resize', handleResize)
  try {
    const res = await getAdminDashboard()
    const d = res.data
    kpiCards.value.forEach(card => { card.value = d.total[card.key] || 0 })
    animateCounters()
    await nextTick()
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    if (barChart.value)   initBarChart(d.class_students)
    if (donutChart.value) initDonutChart(d.att_dist.length ? d.att_dist : [{ name:'暂无数据', value:1 }])
    if (hwChart.value)    initHwChart(d.hw_submissions)
    if (polarChart.value) initPolarChart(d.course_hw)
  } catch (e) {
    console.error('看板加载失败', e)
  }
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
  charts = []
})
</script>

<style scoped>
.animating { animation: blink .15s steps(1) infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
</style>
