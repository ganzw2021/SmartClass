<template>
  <div class="space-y-6">

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
        <!-- 状态环形图 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">签到状态总览</div>
          <div ref="donutChart" style="height:280px;"></div>
        </div>
        <!-- 班级签到率 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">各班级签到率</div>
          <div ref="classRateChart" style="height:280px;"></div>
        </div>
      </div>

      <!-- 第二行图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- 各次考勤详情 -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">各次考勤详情</div>
          <div ref="reportChart" style="height:280px;"></div>
        </div>
        <!-- 缺勤 TOP -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
          <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">缺勤 TOP 学生</div>
          <div ref="absentChart" style="height:280px;"></div>
        </div>
      </div>

      <!-- 报表明细表格 -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="text-sm font-bold text-slate-500 mb-3 border-b border-slate-100 pb-2">考勤报表明细（共 {{ tableData.length }} 条）</div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-slate-50 border-b border-slate-100">
                <th class="text-left py-3 px-4 text-slate-500 font-medium">课程</th>
                <th class="text-left py-3 px-4 text-slate-500 font-medium">班级</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">总人数</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">已签到</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">迟到</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">请假</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">缺勤</th>
                <th class="text-center py-3 px-4 text-slate-500 font-medium">签到率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id"
                class="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td class="py-3 px-4 text-slate-700">{{ row.course_name }}</td>
                <td class="py-3 px-4 text-slate-500">{{ row.class_name }}</td>
                <td class="py-3 px-4 text-center text-slate-400">{{ row.total }}</td>
                <td class="py-3 px-4 text-center font-mono text-emerald-600">{{ row.signed }}</td>
                <td class="py-3 px-4 text-center font-mono text-amber-600">{{ row.late }}</td>
                <td class="py-3 px-4 text-center font-mono text-sky-600">{{ row.leave }}</td>
                <td class="py-3 px-4 text-center font-mono text-rose-600">{{ row.absent }}</td>
                <td class="py-3 px-4 text-center">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                    :class="getRateBadge(row.rate)">{{ row.rate }}%</span>
                </td>
              </tr>
              <tr v-if="tableData.length === 0">
                <td colspan="8" class="py-12 text-center text-slate-400">暂无考勤数据</td>
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
import { getAdminAttendanceStats, getAdminCourseList, getAdminClassList } from '../api.js'

const loading = ref(true)
const filterCourse = ref('')
const filterClass = ref('')
const courseList = ref([])
const classList = ref([])
const tableData = ref([])

const summary = ref([
  { label: '考勤报表数', value: 0, borderClass: 'border-l-sky-500' },
  { label: '签到人次',   value: 0, borderClass: 'border-l-emerald-500' },
  { label: '缺勤人次',   value: 0, borderClass: 'border-l-rose-500' },
  { label: '平均签到率', value: '0%', borderClass: 'border-l-amber-500' },
])

const donutChart = ref(null)
const classRateChart = ref(null)
const reportChart = ref(null)
const absentChart = ref(null)
let charts = []

function getRateBadge(rate) {
  const n = parseFloat(rate)
  if (n >= 90) return 'bg-emerald-50 text-emerald-700'
  if (n >= 70) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

function disposeCharts() { charts.forEach(c => c.dispose()); charts = [] }

function initDonutChart(dist) {
  if (!donutChart.value) return
  const ins = echarts.init(donutChart.value)
  charts.push(ins)
  const colorMap = { '已签到': '#10b981', '迟到': '#f59e0b', '请假': '#6366f1', '缺勤': '#ef4444' }
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${p.name}<br/><b style="color:${p.color}">${p.value}</b> 人次` },
    legend: { orient: 'vertical', right: 0, top: 'middle', textStyle: { color: '#64748b', fontSize: 11 } },
    series: [{
      type: 'pie', radius: ['45%', '68%'], center: ['40%', '50%'],
      data: dist.map(d => ({ name: d.name, value: d.value, itemStyle: { color: colorMap[d.name] || '#6366f1' } })),
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(99,102,241,0.2)' } }
    }]
  })
}

function initClassRateChart(data) {
  if (!classRateChart.value) return
  const ins = echarts.init(classRateChart.value)
  charts.push(ins)
  const names = data.map(d => d.name.replace('2025级',''))
  const values = data.map(d => parseFloat(d.rate))
  const visibleCount = 6
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 130, right: 60, top: 10, bottom: 40 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 40, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#6366f144' }, fillerColor: 'rgba(99,102,241,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value', max: 100,
      axisLabel: { color: '#94a3b8', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 10 } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 16,
      itemStyle: { color: p => {
        const v = values[p.dataIndex]
        const c = v >= 90 ? '#10b981' : v >= 70 ? '#6366f1' : '#ef4444'
        return new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:c+'44'},{offset:1,color:c}])
      }, borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', color: '#64748b', fontSize: 10, formatter: p => p.value + '%' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/>签到率 <b style="color:#6366f1">${p.value}%</b>` }
  })
}

