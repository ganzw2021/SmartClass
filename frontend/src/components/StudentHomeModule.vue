<template>
  <div class="space-y-6">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="bg-red-50 border border-red-100 rounded-2xl p-4 text-red-600 text-sm">
      {{ error }}
    </div>

    <!-- 主体内容 -->
    <div v-else class="space-y-6">
      <!-- 消息通知区域 -->
      <div class="bg-white rounded-2xl shadow-sm border border-orange-100 overflow-hidden">
        <!-- 通知头部 -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-orange-50 bg-gradient-to-r from-orange-50 to-amber-50">
          <div class="flex items-center gap-2">
            <span class="text-lg">🔔</span>
            <h3 class="font-bold text-slate-700">消息中心</h3>
            <span v-if="unreadCount > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
              {{ unreadCount }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <button v-if="notifications.length > 0" @click="markAllRead" 
              class="text-xs text-blue-500 hover:text-blue-600">全部已读</button>
            <button v-if="hasReadNotifications" @click="clearRead" 
              class="text-xs text-slate-400 hover:text-slate-600">清空已读</button>
          </div>
        </div>

        <!-- 无通知 -->
        <div v-if="notifications.length === 0" class="py-10 text-center">
          <div class="text-4xl mb-2">📭</div>
          <p class="text-slate-400 text-sm">暂无通知消息</p>
        </div>

        <!-- 通知列表 -->
        <div v-else class="max-h-80 overflow-y-auto">
          <div v-for="notif in notifications" :key="notif.id"
            :class="['px-5 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors relative',
              notif.is_read ? 'opacity-60' : 'bg-blue-50/30']">
            <div class="flex items-start gap-3">
              <!-- 类型图标 -->
              <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0',
                notif.type === 'homework_new' ? 'bg-green-100' : 'bg-amber-100']">
                {{ notif.type === 'homework_new' ? '📝' : '⏰' }}
              </div>
              <!-- 内容 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span :class="['text-sm font-medium', notif.is_read ? 'text-slate-500' : 'text-slate-800']">
                    {{ notif.title }}
                  </span>
                  <span v-if="!notif.is_read" class="w-2 h-2 bg-blue-500 rounded-full"></span>
                </div>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ notif.content }}</p>
                <p class="text-xs text-slate-400 mt-1">{{ formatTime(notif.created_at) }}</p>
              </div>
              <!-- 删除按钮 -->
              <button @click.stop="deleteNotification(notif.id)" 
                class="p-1 text-slate-400 hover:text-red-500 transition-colors">
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 个人资料卡片 -->
      <div class="bg-white rounded-2xl shadow-sm border border-blue-50 p-6">
        <div class="flex items-start gap-4">
          <!-- 头像 -->
          <div class="relative flex-shrink-0">
            <div v-if="profile.avatar" class="w-16 h-16 rounded-full overflow-hidden">
              <img :src="profile.avatar" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-2xl font-bold select-none">
              {{ (user?.name || 'S').charAt(0) }}
            </div>
            <!-- 上传头像按钮 -->
            <label class="absolute -bottom-1 -right-1 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs cursor-pointer hover:bg-blue-600" title="更换头像">
              <input type="file" accept="image/*" class="hidden" @change="handleAvatarFile" />
              ✎
            </label>
          </div>

          <!-- 基本信息 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-xl font-bold text-slate-800">{{ user?.name || '学生' }}</h2>
              <button @click="openEditModal" class="text-xs text-blue-500 hover:text-blue-600">[编辑签名]</button>
            </div>
            <p class="text-slate-500 text-sm">学号：{{ user?.username }}</p>
            <p v-if="profile.bio" class="text-slate-400 text-sm mt-1 italic">"{{ profile.bio }}"</p>
            <p v-else class="text-slate-300 text-sm mt-1 italic">暂无个性签名</p>
          </div>

          <!-- 修改密码 -->
          <button @click="openPasswordModal" class="flex-shrink-0 px-3 py-1.5 text-xs bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors">
            修改密码
          </button>
        </div>
      </div>

      <!-- 课程信息 -->
      <div class="space-y-3">
        <!-- 标题 + 学期筛选 -->
        <div class="flex items-center justify-between flex-wrap gap-2">
          <h3 class="text-lg font-bold text-slate-700">我的课程</h3>
          <select v-if="terms.length > 0" v-model="selectedTerm" @change="loadCourses"
            class="border border-slate-200 rounded-xl px-3 py-1.5 text-sm text-slate-700 focus:border-blue-400 outline-none">
            <option value="">全部学期</option>
            <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- 无课程 -->
        <div v-if="courses.length === 0" class="bg-white rounded-2xl p-8 text-center text-slate-400">
          暂无课程信息
        </div>

        <!-- 课程卡片列表 -->
        <div v-for="course in courses" :key="course.id"
          class="bg-white rounded-2xl shadow-sm border border-blue-50 p-5 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <h4 class="font-bold text-slate-800">{{ course.name }}</h4>
              <p class="text-sm text-slate-500 mt-0.5">{{ course.teacher_name || '未知教师' }}</p>
            </div>
            <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
              <span class="inline-block px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-medium">
                {{ course.class_name || '未知班级' }}
              </span>
              <span v-if="course.term" class="inline-block px-3 py-1 bg-green-50 text-green-600 rounded-full text-xs">
                {{ course.term }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑签名弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showEditModal = false">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-bold text-slate-800 mb-4">编辑个性签名</h3>
        <textarea v-model="editForm.bio"
          class="w-full border border-slate-200 rounded-xl p-3 text-slate-700 focus:border-blue-400 outline-none resize-none"
          rows="3" placeholder="介绍一下自己..."></textarea>
        <div class="flex gap-3 mt-4">
          <button @click="showEditModal = false" class="flex-1 py-2 text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200">取消</button>
          <button @click="saveProfile" :disabled="saving" class="flex-1 py-2 text-white bg-blue-500 rounded-xl hover:bg-blue-600 disabled:opacity-50">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showPasswordModal = false">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-bold text-slate-800 mb-4">修改密码</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-slate-600 mb-1">旧密码</label>
            <input v-model="passwordForm.old_password" type="password"
              class="w-full border border-slate-200 rounded-xl p-3 text-slate-700 focus:border-blue-400 outline-none"
              placeholder="请输入旧密码" />
          </div>
          <div>
            <label class="block text-sm text-slate-600 mb-1">新密码</label>
            <input v-model="passwordForm.new_password" type="password"
              class="w-full border border-slate-200 rounded-xl p-3 text-slate-700 focus:border-blue-400 outline-none"
              placeholder="请输入新密码" />
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="showPasswordModal = false" class="flex-1 py-2 text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200">取消</button>
          <button @click="savePassword" :disabled="saving" class="flex-1 py-2 text-white bg-blue-500 rounded-xl hover:bg-blue-600 disabled:opacity-50">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast提示 -->
    <div v-if="toast.show" :class="['fixed bottom-20 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-full text-white text-sm shadow-lg z-50',
      toast.type === 'success' ? 'bg-green-500' : 'bg-red-500']">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStudentCourses, getStudentProfile, updateStudentProfile, changeStudentPassword,
  getStudentNotifications, deleteNotification, clearReadNotifications, markNotificationsRead } from '../api.js'

