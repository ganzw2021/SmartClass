<template>
  <div class="space-y-5">
    <div class="flex flex-wrap gap-3 items-end">
      <div>
        <label class="text-xs font-bold text-slate-400">课程</label>
        <select v-model="courseId" @change="onCourseChange" class="block mt-1 border rounded-xl p-3">
          <option value="">请选择课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}{{ course.term ? `（${course.term}）` : '' }}
          </option>
        </select>
      </div>
      <div>
        <label class="text-xs font-bold text-slate-400">班级</label>
        <select v-model="classId" @change="onClassChange" :disabled="!courseId" class="block mt-1 border rounded-xl p-3 disabled:opacity-50">
          <option value="">请选择班级</option>
          <option v-for="c in courseClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div v-if="classId" class="min-w-[220px] flex-1">
        <label class="text-xs font-bold text-slate-400">搜索</label>
        <input v-model.trim="searchQuery" type="search" placeholder="搜索学号或姓名" aria-label="搜索学号或姓名" class="block mt-1 w-full border rounded-xl p-3" />
      </div>
      <button v-if="classId" @click="load" class="px-4 py-3 rounded-xl bg-green-600 text-white font-bold">刷新</button>
    </div>

    <div v-if="statusMessage" class="rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800">{{ statusMessage }}</div>

    <div v-if="showLogs && classId" class="bg-white rounded-2xl shadow-sm overflow-x-auto">
      <div class="px-5 pt-5 text-lg font-black">{{ selectedLogStudent ? `${studentName(selectedLogStudent)} 的积分调整记录` : '积分调整记录' }}</div>
      <table class="w-full text-sm min-w-[720px]">
        <thead class="bg-slate-50"><tr><th class="p-4 text-left">学生</th><th class="p-4 text-left">分项</th><th class="p-4 text-left">增减分</th><th class="p-4 text-left">操作时间</th><th class="p-4 text-left">操作人</th></tr></thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-t">
            <td class="p-4">{{ studentName(log.student_id) }}<span class="ml-2 text-slate-400">{{ log.student_id }}</span></td>
            <td class="p-4">{{ categoryLabel(log.category) }}</td>
            <td class="p-4 font-bold" :class="Number(log.delta) > 0 ? 'text-green-600' : 'text-red-600'">{{ formatDelta(log.delta) }}</td>
            <td class="p-4">{{ formatTime(log.created_at) }}</td>
            <td class="p-4">{{ log.teacher_username || '-' }}</td>
          </tr>
          <tr v-if="!logs.length"><td colspan="5" class="p-8 text-center text-slate-400">暂无调整记录</td></tr>
        </tbody>
      </table>
    </div>

    <div v-if="classId" class="bg-white rounded-2xl shadow-sm overflow-x-auto">
      <table class="w-full text-sm min-w-[940px]">
        <thead class="bg-green-50">
          <tr>
            <th v-for="column in sortableColumns" :key="column.key" class="p-4" :class="column.align === 'left' ? 'text-left' : 'text-center'" :aria-sort="ariaSort(column.key)">
              <button type="button" class="inline-flex w-full items-center gap-1 hover:text-green-700" :class="column.align === 'left' ? 'justify-start' : 'justify-center'" @click="setSort(column.key)">
                <span>{{ column.label }}</span>
                <span class="inline-block w-3" aria-hidden="true">{{ sortIndicator(column.key) }}</span>
              </button>
            </th>
            <th class="p-4">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredRows" :key="r.student_id" class="border-t">
            <td class="p-4 font-bold">{{ r.rank }}</td>
            <td class="p-4 font-mono">{{ r.student_number || '-' }}</td>
            <td class="p-4 font-bold">{{ r.student_name }}</td>
            <td class="p-4 text-center"><Adjust v-if="editingStudentId === r.student_id" :value="r.attendance_score" @minus="change(r, 'attendance', -1)" @plus="change(r, 'attendance', 1)" /><span v-else>{{ Number(r.attendance_score || 0).toFixed(2) }}</span></td>
            <td class="p-4 text-center"><span class="font-bold">{{ Number(r.homework_score || 0).toFixed(2) }}</span><small class="block text-slate-400">天梯 {{ r.ladder_score }} / {{ data.homework_count }} 个作业</small></td>
            <td class="p-4 text-center"><Adjust v-if="editingStudentId === r.student_id" :value="r.classroom_score" @minus="change(r, 'classroom', -1)" @plus="change(r, 'classroom', 1)" /><span v-else>{{ Number(r.classroom_score || 0).toFixed(2) }}</span></td>
            <td class="p-4 text-center text-lg font-black text-green-700">{{ Number(r.total_score || 0).toFixed(2) }}</td>
            <td class="p-4 text-center whitespace-nowrap"><div class="inline-flex gap-2"><button @click="toggleEditing(r)" :disabled="savingStudentId === r.student_id" class="px-3 py-2 rounded-lg bg-blue-600 text-white font-bold disabled:opacity-50">{{ editingStudentId === r.student_id ? '保存' : '调整' }}</button><button @click="toggleLogs(r)" class="px-3 py-2 rounded-lg bg-slate-700 text-white font-bold">{{ showLogs && selectedLogStudent === r.student_id ? '收起记录' : '记录' }}</button></div></td>
          </tr>
          <tr v-if="!filteredRows.length"><td colspan="8" class="p-8 text-center text-slate-400">{{ rows.length ? '未找到匹配的学生' : '暂无学生数据' }}</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, h } from 'vue'
