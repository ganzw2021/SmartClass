<template>
  <section class="lucky-picker flex flex-col items-center py-6 min-h-[600px]">
    <h2 class="text-2xl font-black text-emerald-800 flex items-center gap-3">
      <span aria-hidden="true">✦</span> 幸运签 <span aria-hidden="true">✦</span>
    </h2>
    <p class="mt-2 mb-6 text-sm text-emerald-700/70">摇一摇签筒，看看今天的幸运同学</p>
    <div class="picker-layout">
      <div class="flex flex-col items-center">
        <div class="draw-scene" aria-hidden="true">
          <div class="tube-shadow"></div>
          <div class="tube-group" :class="{ 'is-shaking': phase === 'shaking' }" @animationend="onShakeEnd">
            <svg class="stick-bundle" width="240" height="270" viewBox="0 0 240 270">
              <ellipse cx="120" cy="104" rx="69" ry="20" fill="#794723"/>
              <ellipse cx="120" cy="101" rx="59" ry="13" fill="#432e20"/>
              <g class="inner-sticks">
                <rect v-for="(stick, index) in sticks" :key="index" :x="stick.x" :y="stick.y" width="12" height="106" rx="3"
                  :fill="`url(#${artId}-stick)`" :transform="`rotate(${stick.angle} ${stick.x + 6} 107)`"/>
              </g>
            </svg>
            <div v-if="phase === 'drawing' || phase === 'revealed'" class="drawn-stick"
              :class="{ 'is-drawing': phase === 'drawing', 'is-drawn': phase === 'revealed' }"
              @animationend="onDrawEnd"><span>幸运签</span><i>✦</i></div>
            <svg class="bamboo-tube" width="240" height="270" viewBox="0 0 240 270">
              <defs>
                <linearGradient :id="`${artId}-bamboo`" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stop-color="#97602d"/><stop offset=".3" stop-color="#d5a65b"/>
                  <stop offset=".55" stop-color="#e8c780"/><stop offset="1" stop-color="#98612f"/>
                </linearGradient>
                <linearGradient :id="`${artId}-stick`" x1="0" y1="0" x2="1" y2="0">
                  <stop stop-color="#d4ab65"/><stop offset=".5" stop-color="#ffebae"/><stop offset="1" stop-color="#c89b50"/>
                </linearGradient>
              </defs>
              <path d="M51 104 Q120 136 189 104 L183 242 Q120 270 57 242 Z" :fill="`url(#${artId}-bamboo)`"/>
              <g stroke="#83572f" stroke-width="1.3" opacity=".3">
                <path d="M72 116 L76 249 M94 121 L96 254 M120 124 L120 258 M146 121 L144 254 M168 116 L164 249"/>
              </g>
              <path d="M52 107 Q120 139 188 107" fill="none" stroke="#f3d291" stroke-width="7"/>
              <path d="M55 126 Q120 153 185 126 M57 230 Q120 258 183 230" fill="none" stroke="#76512e" stroke-width="5"/>
              <rect x="94" y="151" width="52" height="66" rx="9" fill="#17634e" stroke="#f1d592" stroke-width="2"/>
              <text x="120" y="178" text-anchor="middle" fill="#fff1c0" font-size="19" font-family="serif">幸</text>
              <text x="120" y="203" text-anchor="middle" fill="#fff1c0" font-size="19" font-family="serif">运</text>
              <path d="M65 144 L69 215" stroke="#fff3c3" stroke-width="5" stroke-linecap="round" opacity=".25"/>
            </svg>
          </div>
        </div>
        <label for="lucky-class" class="mb-2 text-sm font-bold text-emerald-800">抽签班级</label>
        <select id="lucky-class" v-model="selectedClass" :disabled="isBusy"
          class="w-56 border-2 border-emerald-300 p-3 rounded-xl outline-none font-bold text-center bg-emerald-50 focus:border-emerald-600 text-emerald-900 disabled:opacity-60">
          <option value="">选择班级</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <button @click="doRandom" :disabled="!students.length || isBusy" :aria-busy="isBusy"
          class="mt-5 px-10 py-3 bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-600 hover:to-emerald-500 disabled:from-gray-400 disabled:to-gray-400 text-white rounded-full text-lg font-black shadow-lg transition-transform active:scale-95 disabled:cursor-not-allowed">
          {{ phase === 'shaking' ? '摇签中…' : phase === 'drawing' ? '幸运签出筒…' : showResult ? '再摇一签' : '摇一摇 · 抽幸运签' }}
        </button>
        <p class="mt-3 text-sm text-emerald-700/70 min-h-[20px]" role="status">{{ statusText }}</p>
      </div>
      <div class="result-stage" :aria-busy="isBusy">
        <div v-if="!showResult" class="text-center text-emerald-700/60">
          <div class="text-6xl mb-5 text-emerald-300" aria-hidden="true">✦</div>
          <p class="text-lg font-bold">{{ isBusy ? '好运正在酝酿' : '每一份努力，都值得被看见' }}</p>
          <p class="mt-2 text-sm">{{ isBusy ? '幸运同学即将揭晓' : '选好班级，摇出今天的幸运签' }}</p>
        </div>
        <article v-else-if="selectedStudent" class="result-card" aria-label="幸运签结果">
          <div class="bg-gradient-to-r from-emerald-800 to-emerald-600 px-6 py-4 text-center">
            <p class="text-emerald-100 text-xs tracking-[.3em]">今日好运</p>
            <h3 class="text-white text-xl font-black tracking-widest mt-1">幸运签</h3>
          </div>
          <div class="p-5">
            <div class="flex flex-col items-center gap-3 mb-4">
              <div class="w-14 h-14 rounded-full bg-emerald-100 border-4 border-white shadow flex items-center justify-center overflow-hidden">
                <img v-if="selectedStudent.avatar" :src="selectedStudent.avatar" class="w-full h-full object-cover" alt="幸运同学头像"/>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              <div class="text-center">
                <p class="text-emerald-600 text-xs mb-1">幸运同学</p>
                <p class="student-name text-emerald-900 font-black text-2xl">{{ selectedStudent.name }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3 my-4 text-emerald-500" aria-hidden="true">
              <div class="flex-1 h-px bg-emerald-200"></div>✦<div class="flex-1 h-px bg-emerald-200"></div>
            </div>
            <div class="bg-white/70 rounded-xl p-4 border border-emerald-100">
              <p class="text-xs font-bold text-emerald-600 mb-2">幸运寄语</p>
              <p class="text-emerald-900 text-sm leading-relaxed break-words">{{ selectedStudent.signature }}</p>
              <div class="herb-slot mt-4 pt-3 border-t border-dashed border-emerald-200">
                <p class="text-xs font-bold text-emerald-600 mb-2">本签药材 · 课堂小知识</p>
                <template v-if="selectedHerb">
                  <div class="flex flex-wrap items-baseline gap-2">
                    <span class="text-emerald-900 font-black text-lg">{{ selectedHerb.name }}</span>
                    <span class="text-emerald-600 text-xs">{{ selectedHerb.category }}</span>
                  </div>
                  <p class="mt-2 text-sm text-emerald-700 leading-relaxed break-words"><span class="font-bold">功效：</span>{{ selectedHerb.efficacy }}</p>
                </template>
                <p v-else class="text-emerald-600 text-sm" role="status">药材小知识加载中…</p>
              </div>
            </div>
            <div class="flex justify-between gap-3 mt-4 text-xs text-emerald-700/70">
              <span class="break-words">{{ currentClass?.name }}</span><time class="shrink-0">{{ drawDate }}</time>
            </div>
          </div>
          <div class="bg-emerald-800 px-4 py-2 text-center text-emerald-100 text-xs">保持好奇，下一份幸运就是你</div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount, getCurrentInstance } from 'vue'
