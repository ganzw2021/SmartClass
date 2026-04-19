<template>
  <div class="att-stats min-h-screen p-4 lg:p-6 -mx-6 -mt-6 -mb-6" style="background:#070d1a;">

    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-1 h-8 rounded-full" style="background:linear-gradient(180deg,#60a5fa,#00ff9d);"></div>
        <div>
          <h1 class="text-xl font-bold tracking-widest" style="color:#e0f4ff;letter-spacing:4px;">考 勤 统 计</h1>
          <p class="text-xs mt-0.5" style="color:#3a6080;">ATTENDANCE STATISTICS · 管理员视角</p>
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

    <!-- 汇总 KPI -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
      <div v-for="kpi in summary" :key="kpi.label"
        class="rounded-xl p-4 flex flex-col items-center gap-1 border"
        :style="`border-color:${kpi.color}44;background:linear-gradient(135deg,${kpi.color}12,${kpi.color}06);`">
        <div class="text-3xl font-bold font-mono" :style="`color:${kpi.color};text-shadow:0 0 10px ${kpi.color}66;`">{{ kpi.value }}</div>
        <div class="text-xs tracking-widest" style="color:#4a7090;">{{ kpi.label }}</div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-sm" style="color:#3a6080;">数据加载中…</div>
    </div>

    <template v-else>
      <!-- 第一行：各状态分布 + 班级签到率 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <!-- 状态环形图 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">签到状态总览</div>
          <div ref="donutChart" style="height:280px;"></div>
        </div>
        <!-- 班级签到率条形图 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">各班级签到率</div>
          <div ref="classRateChart" style="height:280px;"></div>
        </div>
      </div>

      <!-- 第二行：各报表签到情况 + 学生缺勤排行 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <!-- 考勤报表列表图（按报表显示签到 vs 缺勤） -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">各次考勤详情（已签/缺勤）</div>
          <div ref="reportChart" style="height:280px;"></div>
        </div>
        <!-- 缺勤次数 TOP 排行 -->
        <div class="chart-panel rounded-2xl p-4">
          <div class="panel-title">缺勤 TOP 学生</div>
          <div ref="absentChart" style="height:280px;"></div>
        </div>
      </div>

      <!-- 报表明细表格 -->
      <div class="chart-panel rounded-2xl p-4">
        <div class="panel-title">考勤报表明细</div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs" style="border-collapse:collapse;">
            <thead>
              <tr style="color:#3a6080;border-bottom:1px solid #0d2540;">
                <th class="py-2 px-3 text-left">课程</th>
                <th class="py-2 px-3 text-left">班级</th>
                <th class="py-2 px-3 text-center">总人数</th>
                <th class="py-2 px-3 text-center">已签到</th>
                <th class="py-2 px-3 text-center">迟到</th>
                <th class="py-2 px-3 text-center">请假</th>
                <th class="py-2 px-3 text-center">缺勤</th>
                <th class="py-2 px-3 text-center">签到率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id"
                class="border-b" style="border-color:#0d2540;"
                :class="hoveredRow===row.id?'row-hover':''"
                @mouseenter="hoveredRow=row.id" @mouseleave="hoveredRow=null">
                <td class="py-2 px-3" style="color:#c0e8ff;">{{ row.course_name }}</td>
                <td class="py-2 px-3" style="color:#7ab4d4;">{{ row.class_name }}</td>
                <td class="py-2 px-3 text-center" style="color:#4a7090;">{{ row.total }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#00ff9d;">{{ row.signed }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#f59e0b;">{{ row.late }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#60a5fa;">{{ row.leave }}</td>
                <td class="py-2 px-3 text-center font-mono" style="color:#f472b6;">{{ row.absent }}</td>
                <td class="py-2 px-3 text-center">
                  <span class="rate-badge" :style="getRateStyle(row.rate)">{{ row.rate }}%</span>
                </td>
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
import { getAdminAttendanceStats, getAdminCourseList, getAdminClassList } from '../api.js'

const loading = ref(true)
const filterCourse = ref('')
const filterClass = ref('')
const courseList = ref([])
const classList = ref([])
const tableData = ref([])
const hoveredRow = ref(null)

const summary = ref([
  { label: '考勤报表数', value: 0, color: '#60a5fa' },
  { label: '签到人次', value: 0, color: '#00ff9d' },
  { label: '缺勤人次', value: 0, color: '#f472b6' },
  { label: '平均签到率', value: '0%', color: '#f59e0b' },
])

const donutChart = ref(null)
const classRateChart = ref(null)
const reportChart = ref(null)
const absentChart = ref(null)
let charts = []

function getRateStyle(rate) {
  const n = parseFloat(rate)
  if (n >= 90) return 'background:#00ff9d22;color:#00ff9d;border:1px solid #00ff9d44;'
  if (n >= 70) return 'background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;'
  return 'background:#f472b622;color:#f472b6;border:1px solid #f472b644;'
}

function disposeCharts() { charts.forEach(c => c.dispose()); charts = [] }

function initDonutChart(dist) {
  if (!donutChart.value) return
  const ins = echarts.init(donutChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const colorMap = { '已签到': '#00ff9d', '迟到': '#f59e0b', '请假': '#60a5fa', '缺勤': '#f472b6' }
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${p.name}<br/><b style="color:${p.color}">${p.value}</b> 人次` },
    legend: { orient: 'vertical', right: 0, top: 'middle', textStyle: { color: '#7ab4d4', fontSize: 11 } },
    series: [{
      type: 'pie', radius: ['45%', '68%'], center: ['40%', '50%'],
      data: dist.map(d => ({ name: d.name, value: d.value,
        itemStyle: { color: colorMap[d.name] || '#00c8ff' } })),
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 16, shadowColor: 'rgba(0,200,255,0.4)' } }
    }]
  })
}

function initClassRateChart(data) {
  if (!classRateChart.value) return
  const ins = echarts.init(classRateChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.name.replace('2025级',''))
  const values = data.map(d => parseFloat(d.rate))
  const visibleCount = 7
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 12, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 8, top: 12, bottom: 30, width: 14,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#60a5fa66' }, fillerColor: 'rgba(96,165,250,0.08)', borderColor: '#0d2540',
        textStyle: { color: '#3a6080', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', max: 100, axisLabel: { color: '#3a6080', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { lineStyle: { color: '#1a3050' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 10 } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#00ff9d' : v >= 70 ? '#60a5fa' : '#f472b6'
        return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [0,6,6,0] },
      label: { show: true, position: 'right', color: '#7ab4d4', fontSize: 10, formatter: p => p.value + '%' }
    }],
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${names[p.dataIndex]}<br/>签到率 <b style="color:#60a5fa">${p.value}%</b>` }
  })
}

