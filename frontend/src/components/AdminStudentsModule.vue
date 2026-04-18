<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-slate-800">学生账号管理</h2>
    </div>

    <!-- 批量操作 -->
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
      <h3 class="font-bold text-slate-700 mb-3">批量操作</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs text-slate-400 mb-1">选择班级</label>
          <select v-model="batchClassId" class="w-full border-2 border-slate-100 p-2.5 rounded-xl outline-none text-sm">
            <option value="">全部班级</option>
            <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-slate-400 mb-1">默认密码</label>
          <input v-model="batchPassword" type="text" placeholder="默认 123456" class="w-full border-2 border-slate-100 p-2.5 rounded-xl outline-none text-sm" />
        </div>
        <div class="flex items-end gap-2">
          <button @click="batchCreateAccounts" class="bg-orange-500 text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-orange-600 transition-colors flex-1">
            批量创建账号
          </button>
          <button @click="batchResetPasswords" class="bg-slate-600 text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-slate-700 transition-colors flex-1">
            批量重置密码
          </button>
        </div>
      </div>
      <p class="text-xs text-slate-400 mt-2">说明：批量创建只给未建账号的学生创建，批量重置对所有已建账号的学生生效。</p>
    </div>

    <div v-if="loading" class="text-center py-12 text-slate-400">加载中...</div>

    <!-- 搜索框 -->
    <div v-else class="flex gap-3 items-center">
      <input v-model="searchKeyword" type="text" placeholder="搜索姓名/学号/账号..."
        class="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-400 max-w-md" />
      <span class="text-xs text-slate-400">{{ filteredStudents.length }} 条结果</span>
    </div>

    <!-- 批量操作账号 -->
    <div v-if="!loading && filteredStudents.length > 0" class="flex items-center justify-between bg-red-50 border border-red-100 rounded-xl p-4">
      <div class="flex items-center gap-2">
        <input type="checkbox" v-model="selectAll" @change="toggleSelectAll"
          class="w-4 h-4 rounded border-red-200 text-red-500 focus:ring-red-400" />
        <span class="text-sm text-slate-600">已选 {{ selectedStudents.length }} 人</span>
        <button v-if="selectedStudents.length > 0" @click="selectedStudents = []; selectAll = false" class="text-xs text-slate-400 hover:text-slate-600">取消</button>
      </div>
      <button v-if="selectedStudents.length > 0" @click="batchClearAccounts"
        class="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-600 transition-colors">
        清除账号数据
      </button>
    </div>

    <!-- 学生列表 -->
    <div v-if="!loading" class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="text-left py-3 px-4 text-slate-500 font-medium w-8">
              <input type="checkbox" v-model="selectAll" @change="toggleSelectAll"
                class="w-4 h-4 rounded border-slate-300 text-blue-500 focus:ring-blue-400" />
            </th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">#</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">姓名</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">学号</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">班级</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">账号</th>
            <th class="text-left py-3 px-4 text-slate-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(s, i) in filteredStudents" :key="s.id" class="border-b border-slate-50 hover:bg-slate-50">
            <td class="py-3 px-4">
              <input type="checkbox" :value="s.id" v-model="selectedStudents" class="w-4 h-4 rounded border-slate-300 text-blue-500" />
            </td>
            <td class="py-3 px-4 text-slate-400">{{ i + 1 }}</td>
            <td class="py-3 px-4 font-medium text-slate-700">{{ s.name }}</td>
            <td class="py-3 px-4 text-slate-500">{{ s.student_number || '-' }}</td>
            <td class="py-3 px-4 text-slate-500">{{ getClassName(s.class_id) }}</td>
            <td class="py-3 px-4">
              <span v-if="s.account_id" class="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-bold">{{ s.account_username }}</span>
              <span v-else class="bg-slate-100 text-slate-400 px-2 py-0.5 rounded-full text-xs font-bold">未建</span>
            </td>
            <td class="py-3 px-4">
              <button v-if="s.account_id" @click="resetPassword(s)" class="text-xs text-orange-500 hover:underline mr-2">重置密码</button>
              <button @click="deleteStudent(s)" class="text-xs text-red-400 hover:text-red-600 hover:underline">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="filteredStudents.length === 0" class="py-12 text-center text-slate-400">
        {{ searchKeyword ? '未找到匹配结果' : '暂无学生数据' }}
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-slate-800 text-white px-5 py-3 rounded-xl text-sm font-medium shadow-lg z-50">
      {{ toast }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminClasses, deleteAdminStudent, createAdminStudentAccounts, resetAdminStudentPassword, clearAdminStudentAccounts } from '../api.js'

