<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-2xl font-bold text-slate-800">教师管理</h2>
      <div class="flex gap-3 items-center">
        <input v-model="searchKeyword" type="text" placeholder="搜索账号/姓名..."
          class="border border-slate-200 rounded-xl px-4 py-2 text-sm outline-none focus:border-blue-400 w-56" />
        <button @click="showAddModal = true" class="btn-green px-5 py-2.5 rounded-xl text-sm font-bold">
          + 新增教师
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-slate-400">加载中...</div>

    <div v-else class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="text-left py-4 px-5 text-slate-500 font-medium">ID</th>
            <th class="text-left py-4 px-5 text-slate-500 font-medium">账号</th>
            <th class="text-left py-4 px-5 text-slate-500 font-medium">姓名</th>
            <th class="text-left py-4 px-5 text-slate-500 font-medium">Token</th>
            <th class="text-left py-4 px-5 text-slate-500 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTeachers" :key="t.id" class="border-b border-slate-50 hover:bg-slate-50">
            <td class="py-3 px-5 text-slate-400">{{ t.id }}</td>
            <td class="py-3 px-5 font-medium text-slate-700">{{ t.username }}</td>
            <td class="py-3 px-5 text-slate-700">{{ t.real_name || '-' }}</td>
            <td class="py-3 px-5">
              <span class="font-mono text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{{ t.teacher_token || '-' }}</span>
            </td>
            <td class="py-3 px-5">
              <div class="flex gap-3">
                <button @click="editTeacher(t)" class="text-blue-500 hover:underline text-xs">编辑</button>
                <button @click="resetToken(t)" class="text-orange-500 hover:underline text-xs">重置Token</button>
                <button @click="resetPassword(t)" class="text-orange-600 hover:underline text-xs">重置密码</button>
                <button v-if="t.id !== 1" @click="deleteTeacher(t)" class="text-red-400 hover:text-red-600 hover:underline text-xs">删除</button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredTeachers.length === 0">
            <td colspan="5" class="py-12 text-center text-slate-400">
              {{ searchKeyword ? '未找到匹配结果' : '暂无教师' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" @click.self="closeModals">
        <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
          <h3 class="font-bold text-lg text-slate-800 mb-4">{{ showEditModal ? '编辑教师' : '新增教师' }}</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">账号</label>
              <input v-model="form.username" type="text" :disabled="showEditModal" placeholder="登录账号" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400 disabled:bg-slate-50 disabled:text-slate-400" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">姓名</label>
              <input v-model="form.real_name" type="text" placeholder="真实姓名" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">密码{{ showEditModal ? '（留空不修改）' : '' }}</label>
              <input v-model="form.password" type="text" :placeholder="showEditModal ? '留空不修改' : '默认123456'" class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none text-slate-700 focus:border-blue-400" />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="closeModals" class="flex-1 py-3 rounded-xl border-2 border-slate-100 text-slate-500 font-bold">取消</button>
            <button @click="showEditModal ? saveTeacherEdit() : saveNewTeacher()" class="flex-1 py-3 rounded-xl bg-blue-600 text-white font-bold hover:bg-blue-700 transition-colors">
              {{ showEditModal ? '保存' : '添加' }}
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
import { getAdminTeachers, createAdminTeacher, updateAdminTeacher, deleteAdminTeacher, resetAdminTeacherToken, resetAdminTeacherPassword } from '../api.js'

const teachers = ref([])
const loading = ref(true)
const showAddModal = ref(false)
const showEditModal = ref(false)
const toast = ref('')

const form = ref({ id: '', username: '', real_name: '', password: '' })
const searchKeyword = ref('')

const filteredTeachers = computed(() => {
  if (!searchKeyword.value) return teachers.value
  const kw = searchKeyword.value.toLowerCase()
  return teachers.value.filter(t =>
    (t.username && t.username.toLowerCase().includes(kw)) ||
    (t.real_name && t.real_name.toLowerCase().includes(kw))
  )
})

function showToast(msg) {
  toast.value = msg
  setTimeout(() => toast.value = '', 2500)
}

async function loadTeachers() {
  loading.value = true
  try {
    const res = await getAdminTeachers()
    if (res.data) teachers.value = res.data
  } catch (e) {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function editTeacher(t) {
  form.value = { id: t.id, username: t.username, real_name: t.real_name || '', password: '' }
  showEditModal.value = true
}

function closeModals() {
  showAddModal.value = false
  showEditModal.value = false
  form.value = { id: '', username: '', real_name: '', password: '' }
}

async function saveNewTeacher() {
  if (!form.value.username.trim() || !form.value.real_name.trim()) return showToast('账号和姓名不能为空')
  try {
    await createAdminTeacher({ username: form.value.username, real_name: form.value.real_name, password: form.value.password || '123456' })
    closeModals()
    loadTeachers()
    showToast('添加成功')
  } catch (e) {
    showToast('添加失败')
  }
}

async function saveTeacherEdit() {
  if (!form.value.real_name.trim()) return showToast('姓名不能为空')
  try {
    const data = { real_name: form.value.real_name }
    if (form.value.password) data.password = form.value.password
    await updateAdminTeacher(form.value.id, data)
    closeModals()
    loadTeachers()
    showToast('保存成功')
  } catch (e) {
    showToast('保存失败')
  }
}

async function deleteTeacher(t) {
  if (!confirm(`确定删除教师「${t.username}」吗？`)) return
  try {
    await deleteAdminTeacher(t.id)
    loadTeachers()
    showToast('已删除')
  } catch (e) {
    showToast('删除失败')
  }
}

async function resetToken(t) {
  if (!confirm(`重置教师「${t.username}」的登录Token？`)) return
  try {
    const res = await resetAdminTeacherToken(t.id)
    if (res.success) showToast(`新Token: ${res.data.token}`)
    loadTeachers()
  } catch (e) {
    showToast('重置失败')
  }
}

async function resetPassword(t) {
  if (!confirm(`重置教师「${t.username}」的密码为 123456？`)) return
  try {
    await resetAdminTeacherPassword(t.id)
    showToast('密码已重置为 123456')
  } catch (e) {
    showToast('重置失败')
  }
}

onMounted(loadTeachers)
</script>
