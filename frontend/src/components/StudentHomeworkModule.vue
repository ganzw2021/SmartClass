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
      <button @click="loadHomework" class="ml-3 underline">重试</button>
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
          <div class="flex-1 min-w-0 break-words">
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
            <p v-if="hw.draft" class="mt-2 break-all text-xs text-slate-500">已暂存：{{ hw.draft.file_name }}</p>

            <!-- 提交信息 -->
            <p v-if="!hw.submitted" class="mt-3 text-xs text-slate-500">作业得分：0.0分（未提交）</p>
            <div v-if="hw.submitted && hw.submission" class="mt-3 flex flex-col gap-1 text-xs text-slate-400">
              <div class="flex items-center gap-4">
                <span v-if="hw.submission.score !== null && hw.submission.score !== undefined">
                  得分：<strong class="text-blue-600">{{ formatScore(hw.submission.score) }}分</strong>
                </span>
                <span v-else-if="hw.submission.auto_score !== null && hw.submission.auto_score !== undefined">
                  自动评分：<strong class="text-orange-500">{{ formatScore(hw.submission.auto_score) }}分</strong>
                </span>
                <span>提交于 {{ formatDate(hw.submission.submitted_at) }}</span>
              </div>
              <div v-if="hw.submission.feedback" class="text-yellow-600 truncate">
                评语：{{ hw.submission.feedback }}
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex shrink-0 flex-col gap-2">
            <button type="button" @click="openDraft(hw)" class="px-3 py-1.5 text-xs bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200">暂存文件</button>
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
            <button v-if="hw.submitted" @click="withdrawSubmission(hw)" :disabled="withdrawingId !== null || submitting" class="px-3 py-1.5 text-xs bg-red-50 text-red-600 rounded-lg hover:bg-red-100 disabled:opacity-50">
              {{ withdrawingId === hw.id ? '撤回中…' : '撤回提交' }}
            </button>
            <span v-if="isExpired(hw.deadline) && !hw.submitted" class="px-3 py-1.5 text-xs bg-red-50 text-red-400 rounded-lg text-center">
              未提交
            </span>
            <span v-if="isExpired(hw.deadline) && hw.submitted" class="px-3 py-1.5 text-xs bg-green-50 text-green-600 rounded-lg text-center">
              已提交
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交作业弹窗 -->
    <Teleport to="body">
      <div v-if="draftHw" class="fixed inset-0 bg-black/40 z-[100] flex items-end sm:items-center justify-center sm:p-6">
        <div role="dialog" aria-modal="true" aria-labelledby="homework-draft-title" class="w-full sm:max-w-lg max-h-[90vh] overflow-y-auto bg-white rounded-t-3xl sm:rounded-3xl p-5 sm:p-8 shadow-2xl space-y-4">
          <h3 id="homework-draft-title" class="text-lg font-bold text-slate-800 break-words">暂存文件：{{ draftHw.title }}</h3>
          <p class="text-sm text-slate-600">每份作业只能暂存一个文件，重新上传成功后会覆盖原文件。暂存不算正式提交。</p>
          <div v-if="draftHw.draft" class="rounded-xl bg-slate-50 p-3 text-sm">
            <p class="break-all font-medium">{{ draftHw.draft.file_name }}</p>
            <p class="mt-1 text-xs text-slate-500">暂存于 {{ formatDate(draftHw.draft.updated_at) }}</p>
            <button type="button" @click="downloadDraft" :disabled="draftSaving || draftDownloading" class="mt-2 text-blue-600 underline disabled:opacity-50">{{ draftDownloading ? '下载中…' : '下载暂存文件' }}</button>
          </div>
          <div>
            <label for="homework-draft-file" class="block mb-1 text-sm font-medium">选择暂存文件（最多 90 MB）</label>
            <input id="homework-draft-file" ref="draftInput" type="file" @change="selectDraftFile" :disabled="draftSaving" class="w-full text-sm" />
          </div>
          <p v-if="draftError" role="alert" class="text-sm text-red-600">{{ draftError }}</p>
          <p v-if="draftMessage" role="status" class="text-sm text-green-700">{{ draftMessage }}</p>
          <div class="flex gap-3">
            <button type="button" @click="draftHw = null" :disabled="draftSaving" class="flex-1 rounded-xl border py-3 disabled:opacity-50">关闭</button>
            <button type="button" @click="saveDraft" :disabled="!draftFile || draftSaving || draftDownloading" class="flex-1 rounded-xl bg-blue-600 py-3 text-white disabled:opacity-50">{{ draftSaving ? `上传中 ${draftProgress}%` : draftHw.draft ? '覆盖暂存' : '保存暂存' }}</button>
          </div>
        </div>
      </div>
      <div v-if="submitHw" class="fixed inset-0 bg-black/40 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-6">
        <div role="dialog" aria-modal="true" aria-labelledby="student-homework-submit-title" class="relative bg-white rounded-t-3xl sm:rounded-[32px] w-full sm:max-w-lg sm:p-8 p-5 shadow-2xl overflow-y-auto max-h-[90vh] sm:max-h-[85vh]">
          <!-- 移动端：顶部拖动条 -->
          <div class="sm:hidden w-12 h-1 bg-slate-300 rounded-full mx-auto mb-4"></div>
          
          <!-- 上传时保留弹窗，避免丢失提交状态 -->
          <button type="button" @click="submitHw = null" :disabled="submitting" aria-label="关闭作业提交" class="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 text-slate-500 disabled:opacity-40">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
          
          <h3 id="student-homework-submit-title" class="text-lg font-bold text-slate-800 mb-4 pr-10 break-words">提交作业：{{ submitHw.title }}</h3>

          <!-- 作业描述 -->
          <div v-if="submitHw.description" class="bg-slate-50 rounded-xl p-4 text-sm text-slate-600 mb-4">
            {{ submitHw.description }}
          </div>

          <!-- 文件选择 -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-slate-600 mb-2">选择文件</label>
            <input type="file" @change="handleFileSelect" :disabled="submitting" class="w-full text-sm" />
            <p class="mt-2 text-xs text-slate-500">单个文件不超过 90 MB，上传期间请保持页面开启。</p>
          </div>

          <!-- 备注 -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-slate-600 mb-2">备注（可选）</label>
            <textarea v-model="submitNote" :disabled="submitting" rows="2" class="w-full border border-slate-200 rounded-xl p-3 text-sm outline-none focus:border-blue-400" placeholder="可填写提交说明..."></textarea>
          </div>

          <div v-if="submitError" class="bg-red-50 text-red-600 p-3 rounded-xl text-sm mb-4">{{ submitError }}</div>

          <div class="flex gap-3 mt-6">
            <button @click="submitHw = null" :disabled="submitting" class="disabled:opacity-40 flex-1 py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50">取消</button>
            <button
              @click="doSubmit"
              :disabled="submitting || !selectedFile"
              class="flex-1 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              {{ submitting ? `上传中 ${uploadProgress}%` : '确认提交' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 作业详情弹窗 -->
      <div v-if="detailHw" class="fixed inset-0 bg-black/40 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-6">
        <div role="dialog" aria-modal="true" aria-labelledby="student-homework-detail-title" class="bg-white rounded-t-3xl sm:rounded-[32px] w-full sm:max-w-lg sm:p-8 p-5 shadow-2xl overflow-y-auto max-h-[90vh] sm:max-h-[85vh] relative">
          <!-- 移动端：顶部拖动条 -->
          <div class="sm:hidden w-12 h-1 bg-slate-300 rounded-full mx-auto mb-4"></div>
          
          <div class="sticky top-0 z-10 flex items-start justify-between gap-3 bg-white pb-4">
            <h3 id="student-homework-detail-title" class="min-w-0 break-words text-lg font-bold text-slate-800">{{ detailHw.title }}</h3>
            <button type="button" @click="detailHw = null" aria-label="关闭作业详情" title="关闭" class="shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-500">
              <svg aria-hidden="true" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="space-y-3 text-sm">
            <p v-if="!detailHw.submission" class="text-slate-500">未提交，当前作业计 0.0 分。</p>
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
                  {{ detailHw.submission.score !== null && detailHw.submission.score !== undefined ? `已评分 ${formatScore(detailHw.submission.score)}分` : '已提交' }}
                </span>
              </div>
              <p v-if="detailHw.submission.content" class="whitespace-pre-wrap break-words text-slate-600">备注：{{ detailHw.submission.content }}</p>
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
                <span class="text-blue-600 font-medium">{{ formatScore(detailHw.submission.auto_score) }}分</span>
              </div>
              <!-- 评分详情（JSON格式） -->
              <div v-if="detailHw.submission.auto_grade_details" class="mt-2 p-2 bg-white rounded-lg text-xs">
                <div class="text-slate-500 mb-1">评分详情：</div>
                <pre class="text-slate-600 whitespace-pre-wrap break-words">{{ typeof detailHw.submission.auto_grade_details === 'string' ? detailHw.submission.auto_grade_details : JSON.stringify(detailHw.submission.auto_grade_details, null, 2) }}</pre>
              </div>
              <!-- 教师评语 -->
              <div v-if="detailHw.submission.feedback" class="flex gap-2">
                <span class="text-slate-500">教师评语：</span>
                <span class="text-slate-700">{{ detailHw.submission.feedback }}</span>
              </div>
              <div class="text-xs text-slate-400 mt-1">
                提交时间：{{ formatDate(detailHw.submission.submitted_at) }}
              </div>
            </div>
          </div>
          <button type="button" @click="detailHw = null" class="mt-6 w-full py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50">关闭</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onDeactivated, watch } from 'vue'
