<template>
  <div class="min-h-screen flex flex-col justify-start bg-gradient-to-br from-slate-100 to-slate-200" style="padding-top: env(safe-area-inset-top); padding-bottom: env(safe-area-inset-bottom)">
    <div class="w-full max-w-md mx-auto px-4 pt-6 pb-4">
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-[#1e3a5f] rounded-2xl text-white mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 sm:w-8 sm:h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">智慧课堂管理端</h1>
        <p class="text-slate-500 mt-1 text-sm sm:text-base">江西樟树中医药职业学院</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-5 sm:p-8 sm:pb-8">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">管理员账号</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入账号"
              class="w-full border-2 border-slate-100 p-3 sm:p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-blue-500 transition-colors text-base"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">登录密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="w-full border-2 border-slate-100 p-3 sm:p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-blue-500 transition-colors text-base"
              required
            />
          </div>

          <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-xl text-sm font-medium">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg shadow-lg disabled:opacity-50 bg-[#1e3a5f] text-white hover:bg-[#2a4a73] transition-colors"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { adminLogin } from '../api.js'

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
