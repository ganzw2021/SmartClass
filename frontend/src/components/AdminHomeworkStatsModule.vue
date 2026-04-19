<template>
  <div class="hw-stats min-h-screen p-4 lg:p-6 -mx-6 -mt-6 -mb-6" style="background:#070d1a;">

    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-1 h-8 rounded-full" style="background:linear-gradient(180deg,#f472b6,#a78bfa);"></div>
        <div>
          <h1 class="text-xl font-bold tracking-widest" style="color:#e0f4ff;letter-spacing:4px;">作 业 统 计</h1>
          <p class="text-xs mt-0.5" style="color:#3a6080;">HOMEWORK STATISTICS · 管理员视角</p>
        </div>
      </div>
      <!-- 筛选器 -->
      <div class="flex items-center gap-2">
        <select v-model="filterCourse" @change="loadData"
          class="text-xs rounded-lg px-3 py-1.5 border outline-none"
          style="background:#0a1929;color:#7ab4d4;border-color:#0d2540;">
          <option value="">全部课程</option>
          <option v-for="c in courseList" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filterClass" @change="loadData"
          class="text-xs rounded-lg px-3 py-1.5 border outline-none"
          style="background:#0a1929;color:#7ab4d4;border-color:#0d2540;">
          <option value="">全部班级</option>
          <option v-for="c in classList" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <!-- 顶部汇总 KPI -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
      <div v-for="kpi in summary" :key="kpi.label"
        class="rounded-xl p-4 flex flex-col items-center gap-1 border"
        :style="`border-color:${kpi.color}44;background:linear-gradient(135deg,${kpi.color}12,${kpi.color}06);`">
        <div class="text-3xl font-bold font-mono" :style="`color:${kpi.color};text-shadow:0 0 10px ${kpi.color}66;`">{{ kpi.value }}</div>
        <div class="text-xs tracking-widest" style="color:#4a7090;">{{ kpi.label }}</div>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-sm" style="color:#3a6080;">数据加载中…</div>
    </div>

    <template v-else>
      <!-- 第一行：提交率 + 平均分 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <!-- 作业提交率横向条形图 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">各作业提交率（%）</div>
          <div ref="submitRateChart" style="height:320px;"></div>
        </div>
        <!-- 作业平均分横向条形图 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">各作业平均分</div>
          <div ref="avgScoreChart" style="height:320px;"></div>
        </div>
      </div>

      <!-- 第二行：分数段分布 + 提交人数柱状图 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <!-- 分数段分布堆叠图 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">分数段分布</div>
          <div ref="scoreDistChart" style="height:280px;"></div>
        </div>
        <!-- 班级提交率对比 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">班级作业提交率对比（%）</div>
          <div ref="classRateChart" style="height:280px;"></div>
        </div>
      </div>

      <!-- 作业明细表格 -->
      <div class="chart-panel rounded-2xl p-4">
        <div class="panel-title">作业明细</div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs" style="border-collapse:collapse;">
            <thead>
              <tr style="color:#3a6080;border-bottom:1px solid #0d2540;">
                <th class="py-2 px-3 text-left">作业名称</th>
                <th class="py-2 px-3 text-left">班级</th>
                <th class="py-2 px-3 text-center">应交</th>
                <th class="py-2 px-3 text-center">已交</th>
                <th class="py-2 px-3 text-center">提交率</th>
                <th class="py-2 px-3 text-center">平均分</th>
                <th class="py-2 px-3 text-center">最高分</th>
                <th class="py-2 px-3 text-center">最低分</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id"
                class="border-b transition-colors"
                style="border-color:#0d2540;"
                :class="hoveredRow===row.id?'row-hover':''"
                @mouseenter="hoveredRow=row.id" @mouseleave="hoveredRow=null">
                <td class="py-2 px-3 font-medium" style="color:#c0e8ff;">{{ row.title }}</td>
                <td class="py-2 px-3" style="color:#7ab4d4;">{{ row.class_name }}</td>
                <td class="py-2 px-3 text-center" style="color:#4a7090;">{{ row.total_stu }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#00ff9d;">{{ row.sub_cnt }}</td>
                <td class="py-2 px-3 text-center">
                  <span class="rate-badge" :style="getRateStyle(row.rate)">{{ row.rate }}%</span>
                </td>
                <td class="py-2 px-3 text-center font-mono" style="color:#f59e0b;">{{ row.avg_score ?? '—' }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#34d399;">{{ row.max_score ?? '—' }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#f472b6;">{{ row.min_score ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div class="scan-line pointer-events-none"></div>
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
const hoveredRow = ref(null)

const summary = ref([
  { label: '作业总数', value: 0, color: '#f472b6' },
  { label: '总提交数', value: 0, color: '#34d399' },
  { label: '平均提交率', value: '0%', color: '#00c8ff' },
  { label: '平均得分', value: '0', color: '#f59e0b' },
])

const submitRateChart = ref(null)
const avgScoreChart = ref(null)
const scoreDistChart = ref(null)
const classRateChart = ref(null)
let charts = []

const techColors = ['#00c8ff','#00ff9d','#a78bfa','#f59e0b','#f472b6','#34d399','#60a5fa','#fb923c','#e879f9','#4ade80']

function getRateStyle(rate) {
  const n = parseFloat(rate)
  if (n >= 90) return 'background:#00ff9d22;color:#00ff9d;border:1px solid #00ff9d44;'
  if (n >= 70) return 'background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;'
  return 'background:#f472b622;color:#f472b6;border:1px solid #f472b644;'
}

function disposeCharts() {
  charts.forEach(c => c.dispose())
  charts = []
}

function initSubmitRateChart(data) {
  if (!submitRateChart.value) return
  const ins = echarts.init(submitRateChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.title)
  const values = data.map(d => parseFloat(d.rate))
  const visibleCount = 7
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 12, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 8, top: 12, bottom: 30, width: 14,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#f472b666' }, fillerColor: 'rgba(244,114,182,0.08)', borderColor: '#0d2540',
        textStyle: { color: '#3a6080', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', max: 100, axisLabel: { color: '#3a6080', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { lineStyle: { color: '#1a3050' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 10, formatter: v => v.length > 8 ? v.slice(0,8)+'…' : v } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#00ff9d' : v >= 70 ? '#f59e0b' : '#f472b6'
        return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [0,6,6,0] },
      label: { show: true, position: 'right', color: '#7ab4d4', fontSize: 10, formatter: p => p.value + '%' }
    }],
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${names[p.dataIndex]}<br/><b style="color:#f472b6">${p.value}%</b>` }
  })
}

function initAvgScoreChart(data) {
  if (!avgScoreChart.value) return
  const ins = echarts.init(avgScoreChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.title)
  const values = data.map(d => d.avg_score ?? 0)
  const visibleCount = 7
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 12, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 8, top: 12, bottom: 30, width: 14,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#f59e0b66' }, fillerColor: 'rgba(245,158,11,0.08)', borderColor: '#0d2540',
        textStyle: { color: '#3a6080', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', max: 100, axisLabel: { color: '#3a6080', fontSize: 10 },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { lineStyle: { color: '#1a3050' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 10, formatter: v => v.length > 8 ? v.slice(0,8)+'…' : v } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: { color: p => new echarts.graphic.LinearGradient(0,0,1,0,[
        {offset:0,color:'#f59e0b44'},{offset:1,color:'#f59e0b'}]), borderRadius: [0,6,6,0] },
      label: { show: true, position: 'right', color: '#7ab4d4', fontSize: 10, formatter: p => p.value > 0 ? p.value.toFixed(1) : '—' }
    }],
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${names[p.dataIndex]}<br/>平均分 <b style="color:#f59e0b">${p.value.toFixed(1)}</b>` }
  })
}

