<template>
  <div class="dashboard-root min-h-screen p-4 lg:p-6 -mx-6 -mt-6 -mb-6" style="background: #070d1a;">

    <!-- 顶部标题栏 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-1 h-8 rounded-full" style="background: linear-gradient(180deg,#00f0ff,#0066ff);"></div>
        <div>
          <h1 class="text-xl font-bold tracking-widest" style="color:#e0f4ff;letter-spacing:4px;">智 慧 课 堂 · 数 据 看 板</h1>
          <p class="text-xs mt-0.5" style="color:#3a6080;">SMART CLASSROOM DASHBOARD  ·  管理员视角</p>
        </div>
      </div>
      <div class="text-right">
        <p class="text-xs" style="color:#3a6080;">系统版本 v8.5</p>
        <p class="text-xs font-mono" style="color:#0af;">{{ currentTime }}</p>
      </div>
    </div>

    <!-- KPI 统计卡片行 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
      <div v-for="kpi in kpiCards" :key="kpi.label"
           class="kpi-card rounded-xl p-3 flex flex-col items-center justify-center gap-1 cursor-default select-none"
           :style="`border-color:${kpi.color}44; background: linear-gradient(135deg, ${kpi.color}12, ${kpi.color}06);`">
        <div class="text-3xl font-bold font-mono tabular-nums counter" :style="`color:${kpi.color}; text-shadow: 0 0 12px ${kpi.color}66;`">
          <span v-if="animDone">{{ kpi.value }}</span>
          <span v-else class="animating">{{ kpi.display }}</span>
        </div>
        <div class="text-xs tracking-widest" style="color:#4a7090;">{{ kpi.label }}</div>
        <div class="w-8 h-0.5 rounded-full mt-1" :style="`background:${kpi.color}88;`"></div>
      </div>
    </div>

    <!-- 主图表区 (3列) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
      <!-- 班级学生人数 - 横向条形图 -->
      <div class="chart-panel rounded-2xl p-4 lg:col-span-2">
        <div class="panel-title">班级学生人数分布</div>
        <div ref="barChart" style="height:260px;"></div>
      </div>

      <!-- 考勤状态 - 环形图 -->
      <div class="chart-panel rounded-2xl p-4">
        <div class="panel-title">考勤状态分布</div>
        <div ref="donutChart" style="height:260px;"></div>
      </div>
    </div>

    <!-- 第二行图表 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
      <!-- 作业提交数 - 柱状图 -->
      <div class="chart-panel rounded-2xl p-4 lg:col-span-2">
        <div class="panel-title">各作业提交人数</div>
        <div ref="hwChart" style="height:220px;"></div>
      </div>

      <!-- 课程作业量 - 极坐标 -->
      <div class="chart-panel rounded-2xl p-4">
        <div class="panel-title">课程作业量</div>
        <div ref="polarChart" style="height:220px;"></div>
      </div>
    </div>

    <!-- 快捷导航行 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <a v-for="nav in navItems" :key="nav.label"
         :href="`?module=${nav.module}`"
         class="nav-card rounded-xl px-5 py-4 flex items-center gap-4 no-underline group"
         :style="`border-color:${nav.color}33;`">
        <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-all group-hover:scale-110"
             :style="`background:${nav.color}22; border:1px solid ${nav.color}44;`">
          <span class="text-xl">{{ nav.icon }}</span>
        </div>
        <div>
          <p class="font-semibold text-sm" :style="`color:${nav.color};`">{{ nav.label }}</p>
          <p class="text-xs" style="color:#3a5070;">{{ nav.desc }}</p>
        </div>
        <svg class="ml-auto w-4 h-4 opacity-40 group-hover:opacity-80 transition-opacity" :style="`color:${nav.color};`" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </a>
    </div>

    <!-- 扫描线装饰 -->
    <div class="scan-line pointer-events-none"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAdminDashboard } from '../api.js'

// ─── 时间 ───────────────────────────────────────────
const currentTime = ref('')
let timerId = null
function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
}

// ─── 数据 ───────────────────────────────────────────
const dashData = ref(null)
const animDone = ref(false)

