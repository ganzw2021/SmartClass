<template>
  <div>
    <!-- 筛选器 -->
    <div class="flex flex-col md:flex-row gap-4 items-end">
      <div class="flex-1 w-full">
        <label class="text-xs font-bold text-slate-400">选择课程</label>
        <select v-model="selectedCourse" @change="() => loadReports()" class="w-full border-2 border-green-50 px-4 py-2 rounded-xl bg-white text-sm font-bold mt-1 outline-green-200">
          <option value="">全部课程</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">[{{ c.term }}] {{ c.name }}</option>
        </select>
      </div>
      <div class="flex-1 w-full">
        <label class="text-xs font-bold text-slate-400">选择班级</label>
        <select v-model="selectedClass" @change="() => loadReports()" class="w-full border-2 border-green-50 px-4 py-2 rounded-xl bg-white text-sm font-bold mt-1 outline-green-200">
          <option value="">全部班级</option>
          <option v-for="c in filteredClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-slate-500 font-bold">{{ total }} 条记录</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-green-200 border-t-green-600"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!reports.length" class="text-center py-20">
      <div class="text-6xl mb-4 opacity-20">📋</div>
      <p class="text-slate-400 font-bold text-lg">暂无考勤记录</p>
      <p class="text-slate-300 text-sm mt-1">在考勤模块开启签到后会自动生成记录</p>
    </div>

    <!-- 报表列表 -->
    <div v-else class="space-y-4 mt-6">
      <div
        v-for="r in reports"
        :key="r.id"
        class="glass-card bg-white p-5 hover:shadow-md transition-all cursor-pointer"
        @click="openDetail(r)"
      >
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center gap-3 mb-1">
              <span class="font-black text-slate-700">{{ r.course_name || '未知课程' }}</span>
              <span class="px-2 py-0.5 bg-green-50 text-green-600 text-xs font-bold rounded-full">{{ r.class_name || '未知班级' }}</span>
            </div>
            <div class="text-xs text-slate-400">
              {{ formatDate(r.started_at) }} ~ {{ formatDate(r.ended_at) }}
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-sm font-bold text-green-600">{{ r.signed_count || 0 }} 已签</div>
              <div class="text-sm font-bold text-red-500">{{ r.absent_count || 0 }} 缺勤</div>
            </div>
            <div class="flex gap-2">
              <button
                @click.stop="openDetail(r)"
                class="px-3 py-1.5 bg-green-50 text-green-600 text-xs font-bold rounded-lg hover:bg-green-100 transition-colors"
              >查看</button>
              <button
                @click.stop="confirmDelete(r)"
                class="px-3 py-1.5 bg-red-50 text-red-500 text-xs font-bold rounded-lg hover:bg-red-100 transition-colors"
              >删除</button>
            </div>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="w-full h-1.5 bg-slate-100 rounded-full mt-3 overflow-hidden">
          <div
            v-if="r.total_students > 0"
            class="h-full bg-green-500 transition-all"
            :style="{ width: (r.signed_count / r.total_students * 100) + '%' }"
          ></div>
        </div>
        <div class="text-xs text-slate-400 mt-1">{{ r.total_students || 0 }} 人</div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex justify-center items-center gap-3 mt-6">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage <= 1"
        class="px-4 py-2 bg-slate-100 text-slate-600 text-sm font-bold rounded-xl disabled:opacity-40 hover:bg-slate-200 transition-colors"
      >上一页</button>
      <span class="text-sm text-slate-500 font-bold">{{ currentPage }} / {{ totalPages }}</span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage >= totalPages"
        class="px-4 py-2 bg-slate-100 text-slate-600 text-sm font-bold rounded-xl disabled:opacity-40 hover:bg-slate-200 transition-colors"
      >下一页</button>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetail" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3 sm:p-4" @click.self="showDetail = false">
      <div class="bg-white rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">

        <!-- 顶部渐变横幅 -->
        <div class="bg-gradient-to-r from-green-600 to-emerald-500 px-6 py-5 text-white">
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-lg font-black leading-tight">{{ detailData.course_name || '未知课程' }}</h3>
                <span class="px-2.5 py-0.5 bg-white/20 backdrop-blur text-xs font-bold rounded-full">{{ detailData.class_name || '未知班级' }}</span>
              </div>
              <p class="text-white/80 text-xs mt-2 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(detailData.started_at) }} ~ {{ formatDate(detailData.ended_at) }}
              </p>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                @click="exportExcel"
                :disabled="exporting"
                class="flex items-center gap-1.5 px-3 py-1.5 bg-white/20 hover:bg-white/30 backdrop-blur text-white text-xs font-bold rounded-lg transition-all"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ exporting ? '导出中...' : '导出Excel' }}
              </button>
              <button @click="showDetail = false" class="text-white/70 hover:text-white p-1.5 hover:bg-white/20 rounded-lg transition-all">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 出勤率进度条 -->
          <div class="mt-4">
            <div class="flex justify-between text-xs text-white/80 mb-1.5">
              <span>出勤率</span>
              <span class="font-black text-white">{{ attendanceRate }}%</span>
            </div>
            <div class="w-full h-2.5 bg-white/20 rounded-full overflow-hidden">
              <div
                class="h-full bg-white rounded-full transition-all duration-700"
                :style="{ width: attendanceRate + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- 统计数字卡 -->
        <div class="grid grid-cols-5 divide-x divide-slate-100 bg-white">
          <div class="py-4 px-2 text-center">
            <div class="text-2xl font-black text-emerald-600">{{ detailData.signed_count || 0 }}</div>
            <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-wide">已签到</div>
          </div>
          <div class="py-4 px-2 text-center">
            <div class="text-2xl font-black text-amber-500">{{ lateCount }}</div>
            <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-wide">迟到</div>
          </div>
          <div class="py-4 px-2 text-center">
            <div class="text-2xl font-black text-orange-500">{{ leaveCount }}</div>
            <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-wide">请假</div>
          </div>
          <div class="py-4 px-2 text-center">
            <div class="text-2xl font-black text-rose-600">{{ detailData.absent_count || 0 }}</div>
            <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-wide">缺勤</div>
          </div>
          <div class="py-4 px-2 text-center">
            <div class="text-2xl font-black text-slate-700">{{ detailData.total_students || 0 }}</div>
            <div class="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-wide">总人数</div>
          </div>
        </div>

        <!-- 表格区域 -->
        <div class="flex-1 overflow-y-auto">
          <table class="w-full text-sm">
            <thead class="sticky top-0 bg-slate-50 border-b border-slate-100">
              <tr>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider w-8">#</th>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider">姓名</th>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider">学号</th>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider">状态</th>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider">签到时间</th>
                <th class="px-4 py-3 text-left text-[11px] text-slate-400 font-bold uppercase tracking-wider w-16">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr
                v-for="(s, idx) in sortedStudents"
                :key="s.id"
                :class="['transition-colors hover:bg-slate-50/80', s.status === 'absent' ? 'bg-rose-50/40' : '']"
              >
                <td class="px-4 py-3 text-xs text-slate-400">{{ idx + 1 }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div :class="['w-7 h-7 rounded-full flex items-center justify-center text-xs font-black text-white', avatarColor(s.student_name)]">
                      {{ (s.student_name || '?')[0] }}
                    </div>
                    <span class="font-bold text-slate-700">{{ s.student_name }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-xs text-slate-400 font-mono">{{ s.student_number || '-' }}</td>
                <td class="px-4 py-3">
                  <span :class="statusClass(s.status) + ' text-xs font-bold px-2.5 py-1 rounded-full inline-flex items-center gap-1'">
                    <span class="w-1.5 h-1.5 rounded-full bg-current opacity-70"></span>
                    {{ statusText(s.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-slate-400 font-mono">{{ s.sign_time ? formatTime(s.sign_time) : '-' }}</td>
                <td class="px-4 py-3">
                  <button
                    @click="openModifyModal(s)"
                    class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-bold rounded-lg transition-all"
                  >修改</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 底部安全区 -->
        <div class="h-2 bg-white"></div>
      </div>
    </div>

    <!-- 修改状态弹窗 -->
    <div v-if="modifyTarget" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl">
        <div class="flex justify-between items-center p-5 border-b border-slate-100">
          <h3 class="font-black text-slate-700">修改考勤状态</h3>
          <button @click="modifyTarget = null" class="text-slate-400 hover:text-slate-600 p-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="text-center">
            <div class="text-lg font-black text-slate-700">{{ modifyTarget.student_name }}</div>
            <div class="text-xs text-slate-400 mt-1">{{ modifyTarget.student_number }}</div>
          </div>
          <div>
            <label class="text-xs font-bold text-slate-400 block mb-2">选择状态</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="opt in statusOptions"
                :key="opt.value"
                @click="selectedStatus = opt.value"
                :class="[
                  'px-3 py-2.5 rounded-xl text-sm font-bold transition-all border-2',
                  selectedStatus === opt.value
                    ? opt.activeClass + ' border-transparent shadow-sm'
                    : 'bg-slate-50 text-slate-500 border-transparent hover:bg-slate-100'
                ]"
              >{{ opt.label }}</button>
            </div>
          </div>
          <div>
            <label class="text-xs font-bold text-slate-400 block mb-1.5">备注（可选）</label>
            <input
              v-model="modifyNote"
              type="text"
              placeholder="如：因病请假"
              class="w-full border-2 border-slate-100 px-3 py-2 rounded-xl text-sm outline-none focus:border-indigo-300"
            />
          </div>
        </div>
        <div class="flex gap-3 p-5 pt-0">
          <button @click="modifyTarget = null" class="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200 transition-colors">取消</button>
          <button @click="doUpdateStatus" :disabled="submitting" class="flex-1 py-3 bg-indigo-500 text-white font-bold rounded-xl hover:bg-indigo-600 transition-colors disabled:opacity-50">
            {{ submitting ? '保存中...' : '确认保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deleteTarget" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="deleteTarget = null">
      <div class="bg-white rounded-2xl p-8 w-full max-w-sm shadow-2xl text-center">
        <div class="text-5xl mb-4">🗑️</div>
        <h3 class="font-black text-slate-700 text-lg mb-2">确认删除</h3>
        <p class="text-slate-400 text-sm mb-6">确定要删除这条考勤记录吗？此操作不可恢复。</p>
        <div class="flex gap-3">
          <button @click="deleteTarget = null" class="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200 transition-colors">取消</button>
          <button @click="doDelete" class="flex-1 py-3 bg-red-500 text-white font-bold rounded-xl hover:bg-red-600 transition-colors">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTeacherCourses } from '../api.js'
import {
  getAttendanceReports,
  getAttendanceReportDetail,
  deleteAttendanceReport,
  updateStudentAttendanceStatus
} from '../api.js'
import * as XLSX from 'xlsx'

// 课程和班级
const courses = ref([])
const classes = ref([])
const selectedCourse = ref('')
const selectedClass = ref('')

const filteredClasses = computed(() => {
  if (!selectedCourse.value) return classes.value
  const course = courses.value.find(c => c.id === selectedCourse.value)
  if (!course || !course.classes) return []
  return course.classes
})

// 报表数据
const reports = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 15
const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)
const loading = ref(false)

// 详情弹窗
const showDetail = ref(false)
const detailData = ref({})
const lateCount = computed(() => detailData.value.students?.filter(s => s.status === 'late').length || 0)
const leaveCount = computed(() => {
  const students = detailData.value.students || []
  return students.filter(s => s.status === 'leave_sick' || s.status === 'leave_personal').length
})
const attendanceRate = computed(() => {
  const total = detailData.value.total_students || 0
  if (!total) return 0
  const rate = ((detailData.value.signed_count || 0) / total * 100)
  return Math.round(rate)
})
const exporting = ref(false)

// 排序：未签到（缺勤）排前面，已签到排后面，中间状态按严重程度
const statusPriority = { absent: 0, late: 1, leave_sick: 2, leave_personal: 3, early_leave: 4, signed: 99 }
const sortedStudents = computed(() => {
  if (!detailData.value.students) return []
  return [...detailData.value.students].sort((a, b) => {
    const pa = statusPriority[a.status] ?? 99
    const pb = statusPriority[b.status] ?? 99
    if (pa !== pb) return pa - pb
    // 同状态按姓名排序
    return (a.student_name || '').localeCompare(b.student_name || '')
  })
})

// 修改状态弹窗
const modifyTarget = ref(null)
const selectedStatus = ref('')
const modifyNote = ref('')
const submitting = ref(false)

const statusOptions = [
  { value: 'absent',        label: '缺勤',   activeClass: 'bg-rose-100 text-rose-700' },
  { value: 'late',          label: '迟到',   activeClass: 'bg-amber-100 text-amber-700' },
  { value: 'leave_sick',    label: '病假',   activeClass: 'bg-orange-100 text-orange-700' },
  { value: 'leave_personal',label: '事假',   activeClass: 'bg-sky-100 text-sky-700' },
  { value: 'early_leave',   label: '早退',   activeClass: 'bg-violet-100 text-violet-700' },
  { value: 'signed',        label: '已签到', activeClass: 'bg-emerald-100 text-emerald-700' },
]

function openModifyModal(student) {
  modifyTarget.value = student
  selectedStatus.value = student.status || 'absent'
  modifyNote.value = student.note || ''
}

async function doUpdateStatus() {
  if (!modifyTarget.value) return
  submitting.value = true
  try {
    await updateStudentAttendanceStatus(modifyTarget.value.id, selectedStatus.value, modifyNote.value)
    modifyTarget.value.status = selectedStatus.value
    modifyTarget.value.note = modifyNote.value
    // 同步更新 detailData 中的记录
    const stu = detailData.value.students?.find(s => s.id === modifyTarget.value.id)
    if (stu) {
      stu.status = selectedStatus.value
      stu.note = modifyNote.value
    }
    modifyTarget.value = null
  } catch (e) {
    console.error('更新状态失败', e)
    alert('修改失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 删除
const deleteTarget = ref(null)

// 加载课程和班级
async function loadCoursesAndClasses() {
  try {
    const res = await getTeacherCourses()
    console.log('[考勤报表] 课程数据:', res.data?.length, '门课')
    if (res.data) {
      // API 返回 {courses: [...], terms: [...]} 或直接是课程数组
      courses.value = Array.isArray(res.data) ? res.data : (res.data?.courses || [])
      console.log('[考勤报表] 课程IDs:', courses.value.map(c => c.id))
      // 提取所有班级
      const allClasses = []
      for (const course of courses.value) {
        if (course.classes) {
          for (const cls of course.classes) {
            if (!allClasses.find(c => c.id === cls.id)) {
              allClasses.push(cls)
            }
          }
        }
      }
      classes.value = allClasses
      console.log('[考勤报表] 班级IDs:', classes.value.map(c => c.id))
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

// 加载报表
async function loadReports(page = 1) {
  loading.value = true
  currentPage.value = page
  console.log('[考勤报表] 筛选参数:', { courseId: selectedCourse.value, classId: selectedClass.value, page })
  try {
    const res = await getAttendanceReports({
      courseId: selectedCourse.value || undefined,
      classId: selectedClass.value || undefined,
      page,
      pageSize
    })
    console.log('[考勤报表] 返回数据:', res.data?.total, '条, reports:', res.data?.reports?.length)
    if (res.data) {
      reports.value = res.data.reports || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    console.error('加载考勤报表失败', e)
  } finally {
    loading.value = false
  }
}

// 打开详情
async function openDetail(r) {
  try {
    const res = await getAttendanceReportDetail(r.id)
    if (res.data) {
      detailData.value = res.data
      showDetail.value = true
    }
  } catch (e) {
    console.error('加载详情失败', e)
  }
}



// 确认删除
function confirmDelete(r) {
  deleteTarget.value = r
}

// 执行删除
async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteAttendanceReport(deleteTarget.value.id)
    deleteTarget.value = null
    showDetail.value = false
    await loadReports(currentPage.value)
  } catch (e) {
    console.error('删除失败', e)
  }
}

// 分页
function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  loadReports(page)
}

// 格式化日期
function formatDate(ts) {
  if (!ts) return '-'
  const d = new Date(ts)
  if (isNaN(d)) return ts
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// 格式化时间
function formatTime(ts) {
  if (!ts) return '-'
  const d = new Date(ts)
  if (isNaN(d)) return ts
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

// 状态样式（更明亮的颜色块）
function statusClass(status) {
  const map = {
    signed:        'bg-emerald-100 text-emerald-700',
    late:          'bg-amber-100 text-amber-700',
    leave_sick:    'bg-orange-100 text-orange-700',
    leave_personal:'bg-sky-100 text-sky-700',
    early_leave:   'bg-violet-100 text-violet-700',
    absent:        'bg-rose-100 text-rose-700'
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

// 状态文字
function statusText(status) {
  const map = {
    signed:        '已签到',
    late:          '迟到',
    leave_sick:    '病假',
    leave_personal:'事假',
    early_leave:   '早退',
    absent:        '缺勤'
  }
  return map[status] || status
}

// 姓名头像颜色
function avatarColor(name) {
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-amber-500', 'bg-rose-500', 'bg-purple-500', 'bg-teal-500', 'bg-indigo-500', 'bg-orange-500']
  const code = (name || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return colors[code % colors.length]
}

// 导出 Excel
async function exportExcel() {
  exporting.value = true
  try {
    const d = detailData.value
    const rows = [
      // 信息头
      ['考勤报表'],
      ['课程', d.course_name || ''],
      ['班级', d.class_name || ''],
      ['考勤时间', `${formatDate(d.started_at)} ~ ${formatDate(d.ended_at)}`],
      ['出勤率', `${attendanceRate.value}%`],
      [],
      // 表头
      ['序号', '姓名', '学号', '状态', '签到时间']
    ]
    // 数据行（按排序后顺序）
    sortedStudents.value.forEach((s, i) => {
      rows.push([
        i + 1,
        s.student_name || '',
        s.student_number || '',
        statusText(s.status),
        s.sign_time ? formatTime(s.sign_time) : ''
      ])
    })

    const ws = XLSX.utils.aoa_to_sheet(rows)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '考勤详情')

    // 设置列宽
    ws['!cols'] = [
      { wch: 6 },   // 序号
      { wch: 12 },  // 姓名
      { wch: 16 },  // 学号
      { wch: 10 },  // 状态
      { wch: 14 }   // 签到时间
    ]

    const fileName = `${d.course_name || '考勤报表'}_${d.class_name || ''}_${formatDate(d.started_at).replace(/[: ]/g, '-')}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (e) {
    console.error('导出失败', e)
    alert('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadCoursesAndClasses()
  loadReports()
})
</script>