import { courseOptions, formatScore, studentError } from '../studentHelpers.js'
import { getStudentHomework, getStudentCourses, submitHomework, withdrawHomework, saveHomeworkDraft, downloadHomeworkDraft } from '../api.js'

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
const uploadProgress = ref(0)
const withdrawingId = ref(null)
const draftHw = ref(null)
const draftFile = ref(null)
const draftInput = ref(null)
const draftSaving = ref(false)
const draftDownloading = ref(false)
const draftProgress = ref(0)
const draftError = ref('')
const draftMessage = ref('')
let loadVersion = 0

async function loadHomework() {
  const version = ++loadVersion
  error.value = ''
  loading.value = true
  try {
    const res = await getStudentHomework(selectedCourseId.value)
    if (version !== loadVersion) return
    if (res.success) {
      homeworkList.value = res.data || []
    } else {
      error.value = res.message || '加载作业失败'
    }
  } catch (e) {
    if (version === loadVersion) error.value = studentError(e)
  } finally {
    if (version === loadVersion) loading.value = false
  }
}

async function loadCourses() {
  try {
    const res = await getStudentCourses()
    if (res.success) {
      // 兼容新格式 {courses, terms} 和旧格式 []
      if (res.data && res.data.courses) {
        courses.value = courseOptions(res.data)
      } else if (Array.isArray(res.data)) {
        courses.value = courseOptions(res.data)
      }
    }
  } catch (e) {}
}

