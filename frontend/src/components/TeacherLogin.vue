<template>
  <div class="min-h-screen flex flex-col justify-start bg-gradient-to-br from-green-50 to-emerald-100" style="padding-top: env(safe-area-inset-top); padding-bottom: env(safe-area-inset-bottom)">
    <div class="w-full max-w-md mx-auto px-4 pt-6 pb-4">
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-[#2d6a4f] rounded-2xl text-white mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 sm:w-8 sm:h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">智慧课堂教师端</h1>
        <p class="text-slate-500 mt-1 text-sm sm:text-base">江西樟树中医药职业学院</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-5 sm:p-8 sm:pb-8">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">教师账号</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入账号"
              class="w-full border-2 border-slate-100 p-3 sm:p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-green-500 transition-colors text-base"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">登录密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="w-full border-2 border-slate-100 p-3 sm:p-4 rounded-xl outline-none text-slate-700 font-medium focus:border-green-500 transition-colors text-base"
              required
            />
          </div>

          <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-xl text-sm font-medium">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg shadow-lg disabled:opacity-50 bg-[#2d6a4f] text-white hover:bg-[#1b4332] transition-colors"
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
import { teacherLogin } from '../api.js'

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
    const res = await teacherLogin(username.value, password.value)
    if (res.success && res.data) {
      sessionStorage.setItem('tc_token', res.data.token)
      sessionStorage.setItem('tc_teacher', JSON.stringify(res.data.user))
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
