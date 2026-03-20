<template>
  <div v-if="visible" class="fixed top-0 left-0 w-full h-full z-[200] flex justify-center pt-20 bg-black/20 backdrop-blur-sm" @click.self="close">
    <div class="w-[600px] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[60vh] border border-gray-200">
      <div class="flex items-center px-4 py-3 border-b border-gray-100 bg-gray-50/50">
        <svg class="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        <input 
          ref="searchInput"
          v-model="query"
          type="text"
          class="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400 text-lg"
          placeholder="搜索…（/任务 /用户 张三 关键词）"
          @keydown.down.prevent="navigate('down')"
          @keydown.up.prevent="navigate('up')"
          @keydown.enter="select"
          @keydown.esc="close"
        />
        <div class="flex gap-2 items-center">
          <span class="hidden sm:inline-flex px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600 border border-gray-200">
            {{ modeLabel }}
          </span>
          <button
            class="px-2 py-1 text-xs rounded border border-gray-200 bg-white text-gray-600 hover:bg-gray-100"
            :class="showAdvanced ? 'border-blue-300 text-blue-600 bg-blue-50' : ''"
            @click.stop="showAdvanced = !showAdvanced"
            title="筛选"
          >
            筛选
          </button>
          <kbd class="hidden sm:inline-block px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs text-gray-500 font-sans">ESC</kbd>
        </div>
      </div>

      <div v-if="showAdvanced && mode === 'search'" class="px-4 py-2 border-b border-gray-100 bg-white flex flex-wrap gap-2 items-center">
        <span class="text-xs text-gray-400">筛选：</span>
        <button
          v-for="f in filters"
          :key="f.id"
          class="px-2 py-1 text-xs rounded-full border transition-colors"
          :class="selectedFilters.has(f.id) ? 'border-blue-300 bg-blue-50 text-blue-700' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
          @click.stop="toggleFilter(f.id)"
        >
          {{ f.label }}
        </button>
        <div class="flex-1" />
        <button
          class="text-xs text-gray-500 hover:text-gray-700"
          @click.stop="clearFilters"
        >
          清空
        </button>
      </div>

      <div v-if="showAdvanced && (mode === 'search' || mode === 'unfinished-tasks' || mode === 'completed-tasks')" class="px-4 py-2 border-b border-gray-100 bg-white flex flex-wrap gap-2 items-center">
        <span class="text-xs text-gray-400">时间：</span>
        <input
          v-model="timeStart"
          type="datetime-local"
          class="text-xs border border-gray-200 rounded px-2 py-1 text-gray-700"
        />
        <span class="text-xs text-gray-400">-</span>
        <input
          v-model="timeEnd"
          type="datetime-local"
          class="text-xs border border-gray-200 rounded px-2 py-1 text-gray-700"
        />
        <div class="flex-1" />
        <div class="flex flex-wrap gap-2 items-center">
          <button
            v-for="tf in timeFieldOptions"
            :key="tf.id"
            class="px-2 py-1 text-xs rounded-full border transition-colors"
            :class="selectedTimeFields.has(tf.id) ? 'border-blue-300 bg-blue-50 text-blue-700' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
            @click.stop="toggleTimeField(tf.id)"
          >
            {{ tf.label }}
          </button>
          <button
            class="text-xs text-gray-500 hover:text-gray-700"
            @click.stop="clearTimeFilter"
          >
            清空
          </button>
        </div>
      </div>
      
      <div v-if="results.length > 0" class="overflow-y-auto py-2">
        <div 
          v-for="(item, index) in results" 
          :key="item.id + item.type"
          class="px-4 py-3 cursor-pointer transition-colors border-l-4"
          :class="index === selectedIndex ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50 border-transparent'"
          @click="selectItem(index)"
          @mouseenter="selectedIndex = index"
        >
          <div class="flex justify-between items-start">
            <div class="font-medium text-gray-800 text-sm truncate pr-4">{{ item.content || '无文本内容' }}</div>
            <span 
              class="text-xs whitespace-nowrap px-1.5 py-0.5 rounded"
              :class="{
                'bg-blue-100 text-blue-600': item.type === 'group-title',
                'bg-green-100 text-green-600': item.type === 'node-title',
                'bg-gray-100 text-gray-500': item.type === 'node-content',
                'bg-orange-100 text-orange-700': item.type === 'task-unchecked',
                'bg-emerald-100 text-emerald-700': item.type === 'task-checked',
                'bg-purple-100 text-purple-700': item.type === 'timer',
                'bg-indigo-100 text-indigo-700': item.type === 'mention'
              }"
            >
              {{ 
                item.type === 'group-title' ? '分组标题' : 
                item.type === 'node-title' ? '节点标题' :
                item.type === 'task-unchecked' ? '未完成任务' :
                item.type === 'task-checked' ? '已完成任务' :
                item.type === 'timer' ? '定时任务' :
                item.type === 'mention' ? '@用户' : '节点内容' 
              }}
            </span>
          </div>
          <div class="text-xs text-gray-400 mt-1 truncate">
             匹配度: {{ Math.round(item.score * 100) }}%
          </div>
        </div>
      </div>
      
      <div v-else-if="query || mode !== 'search'" class="p-8 text-center text-gray-500 text-sm">
        未找到相关节点
      </div>
      
      <div v-else class="p-8 text-center text-gray-400 text-sm">
        输入关键词搜索，或使用 /任务、/完成任务 指令...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

