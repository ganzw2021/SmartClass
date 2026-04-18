<template>
  <div class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-6" @click.self="$emit('close')">
    <div class="bg-white rounded-[32px] w-full max-w-md p-8 shadow-2xl">
      <h3 class="text-xl font-bold text-slate-800 mb-6">
        {{ teacherData ? '编辑教师' : '添加教师' }}
      </h3>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">姓名</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="教师姓名"
            class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none focus:border-green-500 transition-colors"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="登录账号"
            class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none focus:border-green-500 transition-colors"
            :disabled="!!teacherData"
            required
          />
          <p v-if="teacherData" class="text-xs text-slate-400 mt-1">用户名不可修改</p>
        </div>

        <div v-if="!teacherData">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">初始密码</label>
          <input
            v-model="form.password"
            type="text"
            placeholder="默认 123456"
            class="w-full border-2 border-slate-100 p-3 rounded-xl outline-none focus:border-green-500 transition-colors"
          />
        </div>

        <div class="flex gap-3 pt-4">
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createTeacher, updateTeacher } from '../admin-api.js'

const props = defineProps({
  teacherData: Object
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  name: '',
  username: '',
  password: ''
})

onMounted(() => {
  if (props.teacherData) {
    form.value.name = props.teacherData.name || ''
    form.value.username = props.teacherData.username || ''
  }
})

async function handleSubmit() {
  if (!form.value.name.trim() || !form.value.username.trim()) {
    alert('请填写完整信息')
    return
  }

  try {
    if (props.teacherData) {
      await updateTeacher(props.teacherData.id, { name: form.value.name })
    } else {
      await createTeacher({
        name: form.value.name,
        username: form.value.username,
        password: form.value.password || '123456'
      })
    }
    emit('save')
  } catch (e) {
    alert('保存失败：' + (e.response?.data?.message || e.message))
  }
}
</script>