const props = defineProps({ classes: { type: Array, default: () => [] } })
const BACKEND_BASE = (import.meta.env.VITE_BACKEND_BASE || '').replace(/\/$/, '')
const artId = `lucky-tube-${getCurrentInstance().uid}`
const selectedClass = ref('')
const selectedStudent = ref(null)
const selectedHerb = ref(null)
const drawDate = ref('')
const phase = ref('idle')
const isBusy = computed(() => phase.value === 'shaking' || phase.value === 'drawing')
const showResult = computed(() => phase.value === 'revealed')
const currentClass = computed(() => props.classes.find(c => c.id === selectedClass.value))
const students = computed(() => currentClass.value?.students || [])
const statusText = computed(() => {
  if (!currentClass.value) return '请先选择班级'
  if (!students.value.length) return '该班级暂无学生名册'
  if (phase.value === 'shaking') return '签筒摇动中，请稍候'
  if (phase.value === 'drawing') return '幸运签正在出筒'
  if (showResult.value) return `抽中了 ${selectedStudent.value.name}`
  return `共 ${students.value.length} 位同学参与抽签`
})
const sticks = [
  { x: 76, y: 38, angle: -16 }, { x: 92, y: 23, angle: -9 },
  { x: 108, y: 30, angle: -3 }, { x: 123, y: 18, angle: 5 },
  { x: 138, y: 29, angle: 12 }, { x: 151, y: 42, angle: 18 }
]
const signaturePool = [
  '心有所向，学有所成。', '保持好奇，每一次思考都在靠近答案。',
  '认真积累，终会迎来属于你的高光时刻。', '大胆表达，你的想法值得被听见。',
  '今天再进步一点，好运就离你更近一点。', '勤求古训，博采众方。',
  '把今天的问题想明白，就是一份收获。', '你的每一次举手，都在为自己打开新可能。',
  '愿你带着好奇心，把知识变成自己的本领。', '慢慢来，扎实的脚步也能走得很远。',
  '敢于提问的人，已经迈出了探索的第一步。', '多看一眼细节，也许就能发现新的答案。',
  '愿今天的你，比昨天多懂一点点。', '认真观察，是认识世界的好方法。',
  '别怕答错，思考本身就值得鼓励。', '把不懂说出来，学习才有新的起点。',
  '每一味药材都有故事，每一次学习都有惊喜。', '从一片叶子开始，也能认识广阔的本草世界。',
  '愿你的努力像种子一样，悄悄生根发芽。', '今天的灵感，可能藏在一次勇敢的表达里。',
  '多一点耐心，就多一分看清问题的机会。', '你的认真，会在未来给你回响。',
  '愿你用清晰的思路，迎接今天的挑战。', '和同学分享发现，快乐也会加倍。',
  '把课堂里的小收获，积成成长的大力量。', '愿你的目光始终明亮，问题始终有趣。',
  '今天试着换个角度，答案也许就在眼前。', '每一次练习，都是下一次从容的底气。',
  '学会倾听，也是一种出色的表达。', '发现自己的进步，就是今天的幸运。',
  '愿你在求知路上，既有热情也有耐心。', '一步一个脚印，知识会越来越牢固。',
  '认真记录的你，正在为未来留下线索。', '愿你对未知保持敬意，对学习保持热爱。',
  '把复杂的问题拆开，答案会慢慢清楚。', '今天的好问题，值得大家一起讨论。',
  '尝试说出你的推理过程，比猜对更精彩。', '愿你在本草的世界里发现更多奇妙联系。',
  '小小的进步，也值得为自己鼓掌。', '你的想法可能正是讨论需要的新角度。',
  '把好奇带进课堂，把收获带出课堂。', '愿你学会辨认差异，也欣赏万物的独特。',
  '今天认真读过的内容，会成为明天的灵感。', '给自己一点信心，你已经比想象中更会思考。',
  '愿你越学越会问，越问越会学。', '从观察到理解，每一步都值得珍惜。',
  '课堂上的一次尝试，可能成为成长的转折点。', '把知识讲给别人听，是检验理解的好办法。',
  '愿你与同学互相启发，一起找到更多答案。', '新的知识正在靠近，准备好迎接它吧。'
]
const backupHerbs = [
  { name: '人参', category: '补气药', efficacy: '大补元气，复脉固脱，补脾益肺，生津养血' },
  { name: '黄芪', category: '补气药', efficacy: '补气升阳，固表止汗，利水消肿，生津养血' },
  { name: '党参', category: '补气药', efficacy: '健脾益肺，养血生津' },
  { name: '山药', category: '补气药', efficacy: '补脾养胃，生津益肺，补肾涩精' },
  { name: '当归', category: '补血药', efficacy: '补血活血，调经止痛，润肠通便' },
  { name: '白芍', category: '补血药', efficacy: '养血调经，柔肝止痛，敛阴止汗' },
  { name: '枸杞子', category: '补阴药', efficacy: '滋补肝肾，益精明目' },
  { name: '麦冬', category: '补阴药', efficacy: '养阴润肺，益胃生津，清心除烦' },
  { name: '金银花', category: '清热药', efficacy: '清热解毒，疏散风热' },
  { name: '菊花', category: '清热药', efficacy: '散风清热，平肝明目，清热解毒' },
  { name: '蒲公英', category: '清热药', efficacy: '清热解毒，消肿散结，利尿通淋' },
  { name: '薄荷', category: '解表药', efficacy: '疏散风热，清利头目，利咽，透疹' },
  { name: '葛根', category: '解表药', efficacy: '解肌退热，生津止渴，升阳止泻' },
  { name: '陈皮', category: '理气药', efficacy: '理气健脾，燥湿化痰' },
  { name: '丹参', category: '活血化瘀药', efficacy: '活血祛瘀，通经止痛，清心除烦' },
  { name: '茯苓', category: '利水渗湿药', efficacy: '利水渗湿，健脾宁心' },
  { name: '薏苡仁', category: '利水渗湿药', efficacy: '利水渗湿，健脾止泻，除痹，排脓' },
  { name: '山楂', category: '消食药', efficacy: '消食健胃，行气散瘀，化浊降脂' },
  { name: '酸枣仁', category: '安神药', efficacy: '养心补肝，宁心安神，敛汗，生津' },
  { name: '甘草', category: '补气药', efficacy: '补脾益气，清热解毒，祛痰止咳，缓急止痛' }
]
const pick = items => items[Math.floor(Math.random() * items.length)]
const recentHerbs = []
const recentSignatures = []
function pickFresh(items, recent) {
  const options = items.filter(item => !recent.includes(typeof item === 'string' ? item : item.name))
  return pick(options.length ? options : items)
}
function remember(recent, value, limit) {
  if (!value) return
  recent.push(value)
  if (recent.length > limit) recent.shift()
}
let phaseTimer
let requestController
let drawVersion = 0

