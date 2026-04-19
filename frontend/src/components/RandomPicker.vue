<template>
  <div class="flex flex-col items-center py-6 min-h-[600px]">
    <!-- 标题 -->
    <h2 class="text-2xl font-black text-emerald-800 mb-6 flex items-center gap-3">
      <span class="text-3xl">🌿</span>
      悬 壶 问 诊
      <span class="text-3xl">🌿</span>
    </h2>

    <div class="flex flex-col lg:flex-row items-center gap-16 w-full max-w-5xl">
      <!-- 左侧：葫芦（药葫芦）区域 -->
      <div class="flex flex-col items-center">
        <!-- 葫芦 -->
        <div 
          class="relative cursor-pointer"
          :class="{ 'animate-gourd-shake': isShaking }"
        >
          <!-- 葫芦主体 -->
          <svg width="180" height="220" viewBox="0 0 180 220" class="drop-shadow-xl">
            <!-- 葫芦藤 -->
            <path d="M90 10 Q95 5 100 8 Q105 12 102 18 Q98 22 90 20 Q82 22 78 18 Q75 12 80 8 Q85 5 90 10" fill="#5D4037"/>
            <path d="M90 20 L88 30" stroke="#8D6E63" stroke-width="3" stroke-linecap="round"/>
            
            <!-- 葫芦上半部分 -->
            <ellipse cx="90" cy="75" rx="55" ry="50" fill="url(#gourdGradient)"/>
            
            <!-- 葫芦下半部分 -->
            <ellipse cx="90" cy="150" rx="70" ry="60" fill="url(#gourdGradient2)"/>
            
            <!-- 葫芦嘴 -->
            <ellipse cx="90" cy="108" rx="20" ry="8" fill="#6D4C41"/>
            
            <!-- 葫芦纹理 -->
            <path d="M50 70 Q90 60 130 70" stroke="#5D4037" stroke-width="1" fill="none" opacity="0.3"/>
            <path d="M40 100 Q90 90 140 100" stroke="#5D4037" stroke-width="1" fill="none" opacity="0.3"/>
            <path d="M30 140 Q90 125 150 140" stroke="#5D4037" stroke-width="1" fill="none" opacity="0.3"/>
            <path d="M35 170 Q90 160 145 170" stroke="#5D4037" stroke-width="1" fill="none" opacity="0.3"/>
            
            <!-- 药方符号 -->
            <text x="90" y="78" text-anchor="middle" font-size="32" fill="#4E342E" font-family="serif">药</text>
            
            <!-- 装饰图案 -->
            <circle cx="50" cy="60" r="8" fill="none" stroke="#8D6E63" stroke-width="1" opacity="0.5"/>
            <circle cx="130" cy="60" r="8" fill="none" stroke="#8D6E63" stroke-width="1" opacity="0.5"/>
            <circle cx="35" cy="130" r="6" fill="none" stroke="#8D6E63" stroke-width="1" opacity="0.5"/>
            <circle cx="145" cy="130" r="6" fill="none" stroke="#8D6E63" stroke-width="1" opacity="0.5"/>
            
            <!-- 葫芦高光 -->
            <ellipse cx="60" cy="70" rx="15" ry="20" fill="white" opacity="0.15"/>
            <ellipse cx="55" cy="140" rx="20" ry="25" fill="white" opacity="0.15"/>
            
            <!-- 渐变定义 -->
            <defs>
              <linearGradient id="gourdGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8D6E63"/>
                <stop offset="50%" style="stop-color:#A1887F"/>
                <stop offset="100%" style="stop-color:#6D4C41"/>
              </linearGradient>
              <linearGradient id="gourdGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#8D6E63"/>
                <stop offset="50%" style="stop-color:#A1887F"/>
                <stop offset="100%" style="stop-color:#6D4C41"/>
              </linearGradient>
            </defs>
          </svg>
        </div>

        <!-- 求签按钮 -->
        <button 
          @click="doRandom" 
          :disabled="!selectedClass || !students.length || isShaking || isDropping"
          class="mt-6 px-12 py-4 bg-gradient-to-r from-emerald-700 via-emerald-600 to-emerald-700 hover:from-emerald-600 hover:to-emerald-600 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-full text-lg font-black shadow-xl transition-all active:scale-95 disabled:cursor-not-allowed"
        >
          {{ isShaking ? '摇药中...' : isDropping ? '落药...' : '求 药 问 诊' }}
        </button>

        <!-- 班级选择 -->
        <div class="mt-6 w-48">
          <select v-model="selectedClass" class="w-full border-2 border-emerald-400 p-3 rounded-xl outline-none font-bold text-center bg-emerald-50 focus:border-emerald-600 transition-colors text-emerald-900">
            <option value="">选择班级</option>
            <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

      <!-- 右侧：药方展示区域 -->
      <div class="flex-1 flex flex-col items-center justify-center min-h-[450px]">
        <!-- 空状态 -->
        <div v-if="!showResult && !isShaking && !isDropping" class="text-center">
          <div class="text-7xl mb-4 opacity-30">🍃</div>
          <p class="text-emerald-700/60 text-lg">悬壶济世，医者仁心</p>
        </div>

        <!-- 药签掉落动画 -->
        <div v-if="isDropping" class="relative">
          <div 
            class="transition-all duration-700"
            :style="dropStyle"
          >
            <!-- 竹简/药方签 -->
            <div class="bg-gradient-to-b from-amber-100 to-amber-200 rounded-lg shadow-lg overflow-hidden" style="width: 140px; height: 200px;">
              <!-- 签头 -->
              <div class="bg-gradient-to-b from-emerald-700 to-emerald-800 h-10 flex items-center justify-center">
                <span class="text-yellow-300 text-sm font-bold">药签</span>
              </div>
              <!-- 签身 -->
              <div class="p-3 flex-1">
                <div class="text-emerald-800 text-xs text-center mb-2">上上签</div>
                <div class="h-px bg-emerald-400/30 my-2"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 抽中的药方展示 -->
        <div 
          v-if="showResult && selectedStudent"
          class="animate-prescription-appear"
        >
          <!-- 光芒 -->
          <div class="absolute -inset-10 bg-gradient-to-r from-emerald-200 via-green-100 to-emerald-200 rounded-lg blur-2xl opacity-40 animate-pulse"></div>
          
          <!-- 药方/处方笺 -->
          <div class="relative bg-gradient-to-b from-amber-50 to-amber-100 rounded-lg shadow-2xl overflow-hidden" style="width: 340px;">
            <!-- 药方顶栏 -->
            <div class="bg-gradient-to-r from-emerald-700 to-emerald-600 px-6 py-4 text-center">
              <div class="flex items-center justify-center gap-3">
                <span class="text-emerald-300">🌿</span>
                <span class="text-white text-xl font-black tracking-wider">处 方 笺</span>
                <span class="text-emerald-300">🌿</span>
              </div>
            </div>
            
            <!-- 药方内容 -->
            <div class="p-5">
              <!-- 学生信息 -->
              <div class="text-center mb-4">
                <div class="inline-block border-2 border-emerald-600 rounded-lg px-4 py-2 bg-emerald-50">
                  <span class="text-emerald-800 font-black text-lg">{{ selectedStudent.name }}</span>
                </div>
              </div>
              
              <!-- 分隔线 -->
              <div class="flex items-center gap-2 my-3">
                <div class="flex-1 h-px bg-emerald-400"></div>
                <span class="text-emerald-500">◆</span>
                <div class="flex-1 h-px bg-emerald-400"></div>
              </div>
              
              <!-- 药方核心内容区 -->
              <div class="bg-white/60 rounded-lg p-4 border border-emerald-200 mb-4">
                <!-- 诊断 -->
                <div class="flex items-start gap-2 mb-3">
                  <span class="text-emerald-700 font-bold text-sm">诊断：</span>
                  <span class="text-emerald-800 text-sm flex-1">学业精进，才华横溢</span>
                </div>
                
                <!-- 中药处方 -->
                <div class="border-t border-dashed border-emerald-300 pt-3 mb-3">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-emerald-700 font-bold text-sm">处方：</span>
                  </div>
                  <!-- 中药名称 -->
                  <div v-if="selectedHerb" class="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <span class="text-2xl">🌿</span>
                        <div>
                          <div class="text-emerald-800 font-black text-lg">{{ selectedHerb.name }}</div>
                          <div class="text-emerald-600 text-xs">{{ selectedHerb.category }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="mt-2 pt-2 border-t border-emerald-100">
                      <div class="text-emerald-700 text-sm">
                        <span class="font-bold">功效：</span>
                        <span class="text-emerald-600">{{ selectedHerb.efficacy }}</span>
                      </div>
                    </div>
                  </div>
                  <!-- 加载中 -->
                  <div v-else class="text-center py-4 text-emerald-500 text-sm">
                    正在配药...
                  </div>
                </div>
                
                <!-- 医嘱/签名 -->
                <div class="flex items-start gap-2">
                  <span class="text-emerald-700 font-bold text-sm">医嘱：</span>
                  <span class="text-emerald-800 text-sm flex-1 leading-relaxed italic">
                    "{{ selectedStudent.signature }}"
                  </span>
                </div>
              </div>
              
              <!-- 医师签名区 -->
              <div class="border-t border-dashed border-emerald-300 pt-3">
                <div class="flex justify-between items-center">
                  <div>
                    <div class="text-emerald-600 text-xs">主治医师</div>
                    <div class="text-emerald-800 font-serif text-lg">悬壶先生</div>
                  </div>
                  <div class="text-right">
                    <div class="text-emerald-600 text-xs">处方日期</div>
                    <div class="text-emerald-800 text-sm">{{ currentDate }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 头像 -->
            <div class="flex justify-center -mt-2">
              <div class="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-200 to-emerald-300 p-1 shadow-md">
                <div class="w-full h-full rounded-full bg-white flex items-center justify-center overflow-hidden">
                  <svg v-if="!selectedStudent.avatar" xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <img v-else :src="selectedStudent.avatar" class="w-full h-full object-cover" alt="头像" />
                </div>
              </div>
            </div>
            
            <!-- 装饰图案 -->
            <div class="flex justify-center gap-2 mt-3 pb-4">
              <span class="text-emerald-400">🍃</span>
              <span class="text-emerald-500">◆</span>
              <span class="text-emerald-400">🍃</span>
            </div>
            
            <!-- 药方底栏 -->
            <div class="bg-emerald-800 px-4 py-2 text-center">
              <span class="text-emerald-200 text-xs">济世堂 · 悬壶问诊</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  classes: { type: Array, default: () => [] }
})