export interface SearchResult {
  id: string
  content: string
  score: number
  x: number
  y: number
  type: 'group-title' | 'node-title' | 'node-content' | 'task-unchecked' | 'task-checked' | 'timer' | 'mention'
  nodeCreatedAtMs?: number | null
  nodeUpdatedAtMs?: number | null
  taskCreatedAtMs?: number | null
  taskCompletedAtMs?: number | null
}

const props = defineProps<{
  nodes: any[]
  visible: boolean
}>()

const emit = defineEmits(['close', 'select'])

const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref<HTMLInputElement>()
const showAdvanced = ref(false)

type SearchMode = 'search' | 'unfinished-tasks' | 'completed-tasks' | 'timers' | 'mentions'

type ParsedParams = {
  from?: string
  to?: string
  field?: string
  types?: string[]
  user?: string
}

const splitArgs = (input: string) => {
  const out: string[] = []
  let buf = ''
  let quote: '"' | "'" | null = null

  const push = () => {
    const v = buf.trim()
    if (v) out.push(v)
    buf = ''
  }

  for (let i = 0; i < input.length; i++) {
    const ch = input[i]
    if (quote) {
      if (ch === quote) {
        quote = null
      } else {
        buf += ch
      }
      continue
    }

    if (ch === '"' || ch === "'") {
      quote = ch
      continue
    }

    if (/\s/.test(ch)) {
      push()
      continue
    }

    buf += ch
  }
  push()
  return out
}

const normalizeKey = (k: string) => {
  const key = (k || '').trim().toLowerCase()
  if (key === 'start' || key === 'from' || key === 'begin' || key === '开始') return 'from'
  if (key === 'end' || key === 'to' || key === 'stop' || key === '结束') return 'to'
  if (key === 'field' || key === 'timefield' || key === '字段') return 'field'
  if (key === 'type' || key === 'types' || key === '类型') return 'types'
  if (key === 'user' || key === 'u' || key === '用户') return 'user'
  return key
}

const normalizeTypeValue = (v: string) => {
  const s = (v || '').trim()
  const lower = s.toLowerCase()
  const map: Record<string, string> = {
    task: 'task',
    任务: 'task',
    code: 'code',
    代码: 'code',
    table: 'table',
    表格: 'table',
    mermaid: 'mermaid',
    chart: 'mermaid',
    图表: 'mermaid',
    math: 'math',
    公式: 'math',
    image: 'image',
    图片: 'image',
    link: 'link',
    链接: 'link',
    file: 'file',
    附件: 'file',
    audio: 'audio',
    音频: 'audio',
    video: 'video',
    视频: 'video',
  }
  return map[lower] || map[s] || lower
}