const kpiCards = ref([
  { label: '教 师', value: 0, display: 0, color: '#00c8ff', key: 'teachers' },
  { label: '学 生', value: 0, display: 0, color: '#00ff9d', key: 'students' },
  { label: '班 级', value: 0, display: 0, color: '#a78bfa', key: 'classes' },
  { label: '课 程', value: 0, display: 0, color: '#f59e0b', key: 'courses' },
  { label: '作 业', value: 0, display: 0, color: '#f472b6', key: 'homework' },
  { label: '提 交', value: 0, display: 0, color: '#34d399', key: 'submissions' },
  { label: '考 勤', value: 0, display: 0, color: '#60a5fa', key: 'attendance' },
])

const navItems = [
  { label: '班级管理', module: 'classes', icon: '🏫', color: '#a78bfa', desc: '查看/编辑班级和学生' },
  { label: '教师管理', module: 'teachers', icon: '👨‍🏫', color: '#00c8ff', desc: '添加/编辑/删除教师账号' },
  { label: '学生账号', module: 'students', icon: '🎓', color: '#00ff9d', desc: '批量创建账号/重置密码' },
]

// ─── 图表 refs ───────────────────────────────────────
const barChart = ref(null)
const donutChart = ref(null)
const hwChart = ref(null)
const polarChart = ref(null)
let charts = []

// 通用科技风主题色
const techColors = ['#00c8ff','#00ff9d','#a78bfa','#f59e0b','#f472b6','#34d399','#60a5fa','#fb923c','#e879f9','#4ade80']

function initBarChart(data) {
  if (!barChart.value) return
  const ins = echarts.init(barChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.name.replace('2025级','').replace('班',''))
  const values = data.map(d => d.count)
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 120, right: 20, top: 12, bottom: 24 },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#1a3050' } },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } },
      axisLabel: { color: '#3a6080', fontSize: 11 }
    },
    yAxis: {
      type: 'category', data: names,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: values,
      barMaxWidth: 18,
      itemStyle: {
        color: (p) => {
          const grad = new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: techColors[p.dataIndex % techColors.length] + '44' },
            { offset: 1, color: techColors[p.dataIndex % techColors.length] }
          ])
          return grad
        },
        borderRadius: [0, 6, 6, 0]
      },
      label: {
        show: true, position: 'right', color: '#7ab4d4', fontSize: 11,
        formatter: '{c} 人'
      }
    }],
    tooltip: {
      backgroundColor: '#0a1929', borderColor: '#00c8ff44',
      textStyle: { color: '#c0e8ff' },
      formatter: p => `${data[p.dataIndex].name}<br/><b style="color:#00ff9d">${p.value}</b> 人`
    }
  })
}

function initDonutChart(data) {
  if (!donutChart.value) return
  const ins = echarts.init(donutChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const colors = { '已签到': '#00ff9d', '缺勤': '#f472b6', '迟到': '#f59e0b', '请假': '#60a5fa' }
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#0a1929', borderColor: '#00c8ff44',
      textStyle: { color: '#c0e8ff' },
      formatter: p => `${p.name}<br/><b style="color:${p.color}">${p.value}</b> 人`
    },
    legend: {
      orient: 'vertical', right: 0, top: 'middle',
      textStyle: { color: '#7ab4d4', fontSize: 11 }
    },
    series: [{
      type: 'pie', radius: ['48%', '70%'],
      center: ['38%', '50%'],
      data: data.map(d => ({
        name: d.name, value: d.value,
        itemStyle: { color: colors[d.name] || techColors[0] }
      })),
      label: { show: false },
      emphasis: {
        itemStyle: { shadowBlur: 16, shadowColor: 'rgba(0,200,255,0.4)' }
      }
    }]
  })
}