const user = ref(JSON.parse(sessionStorage.getItem('tc_student_user') || '{}'))
const courses = ref([])
const terms = ref([])
const selectedTerm = ref('')
const profile = ref({ avatar: '', bio: '' })
const loading = ref(true)
const error = ref('')
const saving = ref(false)

// 通知相关
const notifications = ref([])
const unreadCount = ref(0)

const showEditModal = ref(false)
const showPasswordModal = ref(false)
const editForm = ref({ bio: '' })
const passwordForm = ref({ old_password: '', new_password: '' })
const toast = ref({ show: false, message: '', type: 'success' })

// 是否有已读通知
const hasReadNotifications = computed(() => notifications.value.some(n => n.is_read))

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2000)
}

function openEditModal() {
  editForm.value.bio = profile.value.bio || ''
  showEditModal.value = true
}

function openPasswordModal() {
  passwordForm.value = { old_password: '', new_password: '' }
  showPasswordModal.value = true
}

// 格式化时间
function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const mins = Math.floor(diff / (1000 * 60))
      return mins <= 1 ? '刚刚' : `${mins}分钟前`
    }
    return `${hours}小时前`
  }
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 加载通知
async function loadNotifications() {
  try {
    const res = await getStudentNotifications()
    if (res.success) {
      notifications.value = res.data?.notifications || []
      unreadCount.value = res.data?.unread_count || 0
    }
  } catch (e) {
    console.error('加载通知失败', e)
  }
}

