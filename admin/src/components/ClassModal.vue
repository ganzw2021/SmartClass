<template>
  <div class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-white rounded-[32px] w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col p-8 shadow-2xl">
      <h3 class="text-xl font-bold text-slate-800 mb-6">
        {{ classData ? '编辑班级' : '添加班级' }}
      </h3>

      <div class="overflow-y-auto flex-1 pr-2">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">班级名称</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="例如：2024级中药学1班"
              class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none focus:border-green-500 transition-colors"
              required
            />
          </div>

          <!-- 学生管理（仅编辑模式） -->
          <div v-if="classData" class="border-t border-slate-100 pt-5">
            <div class="flex justify-between items-center mb-3">
              <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">学生列表 ({{ students.length }}人)</label>
              <button type="button" @click="showAddStudent = true" class="text-xs text-green-600 hover:text-green-800 font-bold">+ 添加学生</button>
            </div>
            
            <!-- 添加学生表单 -->
            <div v-if="showAddStudent" class="bg-green-50 p-4 rounded-xl mb-3 space-y-3">
              <div class="flex gap-2">
                <input v-model="newStudent.student_number" type="text" placeholder="学号（必填）" class="flex-1 border border-green-200 p-2 rounded-lg text-sm" />
                <input v-model="newStudent.name" type="text" placeholder="姓名（必填）" class="flex-1 border border-green-200 p-2 rounded-lg text-sm" />
              </div>
              <div class="flex gap-2">
                <button type="button" @click="showAddStudent = false" class="flex-1 py-2 border border-slate-200 rounded-lg text-sm text-slate-500">取消</button>
                <button type="button" @click="handleAddStudent" class="flex-1 btn-green py-2 rounded-lg text-sm">确认添加</button>
              </div>
            </div>

            <!-- 学生列表 -->
            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div v-if="!students.length" class="text-center text-slate-400 py-6 text-sm">暂无学生</div>
              <div
                v-for="student in students"
                :key="student.id"
                class="flex items-center justify-between bg-slate-50 p-3 rounded-xl"
              >
                <div class="flex items-center gap-3">
                  <span class="text-sm font-medium text-slate-700">{{ student.student_number }}</span>
                  <span class="text-sm text-slate-600">{{ student.name }}</span>
                  <span v-if="student.account_id" class="text-xs text-green-500 bg-green-100 px-2 py-0.5 rounded">已开户</span>
                </div>
                <button type="button" @click="handleRemoveStudent(student)" class="text-red-400 hover:text-red-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="flex gap-3 pt-4 border-t border-slate-100">
            <button type="button" @click="$emit('close')" class="flex-1 py-3 border-2 border-slate-100 rounded-xl font-bold text-slate-500 hover:bg-slate-50">
              取消
            </button>
            <button type="submit" class="flex-1 btn-green py-3 rounded-xl font-bold">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createClass, updateClass, addStudent, deleteStudent } from '../admin-api.js'

const props = defineProps({
  classData: Object
})

const emit = defineEmits(['close', 'save'])

const form = ref({ name: '' })
const students = ref([])
const showAddStudent = ref(false)
const newStudent = ref({ student_number: '', name: '' })

onMounted(() => {
  if (props.classData) {
    form.value.name = props.classData.name || ''
    students.value = props.classData.students || []
  }
})

async function handleAddStudent() {
  if (!newStudent.value.student_number.trim() || !newStudent.value.name.trim()) {
    alert('请填写学号和姓名')
    return
  }
  try {
    await addStudent(props.classData.id, {
      name: newStudent.value.name.trim(),
      student_number: newStudent.value.student_number.trim()
    })
    // 重新加载学生列表
    const cls = props.classData
    const { getAdminClasses } = await import('../admin-api.js')
    const res = await getAdminClasses()
    if (res.success) {
      const updated = res.data.find(c => c.id === cls.id)
      if (updated) students.value = updated.students
    }
    newStudent.value = { student_number: '', name: '' }
    showAddStudent.value = false
    emit('save')
  } catch (e) {
    alert(e.response?.data?.message || '添加失败')
  }
}

async function handleRemoveStudent(student) {
  if (!confirm(`确定移除学生 "${student.name}"？`)) return
  try {
    await deleteStudent(student.id)
    students.value = students.value.filter(s => s.id !== student.id)
    emit('save')
  } catch (e) {
    alert(e.response?.data?.message || '移除失败')
  }
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    alert('请输入班级名称')
    return
  }
  try {
    if (props.classData) {
      await updateClass(props.classData.id, form.value)
    } else {
      await createClass(form.value)
    }
    emit('save')
  } catch (e) {
    alert(e.response?.data?.message || '保存失败')
  }
}
</script>