function initReportChart(data) {
  if (!reportChart.value) return
  const ins = echarts.init(reportChart.value)
  charts.push(ins)
  const names = data.map(d => d.label)
  const visibleCount = 5
  ins.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' } },
    legend: { data: ['已签到','迟到','请假','缺勤'], textStyle: { color: '#64748b', fontSize: 10 }, top: 4 },
    grid: { left: 16, right: 60, top: 40, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 40, bottom: 30, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#10b98144' }, fillerColor: 'rgba(16,185,129,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 9, formatter: v => v.length > 10 ? v.slice(0,10)+'…' : v } },
    series: [
      { name: '已签到', type: 'bar', stack: 'total', data: data.map(d => d.signed), barMaxWidth: 16,
        itemStyle: { color: '#10b981cc', borderRadius: 0 } },
      { name: '迟到', type: 'bar', stack: 'total', data: data.map(d => d.late), barMaxWidth: 16,
        itemStyle: { color: '#f59e0bcc' } },
      { name: '请假', type: 'bar', stack: 'total', data: data.map(d => d.leave), barMaxWidth: 16,
        itemStyle: { color: '#6366f1cc' } },
      { name: '缺勤', type: 'bar', stack: 'total', data: data.map(d => d.absent), barMaxWidth: 16,
        itemStyle: { color: '#ef4444cc', borderRadius: [0,6,6,0] } }
    ]
  })
}

function initAbsentChart(data) {
  if (!absentChart.value) return
  const ins = echarts.init(absentChart.value)
  charts.push(ins)
  const names = data.map(d => d.name)
  const values = data.map(d => d.count)
  const visibleCount = 8
  ins.setOption({
    backgroundColor: 'transparent',
    grid: { left: 100, right: 60, top: 10, bottom: 30 },
    dataZoom: [
      { type: 'slider', yAxisIndex: 0, orient: 'vertical', right: 6, top: 10, bottom: 30, width: 12,
        start: 0, end: Math.min(100, Math.round(visibleCount / Math.max(names.length,1) * 100)),
        handleStyle: { color: '#ef444444' }, fillerColor: 'rgba(239,68,68,0.06)',
        borderColor: '#e2e8f0', textStyle: { color: '#94a3b8', fontSize: 9 } },
      { type: 'inside', yAxisIndex: 0, orient: 'vertical' }
    ],
    xAxis: { type: 'value',
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'category', data: names, axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 10 } },
    series: [{
      type: 'bar', data: values, barMaxWidth: 16,
      itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[
        {offset:0,color:'#ef444444'},{offset:1,color:'#ef4444'}]), borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', color: '#ef4444', fontSize: 10, formatter: p => p.value + ' 次' }
    }],
    tooltip: {
      backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#334155' },
      formatter: p => `${names[p.dataIndex]}<br/>缺勤 <b style="color:#ef4444">${p.value}</b> 次` }
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
    tableData.value = d.list || []
    await nextTick()
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    initDonutChart(d.dist || [])
    initClassRateChart(d.class_rates || [])
    initReportChart(d.report_series || [])
    initAbsentChart(d.absent_top || [])
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