// 删除单条通知
async function handleDeleteNotification(id) {
  try {
    const res = await deleteNotification(id)
    if (res.success) {
      notifications.value = notifications.value.filter(n => n.id !== id)
      if (notifications.value.find(n => n.id === id)?.is_read === 0) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      showToast('已删除')
    }
  } catch (e) {
    showToast('删除失败', 'error')
  }
}

// 标记全部已读
async function markAllRead() {
  try {
    const res = await markNotificationsRead()
    if (res.success) {
      notifications.value.forEach(n => n.is_read = 1)
      unreadCount.value = 0
      showToast('已全部标记为已读')
    }
  } catch (e) {
    showToast('操作失败', 'error')
  }
}

// 清空已读
async function clearRead() {
  try {
    const res = await clearReadNotifications()
    if (res.success) {
      notifications.value = notifications.value.filter(n => !n.is_read)
      showToast('已清空已读消息')
    }
  } catch (e) {
    showToast('操作失败', 'error')
  }
}

// 处理本地图片上传头像
function handleAvatarFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async (ev) => {
    const dataUrl = ev.target.result
    saving.value = true
    try {
      const res = await updateStudentProfile({ avatar: dataUrl })
      if (res.success) {
        profile.value.avatar = dataUrl
        showToast('头像更新成功')
      } else {
        showToast(res.message || '上传失败', 'error')
      }
    } catch (err) {
      showToast('网络错误', 'error')
    } finally {
      saving.value = false
    }
  }
  reader.readAsDataURL(file)
}

async function loadCourses() {
  try {
    const res = await getStudentCourses(selectedTerm.value)
    if (res.success) {
      // 兼容新旧返回格式
      if (res.data && res.data.courses) {
        courses.value = res.data.courses || []
        terms.value = res.data.terms || []
      } else if (Array.isArray(res.data)) {
        courses.value = res.data || []
      }
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const res = await updateStudentProfile({ bio: editForm.value.bio, avatar: profile.value.avatar })
    if (res.success) {
      profile.value.bio = editForm.value.bio
      showEditModal.value = false
      showToast('保存成功')
    } else {
      showToast(res.message || '保存失败', 'error')
    }
  } catch (e) {
    showToast('网络错误', 'error')
  } finally {
    saving.value = false
  }
}

async function savePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    showToast('请填写完整', 'error')
    return
  }
  saving.value = true
  try {
    const res = await changeStudentPassword(passwordForm.value.old_password, passwordForm.value.new_password)
    if (res.success) {
      showPasswordModal.value = false
      showToast('密码修改成功')
    } else {
      showToast(res.message || '修改失败', 'error')
    }
  } catch (e) {
    showToast('网络错误', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [coursesRes, profileRes, notifRes] = await Promise.all([
      getStudentCourses(),
      getStudentProfile(),
      getStudentNotifications()
    ])
    if (coursesRes.success) {
      if (coursesRes.data && coursesRes.data.courses) {
        courses.value = coursesRes.data.courses || []
        terms.value = coursesRes.data.terms || []
      } else if (Array.isArray(coursesRes.data)) {
        courses.value = coursesRes.data || []
      } else {
        error.value = coursesRes.message || '加载课程失败'
      }
    }
    if (profileRes.success) {
      profile.value = profileRes.data || {}
    }
    if (notifRes.success) {
      notifications.value = notifRes.data?.notifications || []
      unreadCount.value = notifRes.data?.unread_count || 0
    }
  } catch (e) {
    error.value = '网络错误'
  } finally {
    loading.value = false
  }
})
</script>