watch(selectedCourseId, loadHomework)

onMounted(loadCourses)
onActivated(loadHomework)
onDeactivated(() => {
  ++loadVersion
  detailHw.value = null
  if (!submitting.value) submitHw.value = null
  if (!draftSaving.value) draftHw.value = null
})

function viewDetail(hw) {
  detailHw.value = hw
}

function openDraft(hw) {
  if (draftSaving.value || draftDownloading.value) return
  draftHw.value = hw
  draftFile.value = null
  draftError.value = ''
  draftMessage.value = ''
}

function selectDraftFile(event) {
  const file = event.target.files?.[0]
  draftError.value = ''
  draftMessage.value = ''
  if (file?.size > 90 * 1024 * 1024) {
    draftFile.value = null
    event.target.value = ''
    draftError.value = '文件超过 90 MB，请压缩后再上传'
    return
  }
  draftFile.value = file || null
}

async function saveDraft() {
  if (!draftHw.value || !draftFile.value || draftSaving.value || draftDownloading.value) return
  const hw = draftHw.value
  draftSaving.value = true
  draftProgress.value = 0
  draftError.value = ''
  draftMessage.value = ''
  try {
    const res = await saveHomeworkDraft(hw.id, draftFile.value, event => {
      if (event.total) draftProgress.value = Math.min(100, Math.round(event.loaded * 100 / event.total))
    })
    if (!res.success) throw new Error(res.message || '暂存失败')
    hw.draft = res.data
    const listed = homeworkList.value.find(item => item.id === hw.id)
    if (listed) listed.draft = res.data
    draftFile.value = null
    if (draftInput.value) draftInput.value.value = ''
    draftMessage.value = '文件已暂存，尚未正式提交'
  } catch (e) {
    draftError.value = studentError(e, e.code === 'ECONNABORTED' ? '等待超时，请刷新后确认暂存结果' : '暂存失败，请稍后重试')
  } finally {
    draftSaving.value = false
  }
}

