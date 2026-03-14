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
          placeholder="搜索节点内容..."
          @keydown.down.prevent="navigate('down')"
          @keydown.up.prevent="navigate('up')"
          @keydown.enter="select"
          @keydown.esc="close"
        />
        <div class="flex gap-2 items-center">
          <button
            class="px-2 py-1 text-xs rounded border border-gray-200 bg-white text-gray-600 hover:bg-gray-100"
            :class="mode === 'unfinished-tasks' ? 'border-blue-300 text-blue-600 bg-blue-50' : ''"
            @click.stop="toggleUnfinishedTasks"
            title="查看全部未完成任务"
          >
            未完成任务
          </button>
          <button
            class="px-2 py-1 text-xs rounded border border-gray-200 bg-white text-gray-600 hover:bg-gray-100"
            :class="mode === 'timers' ? 'border-blue-300 text-blue-600 bg-blue-50' : ''"
            @click.stop="toggleTimers"
            title="查看全部定时任务"
          >
            定时任务
          </button>
          <button
            class="px-2 py-1 text-xs rounded border border-gray-200 bg-white text-gray-600 hover:bg-gray-100"
            :class="mode === 'mentions' ? 'border-blue-300 text-blue-600 bg-blue-50' : ''"
            @click.stop="toggleMentions"
            title="查看@用户"
          >
            @用户
          </button>
          <kbd class="hidden sm:inline-block px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs text-gray-500 font-sans">ESC</kbd>
        </div>
      </div>

      <div v-if="mode === 'search'" class="px-4 py-2 border-b border-gray-100 bg-white flex flex-wrap gap-2 items-center">
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
                'bg-purple-100 text-purple-700': item.type === 'timer',
                'bg-indigo-100 text-indigo-700': item.type === 'mention'
              }"
            >
              {{ 
                item.type === 'group-title' ? '分组标题' : 
                item.type === 'node-title' ? '节点标题' :
                item.type === 'task-unchecked' ? '未完成任务' :
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
        输入关键词搜索...
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
  type: 'group-title' | 'node-title' | 'node-content' | 'task-unchecked' | 'timer' | 'mention'
}

const props = defineProps<{
  nodes: any[]
  visible: boolean
}>()

const emit = defineEmits(['close', 'select'])

const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref<HTMLInputElement>()
const mode = ref<'search' | 'unfinished-tasks' | 'timers' | 'mentions'>('search')

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

const clearFilters = () => {
  selectedFilters.value = new Set()
}

const toggleFilter = (id: string) => {
  const next = new Set(selectedFilters.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedFilters.value = next
}

const toggleUnfinishedTasks = () => {
  mode.value = mode.value === 'unfinished-tasks' ? 'search' : 'unfinished-tasks'
  query.value = ''
}

const toggleTimers = () => {
  mode.value = mode.value === 'timers' ? 'search' : 'timers'
  query.value = ''
}

const toggleMentions = () => {
  mode.value = mode.value === 'mentions' ? 'search' : 'mentions'
  query.value = ''
}

const parseDoc = (html: string) => {
  try {
    const parser = new DOMParser()
    return parser.parseFromString(html, 'text/html')
  } catch {
    return null
  }
}

const getTextContent = (html: string) => {
  const doc = parseDoc(html)
  if (!doc) return html.replace(/<[^>]*>/g, ' ')
  return (doc.body?.textContent || '').replace(/\s+/g, ' ').trim()
}

const getFileExt = (url: string) => {
  const clean = url.split('?')[0]
  const parts = clean.split('.')
  if (parts.length < 2) return ''
  return parts.pop()!.toLowerCase()
}

const detectBlockTypes = (html: string) => {
  const doc = parseDoc(html)
  const set = new Set<string>()
  if (!doc) return set

  if (doc.querySelector('pre code')) set.add('code')
  if (doc.querySelector('table')) set.add('table')
  if (doc.querySelector('mermaid-diagram')) set.add('mermaid')
  if (doc.querySelector('.katex, math, mjx-container')) set.add('math')
  if (doc.querySelector('img')) set.add('image')
  if (doc.querySelector('audio')) set.add('audio')
  if (doc.querySelector('video')) set.add('video')

  const links = Array.from(doc.querySelectorAll('a'))
  if (links.length > 0) set.add('link')
  const fileExts = new Set(['pdf', 'xlsx', 'xls', 'docx', 'ppt', 'pptx'])
  if (links.some(a => fileExts.has(getFileExt((a.getAttribute('href') || ''))))) set.add('file')

  const taskNodes = doc.querySelectorAll('input[type="checkbox"], li[data-checked]')
  if (taskNodes.length > 0) set.add('task')

  return set
}

const extractUnfinishedTasks = (html: string) => {
  const doc = parseDoc(html)
  if (!doc) return [] as string[]

  const tasks: string[] = []

  const liNodes = Array.from(doc.querySelectorAll('li'))
  liNodes.forEach(li => {
    const checkedAttr = li.getAttribute('data-checked')
    const checkbox = li.querySelector('input[type="checkbox"]') as HTMLInputElement | null
    const checked = checkedAttr ? checkedAttr === 'true' : (checkbox ? checkbox.checked : null)
    if (checked === false) {
      const text = (li.textContent || '').replace(/\s+/g, ' ').trim()
      if (text) tasks.push(text)
    }
  })

  if (tasks.length > 0) return tasks

  const inputs = Array.from(doc.querySelectorAll('input[type="checkbox"]')) as HTMLInputElement[]
  inputs.forEach(input => {
    if (!input.checked) {
      const li = input.closest('li')
      const text = (li?.textContent || '').replace(/\s+/g, ' ').trim()
      if (text) tasks.push(text)
    }
  })

  return tasks
}

const extractMentions = (html: string) => {
  const doc = parseDoc(html)
  if (!doc) return [] as { id: string, name: string }[]
  const els = Array.from(doc.querySelectorAll('[data-type="mention"]')) as HTMLElement[]
  return els.map(el => ({
    id: el.getAttribute('data-mention-id') || '',
    name: el.getAttribute('data-mention-name') || (el.textContent || '').replace('@', '').trim(),
  })).filter(x => x.name)
}

// Simple search implementation
const results = computed(() => {
  if (mode.value === 'unfinished-tasks') {
    const taskResults: SearchResult[] = []
    props.nodes.forEach(node => {
      if (node.type !== 'note' || !node.data?.content) return
      const tasks = extractUnfinishedTasks(node.data.content)
      if (tasks.length === 0) return
      tasks.forEach(task => {
        taskResults.push({
          id: node.id,
          content: task,
          score: 1,
          x: node.position.x,
          y: node.position.y,
          type: 'task-unchecked'
        })
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
    const q = query.value.trim().toLowerCase()
    props.nodes.forEach((node: any) => {
      if (node.type !== 'note' || !node.data?.content) return
      const ms = extractMentions(node.data.content)
      ms.forEach(m => {
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

  if (!query.value.trim()) return []
  
  const q = query.value.toLowerCase()
  const searchResults: SearchResult[] = []
  
  props.nodes.forEach(node => {
    // 1. Search in Title (Label)
    const label = node.data?.label || ''
    const lowerLabel = label.toLowerCase()
    
    if (lowerLabel.includes(q)) {
      let score = 0.5
      if (lowerLabel.startsWith(q)) score += 0.3
      if (lowerLabel === q) score += 0.2
      
      searchResults.push({
        id: node.id,
        content: label,
        score: score + 0.1, // Boost titles slightly
        x: node.position.x,
        y: node.position.y,
        type: node.type === 'group' ? 'group-title' : 'node-title'
      })
    }
    
    // 2. Search in Content (for notes)
    if (node.type === 'note' && node.data?.content) {
      const types = detectBlockTypes(node.data.content)
      if (selectedFilters.value.size > 0) {
        const ok = Array.from(selectedFilters.value).every(t => types.has(t))
        if (!ok) return
      }

      const rawContent = node.data.content
      const textContent = getTextContent(rawContent)
      const lowerContent = textContent.toLowerCase()
      
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
        
        searchResults.push({
          id: node.id,
          content: preview,
          score,
          x: node.position.x,
          y: node.position.y,
          type: 'node-content'
        })
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
    mode.value = 'search'
    clearFilters()
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