function initHwChart(data) {
  if (!hwChart.value) return
  const ins = echarts.init(hwChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 24, right: 16, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name.length > 8 ? d.name.slice(0,8)+'…' : d.name),
      axisLabel: { color: '#3a6080', fontSize: 10, rotate: 25 },
      axisLine: { lineStyle: { color: '#1a3050' } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#3a6080', fontSize: 11 },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } },
      axisLine: { show: false }
    },
    series: [{
      type: 'bar', data: data.map(d => d.count),
      barMaxWidth: 32,
      itemStyle: {
        color: (p) => new echarts.graphic.LinearGradient(0, 1, 0, 0, [
          { offset: 0, color: '#0066ff44' },
          { offset: 1, color: '#00c8ff' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', color: '#7ab4d4', fontSize: 10 }
    }],
    tooltip: {
      backgroundColor: '#0a1929', borderColor: '#00c8ff44',
      textStyle: { color: '#c0e8ff' }
    }
  })
}

function initPolarChart(data) {
  if (!polarChart.value) return
  const ins = echarts.init(polarChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#0a1929', borderColor: '#00c8ff44',
      textStyle: { color: '#c0e8ff' }
    },
    angleAxis: {
      type: 'category',
      data: data.map(d => d.name.length > 10 ? d.name.slice(0,10)+'…' : d.name),
      axisLabel: { color: '#7ab4d4', fontSize: 10 }
    },
    radiusAxis: {
      axisLabel: { color: '#3a6080', fontSize: 10 },
      splitLine: { lineStyle: { color: '#0d2035' } }
    },
    polar: { radius: '60%', center: ['50%', '52%'] },
    series: [{
      type: 'bar', data: data.map(d => d.count),
      coordinateSystem: 'polar',
      roundCap: true,
      itemStyle: {
        color: (p) => techColors[p.dataIndex % techColors.length],
        opacity: 0.85
      },
      label: { show: true, position: 'middle', color: '#fff', fontSize: 11, formatter: '{c}' }
    }]
  })
}

// ─── 数字滚动动画 ─────────────────────────────────────
function animateCounters(targets) {
  const duration = 1400
  const steps = 40
  const interval = duration / steps
  let step = 0
  const timer = setInterval(() => {
    step++
    const progress = step / steps
    const ease = 1 - Math.pow(1 - progress, 3)
    kpiCards.value.forEach(card => {
      card.display = Math.round(card.value * ease)
    })
    if (step >= steps) {
      kpiCards.value.forEach(card => { card.display = card.value })
      animDone.value = true
      clearInterval(timer)
    }
  }, interval)
}

// ─── 窗口 resize ────────────────────────────────────
function handleResize() {
  charts.forEach(c => c.resize())
}

// ─── 生命周期 ────────────────────────────────────────
onMounted(async () => {
  updateTime()
  timerId = setInterval(updateTime, 1000)
  window.addEventListener('resize', handleResize)

  try {
    const res = await getAdminDashboard()
    const d = res.data
    dashData.value = d

    // 填充 KPI
    kpiCards.value.forEach(card => {
      card.value = d.total[card.key] || 0
    })
    animateCounters()

    // 等 DOM 更新 + 浏览器绘制完成再初始化图表
    await nextTick()
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
    if (barChart.value)   initBarChart(d.class_students)
    if (donutChart.value) initDonutChart(d.att_dist.length ? d.att_dist : [{ name: '暂无数据', value: 1 }])
    if (hwChart.value)    initHwChart(d.hw_submissions)
    if (polarChart.value) initPolarChart(d.course_hw)
  } catch (e) {
    console.error('看板数据加载失败', e)
    // 降级：使用 stats 接口
    try {
      const { getAdminStats } = await import('../api.js')
      const res2 = await getAdminStats()
      if (res2.data) {
        const s = res2.data
        kpiCards.value.forEach(card => {
          if (s[card.key] !== undefined) card.value = s[card.key]
        })
        animateCounters()
      }
    } catch (_) {}
  }
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.dashboard-root {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  position: relative;
  overflow: hidden;
}

.kpi-card {
  border: 1px solid;
  transition: transform .2s, box-shadow .2s;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,200,255,0.1);
}

.chart-panel {
  background: linear-gradient(135deg, #0a1929 0%, #070f1e 100%);
  border: 1px solid #0d2540;
  position: relative;
  overflow: hidden;
}
.chart-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at top left, rgba(0,200,255,0.04), transparent 60%);
  pointer-events: none;
}

.panel-title {
  font-size: 12px;
  letter-spacing: 2px;
  color: #4a90b8;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #0d2540;
  text-transform: uppercase;
}

.nav-card {
  background: linear-gradient(135deg, #0a1929 0%, #070f1e 100%);
  border: 1px solid;
  transition: transform .2s, box-shadow .2s;
}
.nav-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,100,200,0.15);
}

/* 扫描线 */
@keyframes scan {
  0%   { top: -2px; opacity: .6; }
  100% { top: 100%; opacity: 0; }
}
.scan-line {
  position: fixed;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0,200,255,0.4), transparent);
  animation: scan 6s linear infinite;
}

/* 数字跳动 */
@keyframes digit-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: .4; }
}
.animating { animation: digit-blink .15s steps(1) infinite; }
</style>
