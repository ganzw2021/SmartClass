<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
    <!-- 主静心区域 -->
    <div class="lg:col-span-2 glass-card bg-white p-12 flex flex-col items-center justify-center space-y-10 relative overflow-hidden min-h-[520px] shadow-[0_20px_60px_-15px_rgba(45,106,79,0.1)]">
      <!-- 太极背景 -->
      <div class="absolute inset-0 flex items-center justify-center z-0 pointer-events-none">
        <svg viewBox="0 0 100 100" class="w-4/5 taiji-bg blur-[2px] opacity-[0.03]">
          <path d="M 50 0 A 50 50 0 0 1 50 100 A 25 25 0 0 1 50 50 A 25 25 0 0 0 50 0" fill="#2d6a4f"/>
          <path d="M 50 100 A 50 50 0 0 1 50 0 A 25 25 0 0 1 50 50 A 25 25 0 0 0 50 100" fill="#2d6a4f"/>
          <circle cx="50" cy="25" r="5" fill="#ffffff" />
          <circle cx="50" cy="75" r="5" fill="#2d6a4f" />
        </svg>
      </div>

      <div class="relative z-10 text-center">
        <div class="inline-flex items-center gap-2 px-6 py-1.5 bg-green-50 border border-green-100 rounded-full mb-3 shadow-sm">
          <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span class="text-green-700 font-black tracking-[0.2em] text-xs italic uppercase">{{ ziwuSeason }}</span>
        </div>
        <h2 class="text-3xl font-black text-slate-800 tracking-widest">课间静心</h2>
      </div>

      <!-- 圆形计时器 -->
      <div class="relative w-72 h-72 flex items-center justify-center z-10">
        <div class="absolute inset-0 rounded-full bg-green-50 scale-105 opacity-30 blur-xl"></div>
        <svg class="w-full h-full transform -rotate-90">
          <circle cx="144" cy="144" r="130" stroke="#f1f5f9" stroke-width="12" fill="white" />
          <circle 
            cx="144" cy="144" r="130" 
            stroke="var(--primary-green)" 
            stroke-width="12" 
            fill="transparent" 
            stroke-dasharray="816" 
            :stroke-dashoffset="circleOffset"
            stroke-linecap="round" 
            class="transition-all duration-1000 ease-linear" 
          />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-8">
          <span class="text-7xl font-black text-slate-800 tracking-tighter tabular-nums leading-none">{{ timerDisplay }}</span>
          <p class="text-slate-400 mt-6 font-black text-sm tracking-[0.4em] breath-text">吸气 · 呼气</p>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="flex gap-8 z-10">
        <button @click="resetBreak" class="p-4 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-all active:scale-90" title="重置">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button @click="toggleBreak" class="px-14 py-5 btn-green rounded-full font-black text-lg shadow-xl hover:shadow-2xl transition-all flex items-center gap-3 active:scale-95">
          <svg v-if="!isRunning" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
          <span>{{ isRunning ? '暂停调息' : (timeLeft < 600 ? '继续入静' : '开始入静') }}</span>
        </button>
      </div>
    </div>

    <!-- 右侧：子午流注和练习 -->
    <div class="space-y-6">
      <!-- 子午流注 -->
      <div class="glass-card bg-[#1b4332] text-white p-7 shadow-xl border-none relative overflow-hidden">
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-5">
            <span class="bg-white/10 px-3 py-1 rounded text-[10px] font-black tracking-widest border border-white/20 uppercase">子午流注</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h4 class="text-3xl font-black mb-1">{{ ziwuData.name }}</h4>
          <p class="text-green-300 font-bold text-base mb-3 tracking-widest">{{ ziwuData.organ }}</p>
          <p class="text-[13px] text-green-50/70 leading-relaxed italic">{{ ziwuData.desc }}</p>
        </div>
      </div>

      <!-- 八段锦 -->
      <div class="glass-card bg-[#fdfaf5] p-7 border-l-[12px] border-[#c7a97b] shadow-lg">
        <div class="flex items-center justify-between mb-5">
          <h4 class="font-black text-slate-800 flex items-center gap-2 text-base">
            <span class="w-1.5 h-4 bg-[#c7a97b] rounded-full"></span>
            八段锦·引导
          </h4>
        </div>
        <div class="bg-white/60 p-5 rounded-2xl border border-[#c7a97b]/10">
          <p class="text-sm font-black text-[#8b6e3f] mb-2">{{ currentExercise.title }}</p>
          <p class="text-xs text-slate-600 leading-[1.8] font-medium">{{ currentExercise.content }}</p>
        </div>
      </div>

      <!-- 五音疗愈 -->
      <div class="glass-card bg-white p-6 border border-slate-100 group transition-all" :class="{ 'music-active': audioPlaying }">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-green-50 group-hover:text-green-600 transition-colors">
              <div class="flex items-end gap-[2px] h-4">
                <span class="music-bar"></span>
                <span class="music-bar"></span>
                <span class="music-bar"></span>
              </div>
            </div>
            <div>
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-0.5">五音疗愈 · 五脏和调</p>
              <p class="text-sm font-black text-slate-700">{{ audioLabel }}</p>
            </div>
          </div>
          <button @click="toggleAudio" class="w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-inner active:scale-90" :class="audioPlaying ? 'bg-green-500 text-white' : 'bg-slate-100 text-slate-500 hover:bg-green-500 hover:text-white'">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 子午流注数据
