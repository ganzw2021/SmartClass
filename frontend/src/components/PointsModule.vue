<template>
  <div>
    <!-- 筛选器 -->
    <div class="flex flex-col md:flex-row gap-4 items-end">
      <div class="flex-1 w-full">
        <label class="text-xs font-bold text-slate-400">选择课程</label>
        <select v-model="selectedCourse" @change="loadScores" class="w-full border-2 border-green-50 px-4 py-2 rounded-xl bg-white text-sm font-bold mt-1">
          <option value="">请选择课程</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">[{{ c.term }}] {{ c.name }}</option>
        </select>
      </div>
      <div class="flex-1 w-full">
        <label class="text-xs font-bold text-slate-400">选择班级</label>
        <select v-model="selectedClass" @change="loadScores" class="w-full border-2 border-green-50 px-4 py-2 rounded-xl bg-white text-sm font-bold mt-1">
          <option value="">请选择班级</option>
          <option v-for="c in filteredClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="flex-1 w-full relative">
        <label class="text-xs font-bold text-slate-400">查找学生</label>
        <div class="relative mt-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="输入姓名关键词..." 
            class="w-full border-2 border-green-50 pl-10 pr-4 py-2 rounded-xl bg-white text-sm font-bold outline-none"
          >
        </div>
      </div>
    </div>

    <!-- 分数表格 -->
    <div class="glass-card bg-white shadow-sm overflow-hidden mt-6">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm min-w-[800px]">
          <thead class="bg-green-50 text-green-900 border-b border-green-100">
            <tr>
              <th class="p-5 font-bold">学生姓名</th>
              <th class="p-5 font-bold">考勤分 (20)</th>
              <th class="p-5 font-bold">互动分 (10)</th>
              <th class="p-5 font-bold">作业分 (20)</th>
              <th class="p-5 font-bold text-green-700 text-lg">总平时分</th>
              <th class="p-5 font-bold text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!filteredStudents.length">
              <td colspan="6" class="p-10 text-center text-slate-400 italic">
                {{ selectedCourse && selectedClass ? '该班级暂无学生' : '请先在上方选择课程和班级' }}
              </td>
            </tr>
            <tr 
              v-for="student in filteredStudents" 
              :key="student.id || student.name"
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="p-5 font-bold text-slate-700">
                {{ typeof student === 'string' ? student : student.name }}
              </td>
              <td class="p-5">{{ getScore(student).att }}</td>
              <td class="p-5">{{ getScore(student).interact }}</td>
              <td class="p-5">{{ getScore(student).hw }}</td>
              <td class="p-5 font-black text-green-700 text-lg">
                {{ getScore(student).att + getScore(student).interact + getScore(student).hw }}
              </td>
              <td class="p-5 text-center">
                <button 
                  @click="openScoreModal(student)" 
                  class="bg-slate-100 text-slate-600 px-4 py-1.5 rounded-lg font-bold hover:bg-green-600 hover:text-white transition-all"
                >
                  评分
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 评分弹窗 -->
    <Teleport to="body">
      <div v-if="showScoreModal" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="showScoreModal = false">
        <div class="bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl">
          <h3 class="text-xl font-black mb-6">评分：{{ currentStudentName }}</h3>
          
          <div class="space-y-6">
            <div>
              <label class="text-xs font-bold text-slate-400 block mb-2">考勤分 (0-20)</label>
              <input 
                v-model.number="editingScore.att" 
                type="number" 
                min="0" 
                max="20" 
                class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
              >
            </div>
            <div>
              <label class="text-xs font-bold text-slate-400 block mb-2">互动分 (0-10)</label>
              <input 
                v-model.number="editingScore.interact" 
                type="number" 
                min="0" 
                max="10" 
                class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
              >
            </div>
            <div>
              <label class="text-xs font-bold text-slate-400 block mb-2">作业分 (0-20)</label>
              <input 
                v-model.number="editingScore.hw" 
                type="number" 
                min="0" 
                max="20" 
                class="w-full border-2 border-slate-50 p-4 rounded-xl outline-none"
              >
            </div>
          </div>

          <div class="flex gap-4 mt-8">
            <button @click="showScoreModal = false" class="flex-1 py-4 text-slate-400 font-bold">取消</button>
            <button @click="saveScore" class="flex-1 py-4 btn-green rounded-xl font-bold">保存成绩</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getScores, saveScores, updateStudentScore } from '../api.js'

const props = defineProps({
  classes: { type: Array, default: () => [] },
  courses: { type: Array, default: () => [] }
})

// 状态
const selectedCourse = ref('')
const selectedClass = ref('')
const searchQuery = ref('')
const scoresData = ref({})
const showScoreModal = ref(false)
const currentStudent = ref(null)
const editingScore = ref({ att: 20, interact: 0, hw: 20 })

// 计算属性
const filteredClasses = computed(() => {
  return props.classes
})

const currentClass = computed(() => {
  return props.classes.find(c => c.id === selectedClass.value)
})

const students = computed(() => {
  if (!currentClass.value) return []
  return currentClass.value.students || []
})

const filteredStudents = computed(() => {
  if (!searchQuery.value.trim()) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(s => {
    const name = typeof s === 'string' ? s : s.name
    return name.toLowerCase().includes(query)
  })
})

const currentStudentName = computed(() => {
  if (!currentStudent.value) return ''
  return typeof currentStudent.value === 'string' ? currentStudent.value : currentStudent.value.name
})

// 方法
function getScore(student) {
  const name = typeof student === 'string' ? student : student.name
  const id = student.id || name
  const key = `${selectedCourse.value}_${selectedClass.value}_${id}`
  return scoresData.value[key] || { att: 20, interact: 0, hw: 20 }
}

async function loadScores() {
  if (!selectedCourse.value || !selectedClass.value) return
  
  try {
    const res = await getScores(selectedCourse.value, selectedClass.value)
    if (res.success && res.data) {
      scoresData.value = {}
      res.data.forEach(item => {
        const key = `${selectedCourse.value}_${selectedClass.value}_${item.student_id || item.student_name}`
        scoresData.value[key] = {
          att: item.att_score ?? 20,
          interact: item.interact_score ?? 0,
          hw: item.hw_score ?? 20
        }
      })
    }
  } catch (e) {
    console.error('加载分数失败', e)
  }
}

function openScoreModal(student) {
  currentStudent.value = student
  const score = getScore(student)
  editingScore.value = { ...score }
  showScoreModal.value = true
}

async function saveScore() {
  const student = currentStudent.value
  if (!student) return
  
  const studentId = student.id
  const name = typeof student === 'string' ? student : student.name
  
  try {
    if (studentId) {
      await updateStudentScore(studentId, selectedCourse.value, {
        att_score: editingScore.value.att,
        interact_score: editingScore.value.interact,
        hw_score: editingScore.value.hw
      })
    }
    
    // 更新本地数据
    const key = `${selectedCourse.value}_${selectedClass.value}_${studentId || name}`
    scoresData.value[key] = { ...editingScore.value }
    
    showScoreModal.value = false
  } catch (e) {
    alert('保存失败')
  }
}

// 监听选择变化
watch([selectedCourse, selectedClass], () => {
  if (selectedCourse.value && selectedClass.value) {
    loadScores()
  }
})
</script>
