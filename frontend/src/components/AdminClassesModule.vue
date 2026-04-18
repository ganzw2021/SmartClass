<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-2xl font-bold text-slate-800">班级管理</h2>
      <div class="flex items-center gap-3">
        <input v-model="classSearch" type="text" placeholder="搜索班级名称..."
          class="border border-slate-200 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-blue-400 w-48" />
        <button @click="showAddClassModal = true" class="btn-green px-5 py-2.5 rounded-xl text-sm font-bold">
          + 新增班级
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12 text-slate-400">加载中...</div>

    <!-- 无搜索结果提示 -->
    <div v-else-if="classSearch && filteredClasses.length === 0" class="text-center py-12 text-slate-400">
      未找到匹配"{{ classSearch }}"的班级
    </div>

    <!-- 班级列表 -->
    <div v-else-if="filteredClasses.length > 0 || !classSearch" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="cls in filteredClasses"
        :key="cls.id"
        class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 hover:shadow-md transition-shadow cursor-pointer"
        :class="{ 'ring-2 ring-blue-400': selectedClass?.id === cls.id }"
        @click="selectClass(cls)"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-bold text-slate-800">{{ cls.name }}</h3>
            <p class="text-xs text-slate-400 mt-1">ID: {{ cls.id }}</p>
          </div>
          <div class="flex gap-1">
            <button @click.stop="editClass(cls)" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-blue-500 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click.stop="confirmDeleteClass(cls)" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-red-500 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 text-xs font-bold">
              {{ cls.student_count }}
            </span>
            <span class="text-sm text-slate-500">名学生</span>
          </div>
          <span class="text-xs text-slate-400">{{ cls.description || '无描述' }}</span>
        </div>
      </div>
    </div>

    <div v-if="!loading && !classSearch && classes.length === 0" class="text-center py-12 text-slate-400">
      暂无班级，点击右上角添加
    </div>

    <!-- 学生详情面板 -->
    <div v-if="selectedClass" class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div>
          <h3 class="font-bold text-lg text-slate-800">{{ selectedClass.name }} - 学生列表</h3>
          <p class="text-sm text-slate-400">共 {{ filteredStudents.length }} 名学生{{ studentSearch ? `（搜索"${studentSearch}"）` : '' }}</p>
        </div>
        <div class="flex gap-2 flex-wrap">
          <input v-model="studentSearch" type="text" placeholder="搜索学生姓名/学号..."
            class="border border-slate-200 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-blue-400 w-48" />
          <button @click="showAddStudentModal = true" class="btn-green px-4 py-2 rounded-xl text-sm font-bold">
            + 添加
          </button>
          <button @click="openBatchImport" class="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-indigo-100 transition-colors">
            批量添加
          </button>
          <button v-if="selectedStudents.length > 0" @click="batchDeleteStudents" class="bg-red-50 text-red-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-red-100 transition-colors">
            删除已选({{ selectedStudents.length }})
          </button>
          <button @click="createAccountsForClass" class="bg-orange-50 text-orange-600 px-4 py-2 rounded-xl text-sm font-bold hover:bg-orange-100 transition-colors">
            批量建账号
          </button>
        </div>
      </div>

      <!-- 全选复选框 -->
      <div class="mb-2 flex items-center gap-2">
        <input type="checkbox" id="selectAll" v-model="selectAll" @change="toggleSelectAll"
          class="w-4 h-4 rounded border-slate-300 text-blue-500 focus:ring-blue-400" />
        <label for="selectAll" class="text-xs text-slate-500 cursor-pointer">全选</label>
        <button v-if="selectedStudents.length > 0" @click="selectedStudents = []" class="text-xs text-slate-400 hover:text-slate-600">取消选择</button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left py-3 px-2 text-slate-500 font-medium w-8"></th>
              <th class="text-left py-3 px-2 text-slate-500 font-medium">序号</th>
              <th class="text-left py-3 px-2 text-slate-500 font-medium">姓名</th>
              <th class="text-left py-3 px-2 text-slate-500 font-medium">学号</th>
              <th class="text-left py-3 px-2 text-slate-500 font-medium">账号状态</th>
              <th class="text-left py-3 px-2 text-slate-500 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(s, i) in filteredStudents" :key="s.id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="py-3 px-2">
                <input type="checkbox" :value="s.id" v-model="selectedStudents" class="w-4 h-4 rounded border-slate-300 text-blue-500" />
              </td>
              <td class="py-3 px-2 text-slate-400">{{ i + 1 }}</td>
              <td class="py-3 px-2 font-medium text-slate-700">{{ s.name }}</td>
              <td class="py-3 px-2 text-slate-500">{{ s.student_number || '-' }}</td>
              <td class="py-3 px-2">
                <span v-if="s.account_id" class="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-bold">已建账号</span>
                <span v-else class="bg-slate-100 text-slate-400 px-2 py-0.5 rounded-full text-xs font-bold">未建账号</span>
              </td>
              <td class="py-3 px-2">
                <button v-if="s.account_id" @click="resetStudentPassword(s)" class="text-xs text-orange-500 hover:underline mr-2">重置密码</button>
                <button @click="confirmDeleteStudent(s)" class="text-xs text-red-400 hover:text-red-600 hover:underline">删除</button>
              </td>
            </tr>
            <tr v-if="filteredStudents.length === 0">
              <td colspan="6" class="py-8 text-center text-slate-400">
                {{ studentSearch ? '未找到匹配的学生' : '暂无学生' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑班级弹窗 -->
    <Teleport to="body">
      <div v-if="showAddClassModal || showEditClassModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" @click.self="closeClassModals">
        <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="font-bold text-lg text-slate-800 mb-4">{{ showEditClassModal ? '编辑班级' : '新增班级' }}</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">班级名称</label>
              <input v-model="classForm.name" type="text" placeholder="如：2024级中药学1班" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">班级描述（选填）</label>
              <input v-model="classForm.description" type="text" placeholder="如：中药学专业" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="closeClassModals" class="flex-1 py-3 rounded-xl border-2 border-slate-100 text-slate-500 font-bold">取消</button>
            <button @click="showEditClassModal ? saveClassEdit() : saveNewClass()" class="flex-1 py-3 rounded-xl bg-blue-600 text-white font-bold hover:bg-blue-700 transition-colors">
              {{ showEditClassModal ? '保存' : '添加' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 新增学生弹窗 -->
    <Teleport to="body">
      <div v-if="showAddStudentModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" @click.self="showAddStudentModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="font-bold text-lg text-slate-800 mb-4">添加学生 - {{ selectedClass?.name }}</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">姓名</label>
              <input v-model="studentForm.name" type="text" placeholder="请输入学生姓名" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">学号（选填）</label>
              <input v-model="studentForm.student_number" type="text" placeholder="请输入学号" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showAddStudentModal = false" class="flex-1 py-3 rounded-xl border-2 border-slate-100 text-slate-500 font-bold">取消</button>
            <button @click="saveNewStudent" class="flex-1 py-3 rounded-xl bg-green-600 text-white font-bold hover:bg-green-700 transition-colors">添加</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 批量添加学生弹窗 -->
    <Teleport to="body">
      <div v-if="showBatchImportModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" @click.self="closeBatchImport">
        <div class="bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl max-h-[85vh] flex flex-col">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-lg text-slate-800">批量添加学生 - {{ selectedClass?.name }}</h3>
            <button @click="closeBatchImport" class="text-slate-400 hover:text-slate-600 p-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 说明 -->
          <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-3 mb-4 text-xs text-indigo-700 leading-relaxed">
            <p class="font-bold mb-1">📋 输入格式（每行一条学生信息）：</p>
            <p>每行一条，格式：<span class="font-mono bg-indigo-100 px-1 rounded">姓名,学号</span> 或 <span class="font-mono bg-indigo-100 px-1 rounded">姓名　学号</span>（空格或Tab分隔）</p>
            <p class="mt-1">示例：<span class="font-mono">张三,2024001</span></p>
            <p class="mt-1">学号若为空则留空，例如：<span class="font-mono">李四</span></p>
          </div>

          <!-- 文本输入区 -->
          <div class="flex-1 min-h-0 mb-4">
            <textarea
              v-model="batchText"
              placeholder="张三,2024001&#10;李四,2024002&#10;王五&#10;..."
              class="w-full h-40 border-2 border-slate-100 rounded-xl p-3 text-sm text-slate-700 outline-none focus:border-indigo-400 resize-none font-mono"
            ></textarea>
          </div>

          <!-- 预览 -->
          <div v-if="parsedStudents.length > 0" class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-xs font-bold text-slate-400">预览（共 {{ parsedStudents.length }} 人）</span>
              <span class="text-xs text-emerald-600 font-bold">{{ validCount }} 条有效，{{ invalidCount }} 条无效</span>
            </div>
            <div class="border border-slate-100 rounded-xl overflow-hidden max-h-36 overflow-y-auto">
              <table class="w-full text-xs">
                <thead class="bg-slate-50 sticky top-0">
                  <tr>
                    <th class="py-1.5 px-3 text-left text-slate-400 font-bold">#</th>
                    <th class="py-1.5 px-3 text-left text-slate-400 font-bold">姓名</th>
                    <th class="py-1.5 px-3 text-left text-slate-400 font-bold">学号</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(s, i) in parsedStudents" :key="i" class="border-t border-slate-50">
                    <td class="py-1.5 px-3 text-slate-400">{{ i + 1 }}</td>
                    <td class="py-1.5 px-3 font-medium text-slate-700">{{ s.name || '—' }}</td>
                    <td class="py-1.5 px-3 font-mono text-slate-500">{{ s.student_number || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="flex gap-3">
            <button @click="closeBatchImport" class="flex-1 py-3 rounded-xl border-2 border-slate-100 text-slate-500 font-bold">取消</button>
            <button
              @click="doBatchImport"
              :disabled="batchImporting || validCount === 0"
              class="flex-1 py-3 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ batchImporting ? '导入中...' : `导入 ${validCount > 0 ? validCount : ''} 人` }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-slate-800 text-white px-5 py-3 rounded-xl text-sm font-medium shadow-lg z-50">
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminClasses, createAdminClass, updateAdminClass, deleteAdminClass, addAdminClassStudent, deleteAdminStudent, createAdminStudentAccounts, resetAdminStudentPassword, addStudentsToClass } from '../api.js'

const classes = ref([])
const loading = ref(true)
const selectedClass = ref(null)
const showAddClassModal = ref(false)
const showEditClassModal = ref(false)
const showAddStudentModal = ref(false)
const showBatchImportModal = ref(false)
const toast = ref('')

const classForm = ref({ id: '', name: '', description: '' })
const studentForm = ref({ name: '', student_number: '' })

// 批量添加
const batchText = ref('')
const batchImporting = ref(false)

function openBatchImport() {
  batchText.value = ''
  showBatchImportModal.value = true
}

function closeBatchImport() {
  showBatchImportModal.value = false
}

const parsedStudents = computed(() => {
  const lines = batchText.value.split('\n').filter(l => l.trim())
  return lines.map(line => {
    // 支持：姓名,学号  或  姓名　学号（或Tab）
    const parts = line.split(/[,\t，\s]+/).map(p => p.trim()).filter(p => p)
    return {
      name: parts[0] || '',
      student_number: parts[1] || ''
    }
  })
})

const validCount = computed(() => parsedStudents.value.filter(s => s.name).length)
const invalidCount = computed(() => parsedStudents.value.filter(s => !s.name).length)

// 搜索和批量选择
const classSearch = ref('')
const studentSearch = ref('')
const selectedStudents = ref([])
const selectAll = ref(false)

const filteredClasses = computed(() => {
  if (!classSearch.value) return classes.value
  const kw = classSearch.value.toLowerCase()
  return classes.value.filter(c =>
    (c.name && c.name.toLowerCase().includes(kw)) ||
    (c.description && c.description.toLowerCase().includes(kw))
  )
})

const filteredStudents = computed(() => {
  if (!selectedClass.value) return []
  const students = selectedClass.value.students || []
  if (!studentSearch.value) return students
  const kw = studentSearch.value.toLowerCase()
  return students.filter(s =>
    (s.name && s.name.toLowerCase().includes(kw)) ||
    (s.student_number && s.student_number.toLowerCase().includes(kw))
  )
})

function toggleSelectAll() {
  if (selectAll.value) {
    selectedStudents.value = filteredStudents.value.map(s => s.id)
  } else {
    selectedStudents.value = []
  }
}

async function batchDeleteStudents() {
  if (selectedStudents.value.length === 0) return
  if (!confirm(`确定删除选中的 ${selectedStudents.value.length} 名学生吗？`)) return
  try {
    for (const id of selectedStudents.value) {
      await deleteAdminStudent(id)
    }
    selectedStudents.value = []
    selectAll.value = false
    loadClasses()
    showToast(`已删除 ${selectedStudents.value.length} 名学生`)
  } catch (e) {
    showToast('删除失败')
  }
}

async function doBatchImport() {
  if (!selectedClass.value || validCount.value === 0) return
  batchImporting.value = true
  try {
    const res = await addStudentsToClass(selectedClass.value.id, parsedStudents.value.filter(s => s.name))
    if (res.success) {
      const data = res.data || {}
      const added = data.added || parsedStudents.value.filter(s => s.name).length
      const skipped = data.skipped || 0
      closeBatchImport()
      loadClasses()
      showToast(`导入完成：成功 ${added} 人${skipped > 0 ? `，跳过 ${skipped} 人（学号重复或姓名为空）` : ''}`)
    } else {
      showToast(res.message || '导入失败')
    }
  } catch (e) {
    showToast('导入失败')
  } finally {
    batchImporting.value = false
  }
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => toast.value = '', 2500)
}

async function loadClasses() {
  loading.value = true
  try {
    const res = await getAdminClasses()
    if (res.data) {
      classes.value = res.data
      if (selectedClass.value) {
        selectedClass.value = classes.value.find(c => c.id === selectedClass.value.id) || null
      }
    }
  } catch (e) {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function selectClass(cls) {
  selectedClass.value = cls
}

function editClass(cls) {
  classForm.value = { id: cls.id, name: cls.name, description: cls.description || '' }
  showEditClassModal.value = true
}

function closeClassModals() {
  showAddClassModal.value = false
  showEditClassModal.value = false
  classForm.value = { id: '', name: '', description: '' }
}

async function saveNewClass() {
  if (!classForm.value.name.trim()) return showToast('请输入班级名称')
  try {
    await createAdminClass({ name: classForm.value.name, description: classForm.value.description })
    closeClassModals()
    loadClasses()
    showToast('班级添加成功')
  } catch (e) {
    showToast('添加失败')
  }
}

async function saveClassEdit() {
  if (!classForm.value.name.trim()) return showToast('请输入班级名称')
  try {
    await updateAdminClass(classForm.value.id, { name: classForm.value.name, description: classForm.value.description })
    closeClassModals()
    loadClasses()
    showToast('保存成功')
  } catch (e) {
    showToast('保存失败')
  }
}

async function confirmDeleteClass(cls) {
  if (!confirm(`确定删除班级「${cls.name}」吗？该操作将同时删除班级下所有学生！`)) return
  try {
    await deleteAdminClass(cls.id)
    if (selectedClass.value?.id === cls.id) selectedClass.value = null
    loadClasses()
    showToast('已删除')
  } catch (e) {
    showToast('删除失败')
  }
}

async function saveNewStudent() {
  if (!studentForm.value.name.trim()) return showToast('请输入学生姓名')
  try {
    await addAdminClassStudent(selectedClass.value.id, { name: studentForm.value.name, student_number: studentForm.value.student_number })
    showAddStudentModal.value = false
    studentForm.value = { name: '', student_number: '' }
    loadClasses()
    showToast('学生添加成功')
  } catch (e) {
    showToast('添加失败')
  }
}

async function confirmDeleteStudent(s) {
  if (!confirm(`确定删除学生「${s.name}」吗？`)) return
  try {
    await deleteAdminStudent(s.id)
    loadClasses()
    showToast('已删除')
  } catch (e) {
    showToast('删除失败')
  }
}

async function createAccountsForClass() {
  if (!confirm(`为 ${selectedClass.value.name} 中未建账号的学生批量创建账号？默认密码123456。`)) return
  try {
    const res = await createAdminStudentAccounts(selectedClass.value.id)
    if (res.success) {
      showToast(`成功创建 ${res.data.created} 个账号，跳过 ${res.data.skipped} 个`)
      loadClasses()
    }
  } catch (e) {
    showToast('批量创建失败')
  }
}

async function resetStudentPassword(s) {
  if (!confirm(`重置学生「${s.name}」的账号密码为 123456？`)) return
  try {
    await resetAdminStudentPassword(s.account_id)
    showToast('密码已重置为 123456')
  } catch (e) {
    showToast('重置失败')
  }
}

onMounted(loadClasses)
</script>