// 后端地址
const BACKEND_BASE = import.meta.env.VITE_BACKEND_BASE || 'http://localhost:5000'

const selectedClass = ref('')
const selectedStudent = ref(null)
const selectedHerb = ref(null)  // 选中的中药
const isShaking = ref(false)
const isDropping = ref(false)
const showResult = ref(false)

// 掉落动画的 top 值
const dropTop = ref(-80)

const dropStyle = computed(() => ({
  top: `${dropTop.value}px`,
  transition: isDropping.value ? 'top 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none'
}))

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(now.getDate()).padStart(2, '0')}`
})

// 个性签名库（中医药风格）
const signaturePool = [
  '勤求古训，博采众方',
  '上医治未病，中医治欲病',
  '医者仁心，悬壶济世',
  '阴阳平衡，气血调和',
  '药到病除，妙手回春',
  '望闻问切，四诊合参',
  '君臣佐使，配伍精当',
  '道地药材，疗效显著',
  '标本兼治，固本培元',
  '扶正祛邪，调和阴阳',
  '春生夏长，秋收冬藏',
  '正气存内，邪不可干',
  '疏通经络，调和气血',
  '清热解毒，凉血消肿',
  '补中益气，固本培元',
  '活血化瘀，通络止痛',
  '养心安神，益智开窍',
  '健脾和胃，升清降浊',
  '疏肝解郁，理气和中',
  '滋阴润燥，养血生津'
]

const currentClass = computed(() => {
  return props.classes.find(c => c.id === selectedClass.value)
})

const students = computed(() => {
  if (!currentClass.value) return []
  return currentClass.value.students || []
})

function getRandomSignature() {
  return signaturePool[Math.floor(Math.random() * signaturePool.length)]
}

// 获取随机中药
async function fetchRandomHerb() {
  try {
    const res = await fetch(`${BACKEND_BASE}/api/herb/random`)
    const data = await res.json()
    if (data.success && data.data) {
      selectedHerb.value = data.data
    }
  } catch (e) {
    console.error('获取中药失败', e)
    // 备用本地中药库
    const backupHerbs = [
      { name: '人参', category: '补气药', efficacy: '大补元气，复脉固脱，补脾益肺，生津养血' },
      { name: '黄芪', category: '补气药', efficacy: '补气升阳，固表止汗，利水消肿，生津养血' },
      { name: '当归', category: '补血药', efficacy: '补血活血，调经止痛，润肠通便' },
      { name: '枸杞子', category: '补阴药', efficacy: '滋补肝肾，益精明目' },
      { name: '金银花', category: '清热药', efficacy: '清热解毒，疏散风热' },
      { name: '甘草', category: '补气药', efficacy: '补脾益气，清热解毒，祛痰止咳，缓急止痛' },
    ]
    selectedHerb.value = backupHerbs[Math.floor(Math.random() * backupHerbs.length)]
  }
}

function doRandom() {
  if (!students.value.length) {
    alert('该班级无学生名册')
    return
  }
  
  // 重置状态
  showResult.value = false
  selectedStudent.value = null
  selectedHerb.value = null
  
  // 开始摇晃
  isShaking.value = true
  
  // 摇晃动画（2秒），不显示任何名字
  setTimeout(async () => {
    isShaking.value = false
    
    // 选中一个学生
    const finalStudent = students.value[Math.floor(Math.random() * students.value.length)]
    selectedStudent.value = {
      name: finalStudent.name || finalStudent,
      avatar: finalStudent.avatar || null,
      signature: finalStudent.signature || getRandomSignature()
    }
    
    // 同时获取随机中药
    await fetchRandomHerb()
    
    // 开始掉落动画
    isDropping.value = true
    dropTop.value = -100
    
    // 触发掉落
    setTimeout(() => {
      dropTop.value = 60
    }, 50)
    
    // 掉落完成后放大展示
    setTimeout(() => {
      isDropping.value = false
      showResult.value = true
    }, 800)
    
  }, 2000)
}
</script>

<style scoped>
/* 葫芦摇晃动画 */
@keyframes gourd-shake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  10% { transform: translateX(-12px) rotate(-8deg); }
  20% { transform: translateX(12px) rotate(8deg); }
  30% { transform: translateX(-10px) rotate(-6deg); }
  40% { transform: translateX(10px) rotate(6deg); }
  50% { transform: translateX(-8px) rotate(-5deg); }
  60% { transform: translateX(8px) rotate(5deg); }
  70% { transform: translateX(-6px) rotate(-4deg); }
  80% { transform: translateX(6px) rotate(4deg); }
  90% { transform: translateX(-3px) rotate(-2deg); }
}

.animate-gourd-shake {
  animation: gourd-shake 0.5s ease-in-out infinite;
  transform-origin: top center;
}

/* 药方出现动画 */
@keyframes prescription-appear {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(-30px);
  }
  60% {
    opacity: 1;
    transform: scale(1.03) translateY(5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-prescription-appear {
  animation: prescription-appear 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
</style>