const normalizeFieldValue = (v: string) => {
  const s = (v || '').trim()
  const lower = s.toLowerCase()
  const map: Record<string, TimeFieldId> = {
    'node-created': 'node-created',
    'node-updated': 'node-updated',
    'task-created': 'task-created',
    'task-completed': 'task-completed',
    节点创建: 'node-created',
    节点修改: 'node-updated',
    节点更新: 'node-updated',
    任务创建: 'task-created',
    任务完成: 'task-completed',
  }
  return map[lower] || map[s]
}

const normalizeDateTimeLocalString = (input: string, isEnd: boolean) => {
  const s = (input || '').trim()
  if (!s) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    return isEnd ? `${s}T23:59` : `${s}T00:00`
  }
  const m = s.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})(:\d{2})?$/)
  if (m) return `${m[1]}T${m[2]}`
  return s
}

const parseQuery = (input: string) => {
  const raw = (input || '').trim()
  const args = splitArgs(raw)
  const params: ParsedParams = {}
  let baseMode: SearchMode = 'search'
  let modeWasSet = false
  const keywordParts: string[] = []

  const takeUntilNextCmd = (startIndex: number) => {
    const parts: string[] = []
    let i = startIndex
    for (; i < args.length; i++) {
      const t = args[i]
      if (t.startsWith('/')) break
      parts.push(t)
    }
    return { value: parts.join(' ').trim(), nextIndex: i }
  }

  const parseTimeRangeToken = (token: string) => {
    const t = (token || '').trim()
    if (!t) return null
    if (t.includes('~')) {
      const [a, b] = t.split('~').map(x => x.trim()).filter(Boolean)
      if (a || b) return { from: a || undefined, to: b || undefined }
    }
    if (t.includes('至')) {
      const [a, b] = t.split('至').map(x => x.trim()).filter(Boolean)
      if (a || b) return { from: a || undefined, to: b || undefined }
    }
    return null
  }

  for (let i = 0; i < args.length; i++) {
    const a = args[i]

    if (a.startsWith('/')) {
      const cmd = a.trim()

      if (cmd === '/任务') {
        baseMode = 'unfinished-tasks'
        modeWasSet = true
        continue
      }
      if (cmd === '/完成任务' || cmd === '/已完成任务') {
        baseMode = 'completed-tasks'
        modeWasSet = true
        continue
      }
      if (cmd === '/定时任务') {
        baseMode = 'timers'
        modeWasSet = true
        continue
      }
      if (cmd === '/搜索') {
        baseMode = 'search'
        modeWasSet = true
        continue
      }
      if (cmd === '/用户' || cmd === '/@') {
        if (!modeWasSet) {
          baseMode = 'mentions'
          modeWasSet = true
        }
        const { value, nextIndex } = takeUntilNextCmd(i + 1)
        if (value) {
          params.user = value.replace(/^@/, '').replace(/[，,;；。]+$/g, '')
        }
        i = nextIndex - 1
        continue
      }
      if (cmd === '/时间' || cmd === '/time') {
        const next1 = args[i + 1]
        const next2 = args[i + 2]
        if (next1 && !next1.startsWith('/')) {
          const parsed = parseTimeRangeToken(next1)
          if (parsed) {
            if (parsed.from) params.from = parsed.from
            if (parsed.to) params.to = parsed.to
            i += 1
            continue
          }
          params.from = next1
          if (next2 && !next2.startsWith('/')) {
            params.to = next2
            i += 2
          } else {
            i += 1
          }
        }
        continue
      }
      if (cmd === '/开始' || cmd === '/from') {
        const next1 = args[i + 1]
        if (next1 && !next1.startsWith('/')) {
          params.from = next1
          i += 1
        }
        continue
      }
      if (cmd === '/结束' || cmd === '/to') {
        const next1 = args[i + 1]
        if (next1 && !next1.startsWith('/')) {
          params.to = next1
          i += 1
        }
        continue
      }
      if (cmd === '/字段' || cmd === '/field') {
        const next1 = args[i + 1]
        if (next1 && !next1.startsWith('/')) {
          params.field = next1
          i += 1
        }
        continue
      }
      if (cmd === '/类型' || cmd === '/type' || cmd === '/types') {
        const { value, nextIndex } = takeUntilNextCmd(i + 1)
        if (value) {
          const list = value
            .split(/[,\s]+/)
            .map(x => x.trim())
            .filter(Boolean)
            .map(normalizeTypeValue)
            .filter(Boolean)
          params.types = [...(params.types || []), ...list]
        }
        i = nextIndex - 1
        continue
      }

      keywordParts.push(a)
      continue
    }

    const idx = a.indexOf('=')
    if (idx > 0) {
      const k = normalizeKey(a.slice(0, idx))
      const v = a.slice(idx + 1)
      if (!v) continue

      if (k === 'from') params.from = v
      else if (k === 'to') params.to = v
      else if (k === 'field') params.field = v
      else if (k === 'types') {
        const list = v.split(',').map(x => x.trim()).filter(Boolean).map(normalizeTypeValue).filter(Boolean)
        params.types = [...(params.types || []), ...list]
      } else if (k === 'user') {
        params.user = v
      } else {
        keywordParts.push(a)
      }
      continue
    }

    keywordParts.push(a)
  }

  const keyword = keywordParts.join(' ').trim()
  return { mode: baseMode as SearchMode, keyword, params }
}

