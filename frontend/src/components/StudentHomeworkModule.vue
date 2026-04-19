<template>
  <div class="space-y-6">
    <!-- 课程筛选 -->
    <div v-if="courses.length > 0" class="flex gap-2 flex-wrap">
      <button
        @click="selectedCourseId = null"
        :class="['px-4 py-2 rounded-full text-sm font-medium transition-colors',
          !selectedCourseId ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-blue-50']"
      >
        全部
      </button>
      <button
        v-for="c in courses"
        :key="c.id"
        @click="selectedCourseId = c.id"
        :class="['px-4 py-2 rounded-full text-sm font-medium transition-colors',
          selectedCourseId === c.id ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:bg-blue-50']"
      >
        {{ c.name }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="bg-red-50 border border-red-100 rounded-2xl p-4 text-red-600 text-sm">
      {{ error }}
    </div>

    <!-- 作业列表 -->
    <div v-else class="space-y-4">
      <div v-if="homeworkList.length === 0" class="bg-white rounded-2xl p-8 text-center text-slate-400">
        暂无作业
      </div>

      <div
        v-for="hw in homeworkList"
        :key="hw.id"
        :class="['rounded-2xl shadow-sm border p-5 hover:shadow-md transition-shadow',
          isExpired(hw.deadline) ? 'bg-slate-50 border-slate-200' : 'bg-white border-blue-50']"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <h4 class="font-bold text-slate-800">{{ hw.title }}</h4>
              <!-- 过期标签 -->
              <span v-if="isExpired(hw.deadline)" class="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500">
                已截止
              </span>
              <span v-else :class="['px-2 py-0.5 rounded text-xs font-medium',
                hw.submitted && hw.submission?.score !== null && hw.submission?.score !== undefined ? 'bg-purple-50 text-purple-600' :
                hw.submitted ? 'bg-green-50 text-green-600' :
                'bg-amber-50 text-amber-600']">
                {{ hw.submitted && hw.submission?.score !== null && hw.submission?.score !== undefined ? '已评分' : hw.submitted ? '已提交' : '待提交' }}
              </span>
            </div>
            <p :class="['text-sm mb-2', isExpired(hw.deadline) ? 'text-slate-400' : 'text-slate-500']">
              {{ hw.course_name }} · {{ formatDate(hw.deadline) }}
              <span v-if="isExpired(hw.deadline)" class="text-red-500 ml-1">（已截止）</span>
              <span v-else-if="isNearDeadline(hw.deadline)" class="text-orange-500 ml-1">（即将截止）</span>
            </p>
            <p v-if="hw.description" class="text-sm text-slate-400 line-clamp-2">{{ hw.description }}</p>

            <!-- 提交信息 -->
            <div v-if="hw.submitted && hw.submission" class="mt-3 flex items-center gap-4 text-xs text-slate-400">
              <span v-if="hw.submission.score !== null && hw.submission.score !== undefined">
                得分：<strong class="text-blue-600">{{ hw.submission.score }}分</strong>
              </span>
              <span v-else-if="hw.submission.auto_score !== null && hw.submission.auto_score !== undefined">
                自动评分：<strong class="text-orange-500">{{ hw.submission.auto_score }}分</strong>
              </span>
              <span>提交于 {{ formatDate(hw.submission.submitted_at) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex flex-col gap-2">
            <button
              @click="viewDetail(hw)"
              class="px-3 py-1.5 text-xs bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
            >
              查看
            </button>
            <button
              v-if="!hw.submitted && !isExpired(hw.deadline)"
              @click="openSubmit(hw)"
              class="px-3 py-1.5 text-xs bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
            >
              提交
            </button>
            <button
              v-if="hw.submitted && !isExpired(hw.deadline)"
              @click="openSubmit(hw)"
              class="px-3 py-1.5 text-xs bg-amber-50 text-amber-600 rounded-lg hover:bg-amber-100 transition-colors"
            >
              重新提交
            </button>
            <!-- 已过期提示 -->
            <span v-if="isExpired(hw.deadline) && !hw.submitted" class="px-3 py-1.5 text-xs bg-red-50 text-red-400 rounded-lg text-center">
              未提交
            </span>
            <span v-if="isExpired(hw.deadline) && hw.submitted" class="px-3 py-1.5 text-xs bg-green-50 text-green-600 rounded-lg text-center">
              已按时提交
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交作业弹窗 -->
    <Teleport to="body">
      <div v-if="submitHw" class="fixed inset-0 bg-black/40 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-6" @click.self="submitHw = null">
        <div class="bg-white rounded-t-3xl sm:rounded-[32px] w-full sm:max-w-lg sm:p-8 p-5 shadow-2xl overflow-y-auto max-h-[90vh] sm:max-h-[85vh]">
          <!-- 移动端：顶部拖动条 -->
          <div class="sm:hidden w-12 h-1 bg-slate-300 rounded-full mx-auto mb-4"></div>
          
          <!-- 关闭按钮（移动端右上角） -->
          <button @click="submitHw = null" class="sm:hidden absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-100 text-slate-500">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
          
          <h3 class="text-lg font-bold text-slate-800 mb-4 pr-8 sm:pr-0">提交作业：{{ submitHw.title }}</h3>

          <!-- 作业描述 -->
          <div v-if="submitHw.description" class="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 mb-4">
            {{ submitHw.description }}
          </div>

          <!-- 文件选择 -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-slate-600 mb-2">选择文件</label>
            <input type="file" @change="handleFileSelect" class="w-full text-sm" />
          </div>

          <!-- 备注 -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-slate-600 mb-2">备注（可选）</label>
            <textarea v-model="submitNote" rows="2" class="w-full border border-slate-200 rounded-xl p-3 text-sm outline-none focus:border-blue-400" placeholder="可填写提交说明..."></textarea>
          </div>

          <div v-if="submitError" class="bg-red-50 text-red-600 p-3 rounded-xl text-sm mb-4">{{ submitError }}</div>

          <div class="flex gap-3 mt-6">
            <button @click="submitHw = null" class="flex-1 py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50">取消</button>
            <button
              @click="doSubmit"
              :disabled="submitting || !selectedFile"
              class="flex-1 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              {{ submitting ? '提交中...' : '确认提交' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 作业详情弹窗 -->
      <div v-if="detailHw" class="fixed inset-0 bg-black/40 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-6" @click.self="detailHw = null">
        <div class="bg-white rounded-t-3xl sm:rounded-[32px] w-full sm:max-w-lg sm:p-8 p-5 shadow-2xl overflow-y-auto max-h-[90vh] sm:max-h-[85vh] relative">
          <!-- 移动端：顶部拖动条 -->
          <div class="sm:hidden w-12 h-1 bg-slate-300 rounded-full mx-auto mb-4"></div>
          
          <!-- 关闭按钮（移动端右上角） -->
          <button @click="detailHw = null" class="sm:hidden absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-100 text-slate-500">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
          
          <h3 class="text-lg font-bold text-slate-800 mb-4 pr-8 sm:pr-0">{{ detailHw.title }}</h3>
          <div class="space-y-3 text-sm">
            <div class="flex gap-2">
              <span class="text-slate-500">课程：</span><span class="text-slate-700 font-medium">{{ detailHw.course_name }}</span>
            </div>
            <div class="flex gap-2">
              <span class="text-slate-500">截止时间：</span><span class="text-slate-700 font-medium">{{ formatDate(detailHw.deadline) }}</span>
            </div>
            <div v-if="detailHw.description" class="flex gap-2">
              <span class="text-slate-500">描述：</span>
              <span class="text-slate-700">{{ detailHw.description }}</span>
            </div>
            <div v-if="detailHw.attachments?.length" class="flex gap-2">
              <span class="text-slate-500 shrink-0">附件：</span>
              <div class="flex flex-col gap-1">
                <button
                  v-for="att in detailHw.attachments" :key="att.id"
                  @click="downloadHwAttachment(att)"
                  class="text-blue-600 hover:underline text-left flex items-center gap-1">
                  📎 {{ att.file_name }}
                </button>
              </div>
            </div>
            <div v-if="detailHw.submission" class="mt-3 p-3 bg-slate-50 rounded-xl space-y-2">
              <div class="flex gap-2">
                <span class="text-slate-500">提交状态：</span>
                <span :class="detailHw.submission.score !== null && detailHw.submission.score !== undefined ? 'text-purple-600 font-bold' : 'text-green-600'">
                  {{ detailHw.submission.score !== null && detailHw.submission.score !== undefined ? `已评分 ${detailHw.submission.score}分` : '已提交' }}
                </span>
              </div>
              <!-- 我提交的文件 -->
              <div v-if="detailHw.submission.attachments?.length" class="flex gap-2">
                <span class="text-slate-500 shrink-0">我的提交：</span>
                <div class="flex flex-col gap-1">
                  <button
                    v-for="att in detailHw.submission.attachments" :key="att.id"
                    @click="downloadSubAttachment(att)"
                    class="text-green-600 hover:underline text-left flex items-center gap-1">
                    📄 {{ att.file_name }}
                  </button>
                </div>
              </div>
              <!-- 自动评分详情 -->
              <div v-if="detailHw.submission.auto_grade_message" class="flex gap-2">
                <span class="text-slate-500">自动评语：</span>
                <span class="text-slate-700">{{ detailHw.submission.auto_grade_message }}</span>
              </div>
              <div v-if="detailHw.submission.auto_score !== null && detailHw.submission.auto_score !== undefined" class="flex gap-2">
                <span class="text-slate-500">自动评分：</span>
                <span class="text-blue-600 font-medium">{{ detailHw.submission.auto_score }}分</span>
              </div>
              <!-- 评分详情（JSON格式） -->
              <div v-if="detailHw.submission.auto_grade_details" class="mt-2 p-2 bg-white rounded-lg text-xs">
                <div class="text-slate-500 mb-1">评分详情：</div>
                <pre class="text-slate-600 whitespace-pre-wrap">{{ typeof detailHw.submission.auto_grade_details === 'string' ? detailHw.submission.auto_grade_details : JSON.stringify(detailHw.submission.auto_grade_details, null, 2) }}</pre>
              </div>
              <!-- 教师评语 -->
              <div v-if="detailHw.submission.comment" class="flex gap-2">
                <span class="text-slate-500">教师评语：</span>
                <span class="text-slate-700">{{ detailHw.submission.comment }}</span>
              </div>
              <div class="text-xs text-slate-400 mt-1">
                提交时间：{{ formatDate(detailHw.submission.submitted_at) }}
              </div>
            </div>
          </div>
          <button @click="detailHw = null" class="mt-6 w-full py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 sm:hidden">关闭</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getStudentHomework, getStudentCourses, submitHomework } from '../api.js'

const courses = ref([])
const homeworkList = ref([])
const selectedCourseId = ref(null)
const loading = ref(true)
const error = ref('')

const submitHw = ref(null)
const detailHw = ref(null)
const selectedFile = ref(null)
const submitNote = ref('')
const submitting = ref(false)
const submitError = ref('')

async function loadHomework() {
  loading.value = true
  try {
    const res = await getStudentHomework(selectedCourseId.value)
    if (res.success) {
      homeworkList.value = res.data || []
    } else {
      error.value = res.message || '加载作业失败'
    }
  } catch (e) {
    error.value = '网络错误'
  } finally {
    loading.value = false
  }
}

async function loadCourses() {
  try {
    const res = await getStudentCourses()
    if (res.success) {
      // 兼容新格式 {courses, terms} 和旧格式 []
      if (res.data && res.data.courses) {
        courses.value = res.data.courses || []
      } else if (Array.isArray(res.data)) {
        courses.value = res.data || []
      }
    }
  } catch (e) {}
}

watch(selectedCourseId, loadHomework)

onMounted(async () => {
  await loadCourses()
  await loadHomework()
})

function viewDetail(hw) {
  detailHw.value = hw
}

function openSubmit(hw) {
  submitHw.value = hw
  selectedFile.value = null
  submitNote.value = ''
  submitError.value = ''
}

function handleFileSelect(e) {
  selectedFile.value = e.target.files[0]
}

async function doSubmit() {
  if (!selectedFile.value) return
  submitting.value = true
  submitError.value = ''
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  if (submitNote.value) formData.append('note', submitNote.value)
  try {
    const res = await submitHomework(submitHw.value.id, formData)
    if (res.success) {
      submitHw.value = null
      await loadHomework()
    } else {
      submitError.value = res.message || '提交失败'
    }
  } catch (e) {
    submitError.value = '网络错误'
  } finally {
    submitting.value = false
  }
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
}

// 检查作业是否已过期
function isExpired(deadline) {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

// 检查作业是否临近截止（24小时内）
function isNearDeadline(deadline) {
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const diff = deadlineDate - now
  return diff > 0 && diff <= 24 * 60 * 60 * 1000 // 24小时以内
}

function downloadHwAttachment(att) {
  const token = sessionStorage.getItem('tc_student_token')
  const url = `/api/homework/attachments/${att.id}/download?token=${token}`
  const a = document.createElement('a')
  a.href = url; a.target = '_blank'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
}

function downloadSubAttachment(att) {
  const token = sessionStorage.getItem('tc_student_token')
  const url = `/api/submissions/attachments/${att.id}/download?token=${token}`
  const a = document.createElement('a')
  a.href = url; a.target = '_blank'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
}
</script>