function initScoreDistChart(data) {
  if (!scoreDistChart.value) return
  const ins = echarts.init(scoreDistChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  // data: [{title, dist: {excellent, good, pass, fail}}]
  const names = data.map(d => d.title.length > 8 ? d.title.slice(0,8)+'…' : d.title)
  const segments = ['优秀(90+)', '良好(70-89)', '及格(60-69)', '不及格(<60)']
  const segColors = ['#00ff9d', '#00c8ff', '#f59e0b', '#f472b6']
  const segKeys = ['excellent', 'good', 'pass', 'fail']
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' } },
    legend: { data: segments, textStyle: { color: '#7ab4d4', fontSize: 10 }, top: 4 },
    grid: { left: 16, right: 16, top: 40, bottom: 50 },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#3a6080', fontSize: 9, rotate: 20 },
      axisLine: { lineStyle: { color: '#1a3050' } }, axisTick: { show: false } },
    yAxis: { type: 'value', axisLabel: { color: '#3a6080', fontSize: 10 },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { show: false } },
    series: segKeys.map((k, i) => ({
      name: segments[i], type: 'bar', stack: 'total',
      data: data.map(d => d.dist[k] || 0),
      itemStyle: { color: segColors[i] + 'cc', borderRadius: i === 3 ? [4,4,0,0] : 0 },
      label: { show: false }
    }))
  })
}