function initReportChart(data) {
  if (!reportChart.value) return
  const ins = echarts.init(reportChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  // data: [{label, signed, absent, late, leave}]
  const names = data.map(d => d.label)
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' } },
    legend: { data: ['已签到','迟到','请假','缺勤'], textStyle: { color: '#7ab4d4', fontSize: 10 }, top: 4 },
    grid: { left: 16, right: 60, top: 38, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 8, top: 38, bottom: 30, width: 14,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#00ff9d66' }, fillerColor: 'rgba(0,255,157,0.08)', borderColor: '#0d2540',
        textStyle: { color: '#3a6080', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', axisLabel: { color: '#3a6080', fontSize: 10 },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { lineStyle: { color: '#1a3050' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 9, formatter: v => v.length > 10 ? v.slice(0,10)+'…' : v } },
    series: [
      { name: '已签到', type: 'bar', stack: 'total', data: data.map(d => d.signed), barMaxWidth: 18,
        itemStyle: { color: '#00ff9dcc', borderRadius: 0 } },
      { name: '迟到', type: 'bar', stack: 'total', data: data.map(d => d.late), barMaxWidth: 18,
        itemStyle: { color: '#f59e0bcc' } },
      { name: '请假', type: 'bar', stack: 'total', data: data.map(d => d.leave), barMaxWidth: 18,
        itemStyle: { color: '#60a5facc' } },
      { name: '缺勤', type: 'bar', stack: 'total', data: data.map(d => d.absent), barMaxWidth: 18,
        itemStyle: { color: '#f472b6cc', borderRadius: [0,6,6,0] } }
    ]
  })
}

function initAbsentChart(data) {
  if (!absentChart.value) return
  const ins = echarts.init(absentChart.value, null, { renderer: 'canvas' })
  charts.push(ins)
  const names = data.map(d => d.name)
  const values = data.map(d => d.count)
  const visibleCount = 8
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 100, right: 60, top: 12, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 8, top: 12, bottom: 30, width: 14,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#f472b666' }, fillerColor: 'rgba(244,114,182,0.08)', borderColor: '#0d2540',
        textStyle: { color: '#3a6080', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', axisLabel: { color: '#3a6080', fontSize: 10 },
      splitLine: { lineStyle: { color: '#0d2035', type: 'dashed' } }, axisLine: { lineStyle: { color: '#1a3050' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#7ab4d4', fontSize: 10 } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 18,
      itemStyle: { color: p => new echarts.graphic.LinearGradient(0,0,1,0,[
        {offset:0,color:'#f472b644'},{offset:1,color:'#f472b6'}]), borderRadius: [0,6,6,0] },
      label: { show: true, position: 'right', color: '#f472b6', fontSize: 10, formatter: p => p.value + ' 次' }
    }],
    tooltip: { backgroundColor: '#0a1929', borderColor: '#00c8ff44', textStyle: { color: '#c0e8ff' },
      formatter: p => `${names[p.dataIndex]}<br/>缺勤 <b style="color:#f472b6">${p.value}</b> 次` }
  })
}

async function loadData() {
  loading.value = true
  disposeCharts()
  try {
    const res = await getAdminAttendanceStats({ course_id: filterCourse.value, class_id: filterClass.value })
    const d = res.data
    summary.value[0].value = d.total_reports
    summary.value[1].value = d.total_signed
    summary.value[2].value = d.total_absent
    summary.value[3].value = d.avg_rate + '%'
    tableData.value = d.list
    await nextTick()
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    initDonutChart(d.dist)
    initClassRateChart(d.class_rates)
    initReportChart(d.report_series)
    initAbsentChart(d.absent_top)
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
.att-stats {
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
