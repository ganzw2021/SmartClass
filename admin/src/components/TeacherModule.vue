<template>
  <div>
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold border-l-4 border-green-600 pl-3 text-slate-800">教师管理</h3>
      <button @click="openTeacherModal()" class="btn-green px-6 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        添加教师
      </button>
    </div>

    <!-- 教师列表 -->
    <div class="mt-6 glass-card bg-white overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">姓名</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">用户名</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">关联课程</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">管理班级</th>
            <th class="px-6 py-4 text-right text-xs font-bold text-slate-400 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="!teachers.length">
            <td colspan="5" class="px-6 py-10 text-center text-slate-400">暂无教师</td>
          </tr>
          <tr v-for="teacher in teachers" :key="teacher.id" class="hover:bg-slate-50">
            <td class="px-6 py-4 font-bold text-slate-700">{{ teacher.name }}</td>
            <td class="px-6 py-4 text-slate-500">{{ teacher.username }}</td>
            <td class="px-6 py-4 text-slate-500">
              <span v-for="c in teacher.courses" :key="c.id" class="inline-block bg-green-50 text-green-700 px-2 py-0.5 rounded text-xs mr-1">
                {{ c.name }}
              </span>
              <span v-if="!teacher.courses?.length" class="text-slate-300">暂无</span>
            </td>
            <td class="px-6 py-4 text-slate-500">
              <span v-for="cls in teacher.classes" :key="cls.id" class="inline-block bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs mr-1">
                {{ cls.name }}
              </span>
              <span v-if="!teacher.classes?.length" class="text-slate-300">暂无</span>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="openTeacherModal(teacher)" class="text-green-600 hover:text-green-800 mr-3">编辑</button>
              <button @click="resetPassword(teacher)" class="text-blue-600 hover:text-blue-800 mr-3">重置密码</button>
              <button @click="deleteTeacherHandler(teacher.id)" class="text-red-400 hover:text-red-600">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 教师弹窗 -->
    <TeacherModal
      v-if="showModal"
      :teacherData="editingTeacher"
      @close="showModal = false"
      @save="handleSaveTeacher"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTeachers, deleteTeacher, resetTeacherPassword } from '../admin-api.js'
import TeacherModal from './TeacherModal.vue'

const emit = defineEmits(['refresh'])

const teachers = ref([])
const showModal = ref(false)
const editingTeacher = ref(null)

async function loadTeachers() {
  try {
    const res = await getTeachers()
    if (res.success) {
      teachers.value = res.data || []
    }
  } catch (e) {
    console.error('加载教师失败:', e)
  }
}

function openTeacherModal(teacher = null) {
  editingTeacher.value = teacher
  showModal.value = true
}

async function handleSaveTeacher() {
  showModal.value = false
  await loadTeachers()
  emit('refresh')
}

async function deleteTeacherHandler(id) {
  if (!confirm('确定删除该教师？')) return
  try {
    await deleteTeacher(id)
    await loadTeachers()
  } catch (e) {
    alert('删除失败')
  }
}

async function resetPassword(teacher) {
  if (!confirm(`确定重置 ${teacher.name} 的密码为 123456？`)) return
  try {
    await resetTeacherPassword(teacher.id, '123456')
    alert('密码已重置为：123456')
  } catch (e) {
    alert('重置失败')
  }
}

onMounted(() => {
  loadTeachers()
})
</script>