const parsed = computed(() => parseQuery(query.value))
const mode = computed<SearchMode>(() => parsed.value.mode)
const keyword = computed(() => parsed.value.keyword)
const params = computed(() => parsed.value.params)

const modeLabel = computed(() => {
  if (mode.value === 'unfinished-tasks') return '任务'
  if (mode.value === 'completed-tasks') return '完成任务'
  if (mode.value === 'timers') return '定时任务'
  if (mode.value === 'mentions') return '@用户'
  return '搜索'
})

const filters = [
  { id: 'task', label: '任务' },
  { id: 'code', label: '代码' },
  { id: 'table', label: '表格' },
  { id: 'mermaid', label: '图表' },
  { id: 'math', label: '公式' },
  { id: 'image', label: '图片' },
  { id: 'link', label: '链接' },
  { id: 'file', label: '附件' },
  { id: 'audio', label: '音频' },
  { id: 'video', label: '视频' },
]

const selectedFilters = ref(new Set<string>())
const timeStart = ref('')
const timeEnd = ref('')

type TimeFieldId = 'node-created' | 'node-updated' | 'task-created' | 'task-completed'
const selectedTimeFields = ref(new Set<TimeFieldId>())

const clearTimeFilter = () => {
  timeStart.value = ''
  timeEnd.value = ''
  selectedTimeFields.value = new Set()
  setDefaultTimeFields()
}