import { getPointsBoard, adjustPoints, getPointLogs } from '../api.js'

const Adjust = {
  props: { value: [Number, String] },
  emits: ['minus', 'plus'],
  setup(props, { emit }) {
    return () => h('div', { class: 'inline-flex items-center gap-2' }, [
      h('button', { class: 'w-7 h-7 rounded-md bg-red-50 text-red-600 font-black', onClick: () => emit('minus') }, '-'),
      h('span', { class: 'min-w-[52px]' }, Number(props.value || 0).toFixed(2)),
      h('button', { class: 'w-7 h-7 rounded-md bg-green-50 text-green-600 font-black', onClick: () => emit('plus') }, '+')
    ])
  }
}

const props = defineProps({ courses: { type: Array, default: () => [] }, classes: { type: Array, default: () => [] } })
const courseId = ref('')
const classId = ref('')
const rows = ref([])
const data = ref({ homework_count: 0 })
const searchQuery = ref('')
const editingStudentId = ref(null)
const savingStudentId = ref(null)
const pendingChanges = ref({})
const showLogs = ref(false)
const selectedLogStudent = ref(null)
const logs = ref([])
const statusMessage = ref('')
const sortKey = ref('student_number')
const sortDirection = ref('asc')
const numericSortKeys = new Set(['rank', 'attendance_score', 'homework_score', 'classroom_score', 'total_score'])
const descendingByDefault = new Set(['attendance_score', 'homework_score', 'classroom_score', 'total_score'])
const sortableColumns = [
  { key: 'rank', label: '排名', align: 'left' },
  { key: 'student_number', label: '学号', align: 'left' },
  { key: 'student_name', label: '姓名', align: 'left' },
  { key: 'attendance_score', label: '考勤分', align: 'center' },
  { key: 'homework_score', label: '作业分', align: 'center' },
  { key: 'classroom_score', label: '课堂分', align: 'center' },
  { key: 'total_score', label: '总分', align: 'center' }
]

const selectedCourse = computed(() => props.courses.find(c => String(c.id) === String(courseId.value)))
const courseClasses = computed(() => selectedCourse.value?.classes || props.classes.filter(c => (c.course_ids || []).map(String).includes(String(courseId.value))))
const filteredRows = computed(() => {
  const q = searchQuery.value.toLowerCase()
  const result = rows.value.filter(r => !q || String(r.student_number || '').toLowerCase().includes(q) || String(r.student_name || '').toLowerCase().includes(q))

  return [...result].sort((a, b) => {
    const key = sortKey.value
    const aValue = a[key]
    const bValue = b[key]
    const aEmpty = aValue === null || aValue === undefined || aValue === ''
    const bEmpty = bValue === null || bValue === undefined || bValue === ''
    if (aEmpty !== bEmpty) return aEmpty ? 1 : -1
    if (aEmpty) return 0

    const comparison = numericSortKeys.has(key)
      ? Number(aValue) - Number(bValue)
      : String(aValue).localeCompare(String(bValue), 'zh-CN', { numeric: true, sensitivity: 'base' })
    return sortDirection.value === 'asc' ? comparison : -comparison
  })
})

function setSort(key) {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    return
  }
  sortKey.value = key
  sortDirection.value = descendingByDefault.has(key) ? 'desc' : 'asc'
}