function armPhaseFallback(callback, duration) {
  clearTimeout(phaseTimer)
  // 动画结束事件为主；后台标签页等情况下由兜底计时器收尾。
  phaseTimer = setTimeout(callback, duration + 160)
}
function finishShaking() {
  if (phase.value !== 'shaking') return
  phase.value = 'drawing'
  armPhaseFallback(finishDrawing, 760)
}
function finishDrawing() {
  if (phase.value !== 'drawing') return
  clearTimeout(phaseTimer)
  phase.value = 'revealed'
}
function onShakeEnd(event) {
  if (event.target === event.currentTarget && event.animationName.startsWith('tube-shake')) finishShaking()
}
function onDrawEnd(event) {
  if (event.target === event.currentTarget && event.animationName.startsWith('stick-draw')) finishDrawing()
}

async function fetchRandomHerb(version) {
  const controller = new AbortController()
  requestController = controller
  const timeout = setTimeout(() => controller.abort(), 4500)
  let herb = pickFresh(backupHerbs, recentHerbs)
  try {
    const query = recentHerbs.length ? `?exclude=${encodeURIComponent(recentHerbs.join(','))}` : ''
    const res = await fetch(`${BACKEND_BASE}/api/herb/random${query}`, { signal: controller.signal })
    if (!res.ok) throw new Error('药材接口请求失败')
    const data = await res.json()
    if (data.success && data.data?.name) herb = data.data
  } catch {
    // 失败、超时和无效响应均使用本地药材，抽签动画不等待网络。
  } finally {
    clearTimeout(timeout)
    if (requestController === controller) requestController = undefined
  }
  if (version === drawVersion) {
    selectedHerb.value = herb
    remember(recentHerbs, herb.name, 12)
  }
}
function doRandom() {
  if (isBusy.value || !students.value.length) return
  requestController?.abort()
  const version = ++drawVersion
  const student = pick(students.value)
  const signature = student.signature || pickFresh(signaturePool, recentSignatures)
  if (!student.signature) remember(recentSignatures, signature, 12)
  selectedStudent.value = {
    name: student.name || student,
    avatar: student.avatar || null,
    signature
  }
  selectedHerb.value = null
  drawDate.value = new Date().toLocaleDateString('zh-CN').replaceAll('/', '.')
  phase.value = 'shaking'
  // 与摇筒并行获取药材，避免接口延迟打断出签。
  void fetchRandomHerb(version)
  armPhaseFallback(finishShaking, 1440)
}
function resetDraw() {
  ++drawVersion
  clearTimeout(phaseTimer)
  requestController?.abort()
  phase.value = 'idle'
  selectedStudent.value = null
  selectedHerb.value = null
}
watch(selectedClass, resetDraw)
watch(currentClass, value => { if (!value) resetDraw() })
onBeforeUnmount(resetDraw)
</script>

