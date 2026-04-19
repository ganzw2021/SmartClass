<template>
  <div class="space-y-5">

    <!-- 标题栏 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <div class="w-1 h-7 rounded-full bg-gradient-to-b from-blue-500 to-indigo-500"></div>
        <h2 class="text-2xl font-bold text-slate-800">课程管理</h2>
        <span class="ml-2 px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-500">{{ courses.length }} 门</span>
      </div>
      <div class="flex gap-2">
        <button @click="openBatchModal" class="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-all">
          批量开设
        </button>
        <button @click="openCreateModal" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl text-sm font-medium transition-all">
          + 新建课程
        </button>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="flex flex-wrap gap-3 items-center">
      <input v-model="filterName" placeholder="搜索课程名称…" class="px-3 py-2 border border-slate-200 rounded-xl text-sm w-48 focus:outline-none focus:ring-2 focus:ring-blue-200"/>
      <select v-model="filterTeacher" class="px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200">
        <option value="">全部教师</option>
        <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.real_name || t.username }}</option>
      </select>
      <select v-model="filterTerm" class="px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200">
        <option value="">全部学期</option>
        <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
      </select>
      <span class="text-xs text-slate-400 ml-auto">共 {{ filteredCourses.length }} 门课程</span>
    </div>

    <!-- 课程卡片列表 -->
    <div v-if="loading" class="text-center py-12 text-slate-400">加载中…</div>
    <div v-else-if="filteredCourses.length === 0" class="text-center py-12 text-slate-400">
      <div class="text-4xl mb-2">📚</div>
      <div>{{ filterName || filterTeacher || filterTerm ? '未找到匹配课程' : '暂无课程，点击上方按钮添加' }}</div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="c in filteredCourses" :key="c.id"
           class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 hover:shadow-md transition-all">
        <!-- 卡片头部 -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <div class="font-bold text-slate-800 truncate">{{ c.name }}</div>
            <div class="text-xs text-slate-400 mt-0.5">{{ c.id }}</div>
          </div>
          <div class="flex gap-1 ml-2 shrink-0">
            <button @click="openEditModal(c)" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-blue-500 transition-all" title="编辑">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
            </button>
            <button @click="confirmDelete(c)" class="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-all" title="删除">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
        <!-- 信息行 -->
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-if="c.term" class="px-2 py-0.5 rounded-full text-xs bg-indigo-50 text-indigo-500">{{ c.term }}</span>
          <span class="px-2 py-0.5 rounded-full text-xs bg-emerald-50 text-emerald-600">{{ c.teacher_name || '未分配' }}</span>
          <span class="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-500">{{ c.classes?.length || 0 }} 个班级</span>
        </div>
        <!-- 班级标签 -->
        <div v-if="c.classes?.length" class="flex flex-wrap gap-1">
          <span v-for="cls in c.classes.slice(0, 5)" :key="cls.id"
                class="px-2 py-0.5 rounded-md text-xs bg-slate-50 text-slate-600 border border-slate-100">
            {{ cls.name.length > 12 ? cls.name.slice(0,12)+'…' : cls.name }}
          </span>
          <span v-if="c.classes.length > 5" class="px-2 py-0.5 rounded-md text-xs bg-slate-100 text-slate-400">
            +{{ c.classes.length - 5 }}
          </span>
        </div>
        <div v-else class="text-xs text-slate-300 italic">暂未关联班级</div>
      </div>
    </div>

    <!-- ========== 新建/编辑弹窗 ========== -->
    <div v-if="showModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] flex flex-col">
        <!-- 弹窗头部 -->
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div class="font-bold text-slate-800">{{ editingCourse ? '编辑课程' : '新建课程' }}</div>
          <button @click="closeModal" class="text-slate-400 hover:text-slate-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <!-- 弹窗内容 -->
        <div class="px-6 py-4 space-y-4 overflow-y-auto flex-1">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">课程名称 <span class="text-red-400">*</span></label>
            <input v-model="form.name" placeholder="例如：中药学基础" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">课程ID</label>
            <input v-model="form.id" placeholder="留空自动生成" :disabled="!!editingCourse"
                   class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:bg-slate-50 disabled:text-slate-400"/>
            <div class="text-xs text-slate-400 mt-1">留空则自动生成，唯一标识</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">学期</label>
            <input v-model="form.term" placeholder="例如：2024-2025学年第一学期" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">授课教师 <span class="text-red-400">*</span></label>
            <select v-model="form.teacher_id" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200">
              <option value="">请选择教师</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.real_name || t.username }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">关联班级</label>
            <div class="border border-slate-200 rounded-xl p-3 max-h-48 overflow-y-auto space-y-1">
              <label v-for="cls in allClasses" :key="cls.id"
                     class="flex items-center gap-2 py-1 cursor-pointer hover:bg-slate-50 rounded px-1">
                <input type="checkbox" :value="cls.id" v-model="form.class_ids"
                       class="w-4 h-4 rounded accent-blue-500"/>
                <span class="text-sm text-slate-700">{{ cls.name }}</span>
              </label>
              <div v-if="!allClasses.length" class="text-sm text-slate-400 text-center py-2">暂无班级</div>
            </div>
            <div class="text-xs text-slate-400 mt-1">已选 {{ form.class_ids.length }} 个班级</div>
          </div>
        </div>
        <!-- 弹窗底部 -->
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-2 shrink-0">
          <button @click="closeModal" class="px-4 py-2 rounded-xl text-sm text-slate-500 hover:bg-slate-100 transition-all">取消</button>
          <button @click="submitForm" :disabled="saving"
                  class="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-xl text-sm font-medium transition-all">
            {{ saving ? '保存中…' : (editingCourse ? '保存修改' : '创建课程') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========== 批量开设弹窗 ========== -->
    <div v-if="showBatchModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showBatchModal=false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div class="font-bold text-slate-800">批量开设课程</div>
          <button @click="showBatchModal=false" class="text-slate-400 hover:text-slate-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">课程名称（模板）<span class="text-red-400">*</span></label>
            <input v-model="batchForm.name" placeholder="例如：中药学" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"/>
            <div class="text-xs text-slate-400 mt-1">系统将为每个班级创建一门独立课程，课程名自动加上班级后缀</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">学期</label>
            <input v-model="batchForm.term" placeholder="例如：2024-2025学年第一学期" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">授课教师 <span class="text-red-400">*</span></label>
            <select v-model="batchForm.teacher_id" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200">
              <option value="">请选择教师</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.real_name || t.username }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">选择班级（可多选）</label>
            <div class="border border-slate-200 rounded-xl p-3 max-h-48 overflow-y-auto space-y-1">
              <label class="flex items-center gap-2 py-1">
                <input type="checkbox" v-model="batchAll" @change="toggleBatchAll" class="w-4 h-4 rounded accent-blue-500"/>
                <span class="text-sm font-medium text-slate-700">全选</span>
              </label>
              <label v-for="cls in allClasses" :key="cls.id"
                     class="flex items-center gap-2 py-1 cursor-pointer hover:bg-slate-50 rounded px-1">
                <input type="checkbox" :value="cls.id" v-model="batchForm.class_ids"
                       class="w-4 h-4 rounded accent-blue-500"/>
                <span class="text-sm text-slate-700">{{ cls.name }}</span>
              </label>
            </div>
            <div class="text-xs text-slate-400 mt-1">将创建 {{ batchForm.class_ids.length }} 门课程</div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-2">
          <button @click="showBatchModal=false" class="px-4 py-2 rounded-xl text-sm text-slate-500 hover:bg-slate-100 transition-all">取消</button>
          <button @click="submitBatch" :disabled="saving || !batchForm.name || !batchForm.teacher_id || !batchForm.class_ids.length"
                  class="px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-purple-300 text-white rounded-xl text-sm font-medium transition-all">
            {{ saving ? '开设中…' : `确认开设 ${batchForm.class_ids.length} 门课程` }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========== 删除确认弹窗 ========== -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showDeleteModal=false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6">
        <div class="text-center">
          <div class="text-4xl mb-3">🗑️</div>
          <div class="font-bold text-slate-800 mb-2">确认删除课程？</div>
          <div class="text-sm text-slate-500 mb-5">课程 <b class="text-red-500">{{ deleteTarget?.name }}</b> 删除后将无法恢复。</div>
          <div class="flex gap-3 justify-center">
            <button @click="showDeleteModal=false" class="px-4 py-2 rounded-xl text-sm text-slate-500 hover:bg-slate-100 transition-all">取消</button>
            <button @click="doDelete" :disabled="saving"
                    class="px-4 py-2 bg-red-500 hover:bg-red-600 disabled:bg-red-300 text-white rounded-xl text-sm font-medium transition-all">
              {{ saving ? '删除中…' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-xl text-sm font-medium shadow-lg z-50 transition-all"
         :class="toast.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'">
      {{ toast.msg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminCourses, createAdminCourse, updateAdminCourse, deleteAdminCourse, batchCreateCourses,
         getAdminTeachers, getAdminClassList } from '../api.js'

const courses = ref([])
const teachers = ref([])
const allClasses = ref([])
const loading = ref(true)
const saving = ref(false)

// 筛选
const filterName = ref('')
const filterTeacher = ref('')
const filterTerm = ref('')

const terms = computed(() => {
  const set = new Set(courses.value.map(c => c.term).filter(Boolean))
  return [...set].sort().reverse()
})

const filteredCourses = computed(() =>
  courses.value.filter(c => {
    if (filterName.value && !c.name.includes(filterName.value)) return false
    if (filterTeacher.value && c.teacher_id != filterTeacher.value) return false
    if (filterTerm.value && c.term !== filterTerm.value) return false
    return true
  })
)

// 表单
const showModal = ref(false)
const editingCourse = ref(null)
const form = ref({ id: '', name: '', term: '', teacher_id: '', class_ids: [] })

function openCreateModal() {
  editingCourse.value = null
  form.value = { id: '', name: '', term: '', teacher_id: '', class_ids: [] }
  showModal.value = true
}
function openEditModal(c) {
  editingCourse.value = c
  form.value = { id: c.id, name: c.name, term: c.term || '', teacher_id: c.teacher_id || '', class_ids: c.classes?.map(x => x.id) || [] }
  showModal.value = true
}
function closeModal() { showModal.value = false }

async function submitForm() {
  if (!form.value.name) return toast('请填写课程名称', 'error')
  if (!form.value.teacher_id) return toast('请选择授课教师', 'error')
  saving.value = true
  try {
    if (editingCourse.value) {
      await updateAdminCourse(editingCourse.value.id, form.value)
      toast('课程已更新')
    } else {
      await createAdminCourse(form.value)
      toast('课程创建成功')
    }
    closeModal()
    await loadData()
  } catch (e) { toast(e.message || '操作失败', 'error') }
  finally { saving.value = false }
}

// 批量
const showBatchModal = ref(false)
const batchAll = ref(false)
const batchForm = ref({ name: '', term: '', teacher_id: '', class_ids: [] })

function openBatchModal() {
  batchForm.value = { name: '', term: '', teacher_id: '', class_ids: [] }
  batchAll.value = false
  showBatchModal.value = true
}
function toggleBatchAll() {
  batchForm.value.class_ids = batchAll.value ? allClasses.value.map(c => c.id) : []
}

async function submitBatch() {
  if (!batchForm.value.name || !batchForm.value.teacher_id || !batchForm.value.class_ids.length) return
  saving.value = true
  try {
    const r = await batchCreateCourses(batchForm.value)
    toast(r.data?.message || `成功开设 ${batchForm.value.class_ids.length} 门课程`)
    showBatchModal.value = false
    await loadData()
  } catch (e) { toast(e.message || '批量开设失败', 'error') }
  finally { saving.value = false }
}

// 删除
const showDeleteModal = ref(false)
const deleteTarget = ref(null)

function confirmDelete(c) {
  deleteTarget.value = c
  showDeleteModal.value = true
}
async function doDelete() {
  saving.value = true
  try {
    await deleteAdminCourse(deleteTarget.value.id)
    toast('课程已删除')
    showDeleteModal.value = false
    await loadData()
  } catch (e) { toast(e.message || '删除失败', 'error') }
  finally { saving.value = false }
}

// Toast
const toast_data = ref({ show: false, msg: '', type: 'success' })
const toast = (msg, type = 'success') => {
  toast_data.value = { show: true, msg, type }
  setTimeout(() => { toast_data.value.show = false }, 2500)
}

async function loadData() {
  loading.value = true
  try {
    const [cr, tr, cl] = await Promise.all([
      getAdminCourses(), getAdminTeachers(), getAdminClassList()
    ])
    courses.value = cr.data || []
    teachers.value = tr.data || []
    allClasses.value = cl.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(loadData)
</script>