function sortIndicator(key) {
  if (sortKey.value !== key) return ''
  return sortDirection.value === 'asc' ? '↑' : '↓'
}

function ariaSort(key) {
  if (sortKey.value !== key) return 'none'
  return sortDirection.value === 'asc' ? 'ascending' : 'descending'
}

function onCourseChange() {
  editingStudentId.value = null
  pendingChanges.value = {}
  classId.value = ''
  rows.value = []
  data.value = { homework_count: 0 }
  logs.value = []
  showLogs.value = false
  selectedLogStudent.value = null
  searchQuery.value = ''
  statusMessage.value = ''
}

function onClassChange() {
  editingStudentId.value = null
  pendingChanges.value = {}
  logs.value = []
  showLogs.value = false
  selectedLogStudent.value = null
  statusMessage.value = ''
  load()
}

async function load() {
  if (!courseId.value || !classId.value) return
  const response = await getPointsBoard(courseId.value, classId.value)
  if (response.success) {
    data.value = response.data
    rows.value = response.data.rows || []
  } else {
    statusMessage.value = response.message || '积分榜加载失败'
  }
}

function toggleEditing(row) {
  if (editingStudentId.value === row.student_id) saveAdjustments(row)
  else {
    if (editingStudentId.value !== null) {
      statusMessage.value = '请先保存当前学生的调整'
      return
    }
    pendingChanges.value = { [row.student_id]: { attendance: 0, classroom: 0 } }
    statusMessage.value = ''
    editingStudentId.value = row.student_id
  }
}

function change(row, category, delta) {
  const current = pendingChanges.value[row.student_id] || { attendance: 0, classroom: 0 }
  pendingChanges.value = { ...pendingChanges.value, [row.student_id]: { ...current, [category]: current[category] + delta } }
  const field = category === 'attendance' ? 'attendance_score' : 'classroom_score'
  row[field] = Number(row[field] || 0) + delta
  row.total_score = Number(row.attendance_score || 0) + Number(row.homework_score || 0) + Number(row.classroom_score || 0)
  recalculateRanks()
}

function recalculateRanks() {
  const ranked = [...rows.value].sort((a, b) => Number(b.total_score || 0) - Number(a.total_score || 0) || String(a.student_name).localeCompare(String(b.student_name)))
  ranked.forEach((row, index) => { row.rank = index + 1 })
}

async function saveAdjustments(row) {
  if (!courseId.value || !classId.value || savingStudentId.value !== null || !row) return
  const requests = []
  const changes = pendingChanges.value[row.student_id] || {}
  for (const category of ['attendance', 'classroom']) {
    const delta = Number(changes[category] || 0)
    if (delta) requests.push(adjustPoints({ course_id: courseId.value, class_id: classId.value, student_id: row.student_id, category, delta, reason: '积分榜调整' }))
  }
  savingStudentId.value = row.student_id
  try {
    const results = await Promise.all(requests)
    const failed = results.find(result => !result.success)
    if (failed) {
      statusMessage.value = failed.message || '积分保存失败，请重试'
      return
    }
    editingStudentId.value = null
    pendingChanges.value = {}
    statusMessage.value = requests.length ? '积分已保存' : ''
    await load()
    if (showLogs.value && selectedLogStudent.value === row.student_id) await loadLogs()
  } catch (error) {
    statusMessage.value = '积分保存失败，请检查网络后重试'
  } finally {
    savingStudentId.value = null
  }
}

async function toggleLogs(row) {
  if (showLogs.value && selectedLogStudent.value === row.student_id) {
    showLogs.value = false
    selectedLogStudent.value = null
    logs.value = []
    return
  }
  showLogs.value = true
  selectedLogStudent.value = row.student_id
  await loadLogs()
}

async function loadLogs() {
  if (!courseId.value || !classId.value) return
  const response = await getPointLogs(courseId.value, classId.value, selectedLogStudent.value)
  if (response.success) logs.value = response.data || []
  else statusMessage.value = response.message || '记录加载失败'
}

function studentName(studentId) {
  const row = rows.value.find(item => String(item.student_id) === String(studentId))
  return row?.student_name || `学生 ${studentId}`
}

function categoryLabel(category) {
  return { attendance: '考勤分', homework: '作业分', classroom: '课堂分' }[category] || category
}

function formatDelta(value) {
  const number = Number(value || 0)
  return `${number > 0 ? '+' : ''}${number.toFixed(2)}`
}

function formatTime(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}
</script>
