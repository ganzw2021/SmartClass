<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
    <div class="glass-card bg-white p-10 w-full max-w-md shadow-2xl">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-[#2d6a4f] rounded-2xl text-white mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-slate-800">智慧课堂管理系统</h1>
        <p class="text-slate-500 mt-2">江西樟树中医药职业学院</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">管理员账号</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入账号"
            class="w-full border-2 border-slate-100 p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-green-500 transition-colors"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">登录密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            class="w-full border-2 border-slate-100 p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-green-500 transition-colors"
            required
          />
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-xl text-sm font-medium">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full btn-green py-4 rounded-xl font-bold text-lg shadow-lg disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="text-center text-slate-400 text-xs mt-6">
        默认账号: admin / Admin@123456
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { adminLogin } from '../admin-api.js'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const res = await adminLogin(username.value, password.value)
    // 后端返回格式: {code:200, success:true, data:{token, user}}
    if (res.success && res.data) {
      sessionStorage.setItem('tc_admin_token', res.data.token)
      sessionStorage.setItem('tc_admin_user', JSON.stringify(res.data.user))
      emit('login-success', res.data.user)
    } else {
      error.value = res.message || '登录失败'
    }
  } catch (e) {
    error.value = e.response?.data?.message || '网络错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>