function initClassRateChart(data) {
  if (!classRateChart.value) return
  const ins = echarts.init(classRateChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.name.replace('2025级',''))
  const values = data.map(d => parseFloat(d.rate))
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 20, right: 20, top: 20, bottom: 50 },
    xAxis: { type: 'category', data: names,
      axisLabel: { color: '#3a6080', fontSize: 9, rotate: 20 },
      axisLine: { lineStyle: { color: '#1a3050' } }, axisTick: { show: false } },
    yAxis: { type: 'value', max: 100, axisLabel: { color: '#3a6080', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { show: false } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 36,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#00ff9d' : v >= 70 ? '#00c8ff' : '#f59e0b'
        return new echarts.graphic.LinearGradient(0,1,0,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [4,4,0,0] },
      label: { show: true, position: 'top', color: '#7ab4d4', fontSize: 9, formatter: p => p.value + '%' }
    }],
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${names[p.dataIndex]}<br/>提交率 <b style="color:#00c8ff">${p.value}%</b>` }
  })
}

async function loadData() {
  loading.value = true
  disposeCharts()
  try {
    const res = await getAdminHomeworkStats({ course_id: filterCourse.value, class_id: filterClass.value })
    const d = res.data
    // 更新 summary
    summary.value[0].value = d.total_hw
    summary.value[1].value = d.total_subs
    summary.value[2].value = d.avg_rate + '%'
    summary.value[3].value = d.avg_score
    // 表格数据
    tableData.value = d.list
    await nextTick()
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    initSubmitRateChart(d.list)
    initAvgScoreChart(d.list)
    initScoreDistChart(d.list)
    initClassRateChart(d.class_rates)
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
  } catch (e) {}
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

<style scoped>
.hw-stats {
  font-family: 'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;
  position: relative;
  overflow: hidden;
}
.chart-panel {
  background: linear-gradient(135deg,#0a1929 0%,#070f1e 100%);
  border: 1px solid #0d2540;
  position: relative;
  overflow: hidden;
}
.panel-title {
  font-size: 12px; letter-spacing: 2px; color: #4a90b8;
  margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #0d2540;
}
.rate-badge { padding: 1px 6px; border-radius: 6px; font-size: 10px; font-weight: 600; }
.row-hover { background: rgba(0,200,255,0.04) !important; }
@keyframes scan { 0% { top:-2px;opacity:.6; } 100% { top:100%;opacity:0; } }
.scan-line { position:fixed;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(0,200,255,0.4),transparent);
  animation:scan 6s linear infinite; }
</style>