const ZIWU_MAP = [
  { h: [23, 1], name: "子时", organ: "胆经当令", desc: "子时睡得足，黑眼圈不露。此时应入睡以养胆气。", tone: "宫" },
  { h: [1, 3], name: "丑时", organ: "肝经当令", desc: "肝藏血，此时应深度睡眠，让肝血推陈出新。", tone: "角" },
  { h: [3, 5], name: "寅时", organ: "肺经当令", desc: "肺朝百脉。此时呼吸由深转匀，气血重新分配。", tone: "商" },
  { h: [5, 7], name: "卯时", organ: "大肠经当令", desc: "旭日东升。此时宜起身排毒，清理肠胃。", tone: "商" },
  { h: [7, 9], name: "辰时", organ: "胃经当令", desc: "宜进早餐。此时脾胃运化最强，补充全日能量。", tone: "宫" },
  { h: [9, 11], name: "巳时", organ: "脾经当令", desc: "脾主运化。此时大脑最活跃，是学习黄金时段。", tone: "宫" },
  { h: [11, 13], name: "午时", organ: "心经当令", desc: "心主神明。此时宜午休小憩，养心安神。", tone: "徵" },
  { h: [13, 15], name: "未时", organ: "小肠经当令", desc: "分清别浊。小肠吸收精微，宜多饮茶水。", tone: "徵" },
  { h: [15, 17], name: "申时", organ: "膀胱经当令", desc: "津液充沛。此时体能达到高峰，适合学习锻炼。", tone: "羽" },
  { h: [17, 19], name: "酉时", organ: "肾经当令", desc: "肾藏精。此时气血流注肾脏，宜收敛神气。", tone: "羽" },
  { h: [19, 21], name: "戌时", organ: "心包经当令", desc: "心包护心。此时宜保持心情愉悦，散步静心。", tone: "徵" },
  { h: [21, 23], name: "亥时", organ: "三焦经当令", desc: "百脉休养。此时三焦通百脉，宜静卧休养。", tone: "羽" }
]

const EX_LIST = [
  { t: "双手托天理三焦", c: "两掌交叉上托，充分拉伸脊柱与三焦经，适合久坐缓解疲劳。" },
  { t: "左右开弓似射雕", c: "展胸扩肺，疏肝理气，缓解肩颈酸痛，增强心肺功能。" },
  { t: "调理脾胃须单举", c: "一手上托一手下按，调和中焦气机，利于课后运化。" },
  { t: "五劳七伤往后瞧", c: "转动颈部向后望，舒缓颈椎压力，调节五脏劳损。" }
]

// 状态
const timeLeft = ref(600) // 10分钟
const isRunning = ref(false)
const audioPlaying = ref(false)
const breakTimerInt = ref(null)

// 音频
let audioCtx = null
let currentOsc = null

// 计算属性
const ziwuData = computed(() => {
  const hour = new Date().getHours()
  return ZIWU_MAP.find(s => {
    if (s.h[0] > s.h[1]) return hour >= s.h[0] || hour < s.h[1]
    return hour >= s.h[0] && hour < s.h[1]
  }) || ZIWU_MAP[0]
})

const ziwuSeason = computed(() => `药都日课 · ${ziwuData.value.name}调息`)

const currentExercise = computed(() => {
  const idx = Math.floor(Math.random() * EX_LIST.length)
  return { title: EX_LIST[idx].t, content: EX_LIST[idx].c }
})

const audioLabel = computed(() => `药都合成：${ziwuData.value.tone}音 (${ziwuData.value.organ.substring(0, 1)}调)`)

const timerDisplay = computed(() => {
  const mins = Math.floor(timeLeft.value / 60)
  const secs = timeLeft.value % 60
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`
})

const circleOffset = computed(() => {
  return 816 - (timeLeft.value / 600) * 816
})

// 方法
function toggleBreak() {
  if (breakTimerInt.value) {
    clearInterval(breakTimerInt.value)
    breakTimerInt.value = null
    return
  }
  
  breakTimerInt.value = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(breakTimerInt.value)
      breakTimerInt.value = null
      timeLeft.value = 0
    }
  }, 1000)
}

function resetBreak() {
  clearInterval(breakTimerInt.value)
  breakTimerInt.value = null
  timeLeft.value = 600
  isRunning.value = false
}

function toggleAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  }
  
  if (!audioPlaying.value) {
    audioPlaying.value = true
    playFiveToneLoop()
  } else {
    audioPlaying.value = false
    if (currentOsc) {
      currentOsc.stop()
      currentOsc = null
    }
  }
}

function playFiveToneLoop() {
  if (!audioPlaying.value || !audioCtx) return
  
  const freqMap = { "宫": 261.63, "商": 293.66, "角": 329.63, "徵": 392.00, "羽": 440.00 }
  const freq = freqMap[ziwuData.value.tone] || 329.63
  
  const osc = audioCtx.createOscillator()
  const gain = audioCtx.createGain()
  osc.type = 'sine'
  osc.frequency.setValueAtTime(freq, audioCtx.currentTime)
  gain.gain.setValueAtTime(0, audioCtx.currentTime)
  gain.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + 0.5)
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 4)
  osc.connect(gain)
  gain.connect(audioCtx.destination)
  osc.start()
  currentOsc = osc
  
  osc.onended = () => {
    if (audioPlaying.value) setTimeout(playFiveToneLoop, 1000)
  }
  osc.stop(audioCtx.currentTime + 4.5)
}

onUnmounted(() => {
  clearInterval(breakTimerInt.value)
  if (currentOsc) currentOsc.stop()
})
</script>
