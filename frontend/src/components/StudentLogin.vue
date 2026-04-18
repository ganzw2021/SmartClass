<template>
  <div class="min-h-screen flex flex-col justify-start bg-gradient-to-br from-blue-50 to-indigo-100" style="padding-top: env(safe-area-inset-top); padding-bottom: env(safe-area-inset-bottom)">
    <div class="w-full max-w-md mx-auto px-4 pt-6 pb-4">
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-blue-600 rounded-2xl text-white mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 sm:w-8 sm:h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800">智慧课堂学生端</h1>
        <p class="text-slate-500 mt-1 text-sm sm:text-base">江西樟树中医药职业学院</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl p-5 sm:p-8 sm:pb-8">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">学号</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入学号"
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
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-3 sm:py-4 rounded-xl transition-colors flex items-center justify-center gap-2 text-base"
          >
            <svg v-if="loading" class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { studentLogin } from '../api.js'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入学号和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await studentLogin(username.value, password.value)
    if (res.success) {
      emit('login-success', res.data?.user || {})
    } else {
      error.value = res.message || '登录失败，请检查学号和密码'
    }
  } catch (e) {
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>