const classes = ref([])
const loading = ref(true)
const batchClassId = ref('')
const batchPassword = ref('')
const toast = ref('')

const students = computed(() => {
  if (!batchClassId.value) return classes.value.flatMap(c => c.students || [])
  const cls = classes.value.find(c => c.id === batchClassId.value)
  return cls ? cls.students || [] : []
})

const searchKeyword = ref('')

// 批量选择和删除账号
const selectedStudents = ref([])
const selectAll = ref(false)

const filteredStudents = computed(() => {
  if (!searchKeyword.value) return students.value
  const kw = searchKeyword.value.toLowerCase()
  return students.value.filter(s =>
    (s.name && s.name.toLowerCase().includes(kw)) ||
    (s.student_number && s.student_number.toLowerCase().includes(kw)) ||
    (s.account_username && s.account_username.toLowerCase().includes(kw))
  )
})

function getClassName(classId) {
  return classes.value.find(c => c.id === classId)?.name || classId
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => toast.value = '', 2500)
}

async function loadData() {
  loading.value = true
  try {
    const res = await getAdminClasses()
    if (res.data) classes.value = res.data
  } catch (e) {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

async function batchCreateAccounts() {
  if (!batchClassId.value) return showToast('请先选择班级')
  try {
    const res = await createAdminStudentAccounts(batchClassId.value, batchPassword.value || '123456')
    if (res.success) showToast(`创建 ${res.data.created} 个账号，跳过 ${res.data.skipped} 个`)
    loadData()
  } catch (e) {
    showToast('操作失败')
  }
}

async function batchResetPasswords() {
  const targets = students.value.filter(s => s.account_id)
  if (targets.length === 0) return showToast('该班级没有已建账号的学生')
  if (!confirm(`将为 ${targets.length} 名学生重置密码为 ${batchPassword.value || '123456'}？`)) return
  try {
    for (const s of targets) {
      await resetAdminStudentPassword(s.account_id, batchPassword.value || '123456')
    }
    showToast(`已重置 ${targets.length} 名学生的密码`)
  } catch (e) {
    showToast('操作失败')
  }
}

async function resetPassword(s) {
  if (!confirm(`重置「${s.name}」的密码为 123456？`)) return
  try {
    await resetAdminStudentPassword(s.account_id)
    showToast('密码已重置为 123456')
  } catch (e) {
    showToast('重置失败')
  }
}

async function deleteStudent(s) {
  if (!confirm(`确定删除学生「${s.name}」吗？`)) return
  try {
    await deleteAdminStudent(s.id)
    loadData()
    showToast('已删除')
  } catch (e) {
    showToast('删除失败')
  }
}

function toggleSelectAll() {
  if (selectAll.value) {
    selectedStudents.value = filteredStudents.value.map(s => s.id)
  } else {
    selectedStudents.value = []
  }
}

async function batchClearAccounts() {
  if (selectedStudents.value.length === 0) return showToast('请先选择学生')
  if (!confirm(`确定清除选中的 ${selectedStudents.value.length} 名学生的账号吗？\n\n此操作将：\n1. 账号变为未开通状态\n2. 清除所有提交的作业\n3. 清除考勤记录\n4. 清除所有通知\n\n学生基本信息（姓名、学号）将保留。`)) return
  try {
    const res = await clearAdminStudentAccounts(selectedStudents.value)
    if (res.success) {
      showToast(`已清除 ${res.data.cleared} 个账号数据`)
      selectedStudents.value = []
      selectAll.value = false
      loadData()
    } else {
      showToast(res.message || '操作失败')
    }
  } catch (e) {
    showToast('操作失败')
  }
}

onMounted(loadData)
</script>