const toggleTimeField = (id: TimeFieldId) => {
  const next = new Set(selectedTimeFields.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedTimeFields.value = next
}

const setDefaultTimeFields = () => {
  if (selectedTimeFields.value.size > 0) return
  if (mode.value === 'search') {
    selectedTimeFields.value = new Set<TimeFieldId>(['node-updated'])
  } else if (mode.value === 'unfinished-tasks') {
    selectedTimeFields.value = new Set<TimeFieldId>(['task-created'])
  } else if (mode.value === 'completed-tasks') {
    selectedTimeFields.value = new Set<TimeFieldId>(['task-completed'])
  }
}

const timeFieldOptions = computed(() => {
  if (mode.value === 'search') {
    return [
      { id: 'node-created' as const, label: '节点创建' },
      { id: 'node-updated' as const, label: '节点修改' },
    ]
  }
  return [
    { id: 'task-created' as const, label: '任务创建' },
    { id: 'task-completed' as const, label: '任务完成' },
  ]
})

const clearFilters = () => {
  selectedFilters.value = new Set()
}

const toggleFilter = (id: string) => {
  const next = new Set(selectedFilters.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedFilters.value = next
}

const getFileExt = (url: string) => {
  const clean = url.split('?')[0]
  const parts = clean.split('.')
  if (parts.length < 2) return ''
  return parts.pop()!.toLowerCase()
}

type CachedTask = {
  text: string
  checked: boolean
  createdAtMs: number | null
  completedAtMs: number | null
}

type CachedMention = { id: string, name: string }

type CachedNode = {
  htmlKey: string
  textContent: string
  lowerTextContent: string
  blockTypes: Set<string>
  tasks: CachedTask[]
  mentions: CachedMention[]
}

const nodeCache = ref(new Map<string, CachedNode>())

const parseDoc = (html: string) => {
  try {
    const parser = new DOMParser()
    return parser.parseFromString(html, 'text/html')
  } catch {
    return null
  }
}

const toMs = (v: any) => {
  if (!v) return null
  const t = new Date(v).getTime()
  return Number.isNaN(t) ? null : t
}

const buildCache = (html: string): CachedNode => {
  const doc = parseDoc(html)
  const textContent = (doc?.body?.textContent || html.replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim()
  const lowerTextContent = textContent.toLowerCase()

  const blockTypes = new Set<string>()
  const tasks: CachedTask[] = []
  const mentions: CachedMention[] = []

  if (doc) {
    if (doc.querySelector('pre code')) blockTypes.add('code')
    if (doc.querySelector('table')) blockTypes.add('table')
    if (doc.querySelector('mermaid-diagram')) blockTypes.add('mermaid')
    if (doc.querySelector('.katex, math, mjx-container')) blockTypes.add('math')
    if (doc.querySelector('img')) blockTypes.add('image')
    if (doc.querySelector('audio')) blockTypes.add('audio')
    if (doc.querySelector('video')) blockTypes.add('video')

    const links = Array.from(doc.querySelectorAll('a'))
    if (links.length > 0) blockTypes.add('link')
    const fileExts = new Set(['pdf', 'xlsx', 'xls', 'docx', 'ppt', 'pptx'])
    if (links.some(a => fileExts.has(getFileExt((a.getAttribute('href') || ''))))) blockTypes.add('file')

    const liNodes = Array.from(doc.querySelectorAll('li'))
    liNodes.forEach(li => {
      const checkbox = li.querySelector('input[type="checkbox"]') as HTMLInputElement | null
      const checkedAttr = li.getAttribute('data-checked')
      const checked = checkedAttr ? checkedAttr === 'true' : (checkbox ? checkbox.checked : null)
      if (checked === null) return
      blockTypes.add('task')

      const text = (li.textContent || '').replace(/\s+/g, ' ').trim()
      if (!text) return

      const createdAt = li.getAttribute('data-created-at')
      const completedAt = li.getAttribute('data-completed-at')

      tasks.push({
        text,
        checked,
        createdAtMs: toMs(createdAt),
        completedAtMs: toMs(completedAt),
      })
    })

    const els = Array.from(doc.querySelectorAll('[data-type="mention"]')) as HTMLElement[]
    els.forEach(el => {
      const name = el.getAttribute('data-mention-name') || (el.textContent || '').replace('@', '').trim()
      if (!name) return
      mentions.push({
        id: el.getAttribute('data-mention-id') || '',
        name,
      })
    })
  }

  return {
    htmlKey: html,
    textContent,
    lowerTextContent,
    blockTypes,
    tasks,
    mentions,
  }
}

const getNodeCache = (node: any) => {
  const html = node?.data?.content
  if (typeof html !== 'string' || !html) return null
  const key = String(node.id)
  const existing = nodeCache.value.get(key)
  if (existing && existing.htmlKey === html) return existing
  const next = buildCache(html)
  nodeCache.value.set(key, next)
  return next
}

const rangeMs = computed(() => {
  const fromRaw = params.value.from ? normalizeDateTimeLocalString(params.value.from, false) : timeStart.value
  const toRaw = params.value.to ? normalizeDateTimeLocalString(params.value.to, true) : timeEnd.value

  const start = fromRaw ? new Date(fromRaw).getTime() : null
  const end = toRaw ? new Date(toRaw).getTime() : null
  const s = start !== null && !Number.isNaN(start) ? start : null
  const e = end !== null && !Number.isNaN(end) ? end : null
  return { start: s, end: e }
})

const inRange = (ms: number | null | undefined) => {
  const { start, end } = rangeMs.value
  if (start === null && end === null) return true
  if (ms === null || ms === undefined) return false
  if (start !== null && ms < start) return false
  if (end !== null && ms > end) return false
  return true
}

const matchTime = (r: SearchResult) => {
  const { start, end } = rangeMs.value
  if (start === null && end === null) return true
  const fieldFromCmd = params.value.field ? normalizeFieldValue(params.value.field) : undefined
  const activeFields = fieldFromCmd ? new Set<TimeFieldId>([fieldFromCmd]) : selectedTimeFields.value
  if (activeFields.size === 0) return true

  const checks: boolean[] = []
  activeFields.forEach(f => {
    if (f === 'node-created') checks.push(inRange(r.nodeCreatedAtMs))
    if (f === 'node-updated') checks.push(inRange(r.nodeUpdatedAtMs))
    if (f === 'task-created') checks.push(inRange(r.taskCreatedAtMs))
    if (f === 'task-completed') checks.push(inRange(r.taskCompletedAtMs))
  })
  return checks.some(Boolean)
}

watch(mode, () => {
  const allowed = new Set<TimeFieldId>()
  if (mode.value === 'search') {
    allowed.add('node-created')
    allowed.add('node-updated')
  } else if (mode.value === 'unfinished-tasks' || mode.value === 'completed-tasks') {
    allowed.add('task-created')
    allowed.add('task-completed')
  } else {
    selectedTimeFields.value = new Set()
    return
  }

  const next = new Set<TimeFieldId>()
  selectedTimeFields.value.forEach(f => {
    if (allowed.has(f)) next.add(f)
  })
  selectedTimeFields.value = next
  setDefaultTimeFields()
})

setDefaultTimeFields()

const effectiveTypes = computed(() => {
  const list = params.value.types
  if (!list || list.length === 0) return selectedFilters.value
  return new Set(list)
})

const effectiveUser = computed(() => {
  const u = (params.value.user || '').trim()
  if (!u) return null
  return u.replace(/^@/, '')
})

watch(parsed, () => {
  if (params.value.from) {
    timeStart.value = normalizeDateTimeLocalString(params.value.from, false)
  }
  if (params.value.to) {
    timeEnd.value = normalizeDateTimeLocalString(params.value.to, true)
  }
  const f = params.value.field ? normalizeFieldValue(params.value.field) : undefined
  if (f) {
    selectedTimeFields.value = new Set<TimeFieldId>([f])
  }
  const ts = params.value.types
  if (ts && ts.length > 0) {
    selectedFilters.value = new Set<string>(ts)
  }
})

// Simple search implementation
const results = computed(() => {
  if (mode.value === 'unfinished-tasks') {
    const taskResults: SearchResult[] = []
    const q = keyword.value.trim().toLowerCase()
    const userFilter = (effectiveUser.value || '').trim().toLowerCase()
    const activeTypes = effectiveTypes.value
    props.nodes.forEach((node: any) => {
      if (node.type !== 'note' || !node.data?.content) return
      const cached = getNodeCache(node)
      if (!cached) return
      if (activeTypes.size > 0) {
        const ok = Array.from(activeTypes).every(t => cached.blockTypes.has(t))
        if (!ok) return
      }
      if (userFilter) {
        const ok = cached.mentions.some(m => m.name.toLowerCase().includes(userFilter))
        if (!ok) return
      }
      cached.tasks.forEach(t => {
        if (t.checked) return
        if (q && !t.text.toLowerCase().includes(q)) return
        const r: SearchResult = {
          id: node.id,
          content: t.text,
          score: 1,
          x: node.position.x,
          y: node.position.y,
          type: 'task-unchecked',
          taskCreatedAtMs: t.createdAtMs,
          taskCompletedAtMs: t.completedAtMs,
          nodeCreatedAtMs: toMs(node?.data?.createdAt),
          nodeUpdatedAtMs: toMs(node?.data?.updatedAt),
        }
        if (!matchTime(r)) return
        taskResults.push(r)
      })
    })
    return taskResults.slice(0, 50)
  }

  if (mode.value === 'completed-tasks') {
    const taskResults: SearchResult[] = []
    const q = keyword.value.trim().toLowerCase()
    const userFilter = (effectiveUser.value || '').trim().toLowerCase()
    const activeTypes = effectiveTypes.value
    props.nodes.forEach((node: any) => {
      if (node.type !== 'note' || !node.data?.content) return
      const cached = getNodeCache(node)
      if (!cached) return
      if (activeTypes.size > 0) {
        const ok = Array.from(activeTypes).every(t => cached.blockTypes.has(t))
        if (!ok) return
      }
      if (userFilter) {
        const ok = cached.mentions.some(m => m.name.toLowerCase().includes(userFilter))
        if (!ok) return
      }
      cached.tasks.forEach(t => {
        if (!t.checked) return
        if (q && !t.text.toLowerCase().includes(q)) return
        const r: SearchResult = {
          id: node.id,
          content: t.text,
          score: 1,
          x: node.position.x,
          y: node.position.y,
          type: 'task-checked',
          taskCreatedAtMs: t.createdAtMs,
          taskCompletedAtMs: t.completedAtMs,
          nodeCreatedAtMs: toMs(node?.data?.createdAt),
          nodeUpdatedAtMs: toMs(node?.data?.updatedAt),
        }
        if (!matchTime(r)) return
        taskResults.push(r)
      })
    })
    return taskResults.slice(0, 50)
  }

  if (mode.value === 'timers') {
    const timerResults: SearchResult[] = []
    props.nodes.forEach((node: any) => {
      const timers = node?.data?.timers
      if (!Array.isArray(timers)) return
      timers.forEach((t: any) => {
        if (!t) return
        if (!t.enabled) return
        const nextAt = t.nextTriggerAt
        if (!nextAt || Number.isNaN(nextAt)) return
        if (nextAt <= Date.now()) return
        const title = t.title || '定时任务'
        timerResults.push({
          id: node.id,
          content: `${title} · ${new Date(nextAt).toLocaleString()}`,
          score: 1,
          x: node.position.x,
          y: node.position.y,
          type: 'timer',
        })
      })
    })
    timerResults.sort((a, b) => a.content.localeCompare(b.content))
    return timerResults.slice(0, 50)
  }

  if (mode.value === 'mentions') {
    const mentionResults: SearchResult[] = []
    const q = (effectiveUser.value || keyword.value).trim().toLowerCase()
    props.nodes.forEach((node: any) => {
      if (node.type !== 'note' || !node.data?.content) return
      const cached = getNodeCache(node)
      if (!cached) return
      cached.mentions.forEach(m => {
        if (q && !m.name.toLowerCase().includes(q)) return
        mentionResults.push({
          id: node.id,
          content: `@${m.name}`,
          score: 1,
          x: node.position.x,
          y: node.position.y,
          type: 'mention',
        })
      })
    })
    return mentionResults.slice(0, 50)
  }

  if (!keyword.value.trim()) return []
  
  const q = keyword.value.toLowerCase()
  const searchResults: SearchResult[] = []
  
  props.nodes.forEach((node: any) => {
    const nodeCreatedAtMs = toMs(node?.data?.createdAt)
    const nodeUpdatedAtMs = toMs(node?.data?.updatedAt)
    const userFilter = effectiveUser.value

    if (userFilter && node.type === 'note' && node.data?.content) {
      const cachedForUser = getNodeCache(node)
      if (!cachedForUser) return
      const ok = cachedForUser.mentions.some(m => m.name.toLowerCase().includes(userFilter.toLowerCase()))
      if (!ok) return
    }

    // 1. Search in Title (Label)
    const label = node.data?.label || ''
    const lowerLabel = label.toLowerCase()
    
    if (lowerLabel.includes(q)) {
      let score = 0.5
      if (lowerLabel.startsWith(q)) score += 0.3
      if (lowerLabel === q) score += 0.2
      
      const r: SearchResult = {
        id: node.id,
        content: label,
        score: score + 0.1, // Boost titles slightly
        x: node.position.x,
        y: node.position.y,
        type: node.type === 'group' ? 'group-title' : 'node-title',
        nodeCreatedAtMs,
        nodeUpdatedAtMs,
      }
      if (matchTime(r)) searchResults.push(r)
    }
    
    // 2. Search in Content (for notes)
    if (node.type === 'note' && node.data?.content) {
      const cached = getNodeCache(node)
      if (!cached) return
      const types = cached.blockTypes
      const activeTypes = effectiveTypes.value
      if (activeTypes.size > 0) {
        const ok = Array.from(activeTypes).every(t => types.has(t))
        if (!ok) return
      }

      const textContent = cached.textContent
      const lowerContent = cached.lowerTextContent
      
      if (lowerContent.includes(q)) {
        let score = 0.5
        if (lowerContent.startsWith(q)) score += 0.3
        if (lowerContent === q) score += 0.2
        
        // Find context for preview
        const index = lowerContent.indexOf(q)
        const start = Math.max(0, index - 20)
        const end = Math.min(textContent.length, index + q.length + 50)
        let preview = textContent.substring(start, end)
        if (start > 0) preview = '...' + preview
        if (end < textContent.length) preview = preview + '...'
        
        const r: SearchResult = {
          id: node.id,
          content: preview,
          score,
          x: node.position.x,
          y: node.position.y,
          type: 'node-content',
          nodeCreatedAtMs,
          nodeUpdatedAtMs,
        }
        if (matchTime(r)) searchResults.push(r)
      }
    }
  })
  
  return searchResults
    .sort((a, b) => b.score - a.score)
    .slice(0, 10) // Limit to top 10
})

watch(() => props.visible, (val) => {
  if (val) {
    query.value = ''
    selectedIndex.value = 0
    showAdvanced.value = false
    clearFilters()
    timeStart.value = ''
    timeEnd.value = ''
    selectedTimeFields.value = new Set()
    setDefaultTimeFields()
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})

watch(results, () => {
  selectedIndex.value = 0
})

const navigate = (direction: 'up' | 'down') => {
  if (results.value.length === 0) return
  
  if (direction === 'down') {
    selectedIndex.value = (selectedIndex.value + 1) % results.value.length
  } else {
    selectedIndex.value = (selectedIndex.value - 1 + results.value.length) % results.value.length
  }
}

const select = () => {
  if (results.value.length > 0) {
    selectItem(selectedIndex.value)
  }
}

const selectItem = (index: number) => {
  const item = results.value[index]
  if (item) {
    emit('select', item)
    close()
  }
}

const close = () => {
  emit('close')
}
</script>
