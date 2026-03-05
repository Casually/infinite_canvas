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
        <div class="flex gap-1">
          <kbd class="hidden sm:inline-block px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs text-gray-500 font-sans">ESC</kbd>
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
                'bg-gray-100 text-gray-500': item.type === 'node-content'
              }"
            >
              {{ 
                item.type === 'group-title' ? '分组标题' : 
                item.type === 'node-title' ? '节点标题' : '节点内容' 
              }}
            </span>
          </div>
          <div class="text-xs text-gray-400 mt-1 truncate">
             匹配度: {{ Math.round(item.score * 100) }}%
          </div>
        </div>
      </div>
      
      <div v-else-if="query" class="p-8 text-center text-gray-500 text-sm">
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
  type: 'group-title' | 'node-title' | 'node-content'
}

const props = defineProps<{
  nodes: any[]
  visible: boolean
}>()

const emit = defineEmits(['close', 'select'])

const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref<HTMLInputElement>()

// Simple search implementation
const results = computed(() => {
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
      const rawContent = node.data.content
      const textContent = rawContent.replace(/<[^>]*>/g, ' ')
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