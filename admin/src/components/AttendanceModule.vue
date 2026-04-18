<template>
  <div>
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold border-l-4 border-green-600 pl-3 text-slate-800">考勤记录</h3>
    </div>

    <!-- 考勤记录列表 -->
    <div class="glass-card bg-white mt-6 overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">时间</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">课程</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">班级</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">应到</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">实到</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase">状态</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="!logs.length">
            <td colspan="6" class="px-6 py-10 text-center text-slate-400">暂无考勤记录</td>
          </tr>
          <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50">
            <td class="px-6 py-4 text-slate-700">{{ log.created_at }}</td>
            <td class="px-6 py-4 text-slate-700">{{ log.course_name }}</td>
            <td class="px-6 py-4 text-slate-500">{{ log.class_name }}</td>
            <td class="px-6 py-4 text-slate-500">{{ log.total_students }}</td>
            <td class="px-6 py-4 text-slate-500">{{ log.signed_count }}</td>
            <td class="px-6 py-4">
              <span :class="['px-2 py-1 rounded text-xs font-bold',
                log.signed_count >= log.total_students ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700']">
                {{ log.signed_count >= log.total_students ? '已完成' : '进行中' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAttendanceLogs } from '../admin-api.js'

const logs = ref([])

async function loadLogs() {
  try {
    const res = await getAttendanceLogs()
    if (res.success) {
      logs.value = res.data || []
    }
  } catch (e) {
    console.error('加载考勤记录失败:', e)
  }
}

onMounted(() => {
  loadLogs()
})
</script>