<style scoped>
.lucky-picker { width: 100%; }
.picker-layout { display: grid; grid-template-columns: 300px minmax(0, 1fr); align-items: center; gap: 48px; width: 100%; max-width: 920px; }
.draw-scene { position: relative; width: 300px; height: 320px; }
.tube-group { position: absolute; left: 30px; top: 30px; width: 240px; height: 270px; transform-origin: 50% 85%; }
.bamboo-tube { position: relative; z-index: 2; }
.stick-bundle { position: absolute; inset: 0; z-index: 0; }
.tube-shadow { position: absolute; bottom: 13px; left: 64px; width: 172px; height: 18px; border-radius: 50%; background: radial-gradient(ellipse, #30534130, transparent 70%); }
.drawn-stick { position: absolute; z-index: 1; left: 105px; top: 66px; width: 30px; height: 126px; border: 1px solid #c99b52; border-radius: 5px; background: linear-gradient(90deg, #d4ab65, #ffedb7 50%, #d4ab65); box-shadow: 0 2px 5px #65432122; transform-origin: 50% 90%; }
.drawn-stick span { display: block; margin: 9px auto 0; writing-mode: vertical-rl; font: bold 15px serif; letter-spacing: 4px; color: #175c49; }
.drawn-stick i { display: block; text-align: center; font-style: normal; color: #a66129; margin-top: 8px; }
.is-shaking { animation: tube-shake 1440ms ease-in-out both; will-change: transform; }
.is-shaking .inner-sticks { animation: sticks-rattle 180ms ease-in-out 8; transform-origin: 120px 105px; }
.is-drawing { animation: stick-draw 760ms cubic-bezier(.22, .68, .25, 1) both; will-change: transform, opacity; }
.is-drawn { transform: translate3d(0, -52px, 0) rotate(10deg); }
.result-stage { display: flex; justify-content: center; align-items: center; min-height: 500px; min-width: 0; }
.result-card { position: relative; width: 340px; max-width: 100%; border-radius: 16px; overflow: hidden; background: linear-gradient(#fffcf2, #f9efd6); border: 1px solid #e5d6b4; box-shadow: 0 16px 40px #174e3420; animation: result-reveal 360ms cubic-bezier(.2, .65, .3, 1) both; }
.student-name { overflow-wrap: anywhere; }
.herb-slot { min-height: 115px; }
@keyframes tube-shake {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(0); }
  10% { transform: translate3d(-7px, -2px, 0) rotate(-8deg); }
  22% { transform: translate3d(7px, -4px, 0) rotate(8deg); }
  34% { transform: translate3d(-8px, -3px, 0) rotate(-9deg); }
  46% { transform: translate3d(8px, -5px, 0) rotate(9deg); }
  58% { transform: translate3d(-7px, -3px, 0) rotate(-8deg); }
  70% { transform: translate3d(6px, -2px, 0) rotate(7deg); }
  82% { transform: translate3d(-4px, -1px, 0) rotate(-4deg); }
  92% { transform: translate3d(2px, 0, 0) rotate(2deg); }
}
@keyframes sticks-rattle {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-4px) rotate(1deg); }
}
@keyframes stick-draw {
  0% { transform: translate3d(0, 65px, 0) rotate(0); opacity: 0; }
  14% { opacity: 1; }
  72% { transform: translate3d(0, -58px, 0) rotate(12deg); }
  100% { transform: translate3d(0, -52px, 0) rotate(10deg); opacity: 1; }
}
@keyframes result-reveal {
  from { opacity: 0; transform: translate3d(0, 12px, 0) scale(.98); }
  to { opacity: 1; transform: translate3d(0, 0, 0) scale(1); }
}
@media (max-width: 760px) {
  .picker-layout { grid-template-columns: minmax(0, 1fr); gap: 20px; }
  .result-stage { width: 100%; min-height: 480px; padding: 0 8px; }
}
@media (prefers-reduced-motion: reduce) {
  .is-shaking { animation-duration: 80ms; }
  .is-shaking .inner-sticks { animation: none; }
  .is-drawing, .result-card { animation-duration: 80ms; }
}
</style>