async function downloadDraft() {
  if (!draftHw.value?.draft || draftSaving.value || draftDownloading.value) return
  const { id, draft } = draftHw.value
  draftDownloading.value = true
  draftError.value = ''
  try {
    const blob = await downloadHomeworkDraft(id)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = draft.file_name
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 30000)
  } catch (e) {
    draftError.value = studentError(e, '下载暂存文件失败，请刷新后重试')
  } finally {
    draftDownloading.value = false
  }
}

function openSubmit(hw) {
  if (submitting.value || withdrawingId.value !== null) return
  submitHw.value = hw
  selectedFile.value = null
  submitNote.value = hw.submission?.content || ''
  submitError.value = ''
}

async function withdrawSubmission(hw) {
  if (!hw.submitted || submitting.value || withdrawingId.value !== null) return
  const deadlineHint = isExpired(hw.deadline) ? '该作业已截止，撤回后将无法再次提交。' : '截止前可重新提交。'
  if (!window.confirm(`确定撤回「${hw.title}」吗？本次提交及评分将取消，该作业计0.0分，并同步更新天梯榜。${deadlineHint}`)) return
  withdrawingId.value = hw.id
  try {
    const res = await withdrawHomework(hw.id)
    if (!res.success) throw new Error(res.message || '撤回失败')
    hw.submitted = false
    hw.submission = null
    if (detailHw.value?.id === hw.id) detailHw.value = null
    await loadHomework()
  } catch (e) {
    error.value = studentError(e, e.message || '撤回失败，请稍后重试')
  } finally {
    withdrawingId.value = null
  }
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file?.size > 90 * 1024 * 1024) {
    selectedFile.value = null
    e.target.value = ''
    submitError.value = '文件超过 90 MB，请压缩后再上传'
    return
  }
  submitError.value = ''
  selectedFile.value = file || null
}

async function doSubmit() {
  if (submitting.value || !submitHw.value || !selectedFile.value) return
  const homeworkId = submitHw.value.id
  uploadProgress.value = 0
  submitting.value = true
  submitError.value = ''
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  if (submitNote.value) formData.append('content', submitNote.value)
  try {
    const res = await submitHomework(homeworkId, formData, event => {
      if (event.total) uploadProgress.value = Math.min(100, Math.round(event.loaded * 100 / event.total))
    })
    if (res.success) {
      submitHw.value = null
      await loadHomework()
    } else {
      submitError.value = res.message || '提交失败'
    }
  } catch (e) {
    submitError.value = e.code === 'ECONNABORTED' ? '等待超时，请先刷新作业列表确认是否已提交，再决定是否重试' : studentError(e, '上传失败，请检查网络后重试')
  } finally {
    submitting.value = false
  }
}

function formatDate(d) {
  if (!d) return '未设置截止时间'
  const date = new Date(d)
  if (Number.isNaN(date.getTime())) return '时间暂不可用'
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
