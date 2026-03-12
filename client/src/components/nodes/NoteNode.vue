<template>
  <div
    class="note-node border rounded-lg shadow-md flex flex-col transition-all duration-200 w-full h-full min-w-[300px] min-h-[100px]"
    :class="[
      selected ? 'ring-2 ring-blue-500' : ''
    ]"
    :style="{ 
      backgroundColor: data.backgroundColor || '#ffffff',
      borderWidth: (data.borderWidth || 1) + 'px',
      borderColor: '#e5e7eb',
      fontSize: (data.fontSize || 16) + 'px',
      color: data.fontColor || '#000000'
    }"
    @dblclick.stop="enterEditMode"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
    ref="nodeRef"
  >
    <NodeResizeControl 
    :min-width="300" 
    :min-height="100" 
    position="bottom-right"
    :node-id="id"
    @resize-end="onResizeEnd"
    class="opacity-0 hover:opacity-100 bg-blue-500 rounded-full w-4 h-4 translate-x-1/2 translate-y-1/2" 
  />

    <!-- Dynamic Handles -->
    <!-- Top -->
    <Handle 
      id="top-target" 
      type="target" 
      :position="Position.Top" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: handlePositions.top + '%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="top-source" 
      type="source" 
      :position="Position.Top" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: handlePositions.top + '%', opacity: isHovered ? 1 : 0 }" 
    />
    
    <!-- Right -->
    <Handle 
      id="right-target" 
      type="target" 
      :position="Position.Right" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: handlePositions.right + '%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="right-source" 
      type="source" 
      :position="Position.Right" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: handlePositions.right + '%', opacity: isHovered ? 1 : 0 }" 
    />
    
    <!-- Bottom -->
    <Handle 
      id="bottom-target" 
      type="target" 
      :position="Position.Bottom" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: handlePositions.bottom + '%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="bottom-source" 
      type="source" 
      :position="Position.Bottom" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: handlePositions.bottom + '%', opacity: isHovered ? 1 : 0 }" 
    />
    
    <!-- Left -->
    <Handle 
      id="left-target" 
      type="target" 
      :position="Position.Left" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: handlePositions.left + '%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="left-source" 
      type="source" 
      :position="Position.Left" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: handlePositions.left + '%', opacity: isHovered ? 1 : 0 }" 
    />

    <!-- Header -->
    <div class="flex items-center justify-between p-2 border-b border-gray-100 bg-opacity-50 drag-handle cursor-grab active:cursor-grabbing">
      <div 
        v-if="!isTitleEditing"
        class="font-bold flex-1 mr-2 text-sm truncate cursor-text"
        :class="{'text-gray-400': !data.label}"
        @dblclick.stop="startTitleEdit"
      >
        {{ data.label || '无标题' }}
      </div>
      <input
        v-else
        ref="titleInputRef"
        v-model="data.label"
        class="font-bold bg-white focus:outline-none flex-1 mr-2 text-sm placeholder-gray-400 rounded px-1 nodrag"
        placeholder="无标题"
        @mousedown.stop
        @blur="stopTitleEdit"
        @keydown.enter="stopTitleEdit"
      />
      <div class="flex items-center space-x-1">
        <button
          v-if="hasAnyTimers"
          @click.stop="openTimerManager(props.id)"
          class="p-1 rounded transition-colors"
          :class="hasActiveTimers ? 'text-orange-500 hover:bg-orange-50' : 'text-gray-400 hover:bg-gray-100'"
          title="定时任务"
        >
          <AlarmClock class="w-4 h-4" />
        </button>
        <button 
          @click.stop="copyToMarkdown" 
          class="p-1 text-gray-400 hover:text-blue-500 rounded transition-colors"
          title="复制为 Markdown"
        >
          <Copy class="w-3.5 h-3.5" />
        </button>
        <button @click.stop="toggleFullscreen" class="p-1 hover:bg-gray-100 rounded text-gray-500" title="全屏预览">
          <Maximize2 class="w-4 h-4" />
        </button>
        <button 
          v-if="!isCollapsed && hasFixedSize" 
          @click.stop="resetSize" 
          class="p-1 hover:bg-gray-100 rounded text-gray-500" 
          title="重置大小"
        >
          <RotateCcw class="w-4 h-4" />
        </button>
        <button @click.stop="toggleCollapse" class="p-1 hover:bg-gray-100 rounded text-gray-500" :title="isCollapsed ? '展开' : '折叠'">
          <component :is="isCollapsed ? ChevronDown : ChevronUp" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Body -->
    <div 
      v-show="!isCollapsed" 
      class="p-4 flex-1 bg-white bg-opacity-50 overflow-y-auto min-h-0 custom-scrollbar" 
      :class="{
        'nodrag': isEditing || isHovered // Optional: make it easier to interact with content
      }"
      @wheel.stop
      @dblclick.capture="onDblClickCapture"
      @dblclick.stop="handleDblClickBubble"
    >
      <TiptapEditor 
        ref="editorRef" 
        v-model="content" 
        :editable="isEditing"
        @blur="exitEditMode"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick, reactive, inject, computed } from 'vue'
import { Handle, Position, useVueFlow, type NodeProps } from '@vue-flow/core'
import { NodeResizeControl } from '@vue-flow/node-resizer'
import { Maximize2, ChevronUp, ChevronDown, RotateCcw, Copy, AlarmClock } from 'lucide-vue-next'
import TiptapEditor from './TiptapEditor.vue'
import '@vue-flow/node-resizer/dist/style.css'

const props = defineProps<NodeProps>()

const saveHistory = inject('saveHistory', () => {})
const saveData = inject('saveData', () => {})
const openPreview = inject('openPreview', (_id: string) => {})
const openTimerManager = inject('openNodeTimerManager', (_id: string) => {})

const content = ref(props.data.content || '<p></p>')
const isCollapsed = ref(props.data.isCollapsed || false)
const isEditing = ref(false)
const isTitleEditing = ref(false)
const editorRef = ref()
const titleInputRef = ref<HTMLInputElement>()
const nodeRef = ref<HTMLElement>()

const { findNode } = useVueFlow()

const hasFixedSize = computed(() => {
  const node = findNode(props.id)
  if (!node || !node.style) return false
  const style = node.style as Record<string, any>
  return (style.height && style.height !== 'auto') || (style.width && style.width !== 'auto')
})

const hasActiveTimers = computed(() => {
  const timers = (props.data as any)?.timers
  if (!Array.isArray(timers)) return false
  return timers.some((t: any) => t && t.enabled && t.nextTriggerAt && t.nextTriggerAt > Date.now())
})

const hasAnyTimers = computed(() => {
  const timers = (props.data as any)?.timers
  return Array.isArray(timers) && timers.length > 0
})

const isHovered = ref(false)
const handlePositions = reactive({
  top: 50,
  right: 50,
  bottom: 50,
  left: 50
})

const onMouseMove = (event: MouseEvent) => {
  isHovered.value = true
  if (!nodeRef.value) return

  const rect = nodeRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const w = rect.width
  const h = rect.height

  // Calculate percentage for each side
  const topPercent = Math.min(Math.max((x / w) * 100, 10), 90)
  const bottomPercent = topPercent
  const leftPercent = Math.min(Math.max((y / h) * 100, 10), 90)
  const rightPercent = leftPercent

  // Determine closest edge to update "active" indicator if needed, 
  // but for now we update all positions so handles track mouse on their respective axes
  // Note: We clamp between 10% and 90% to keep handles on the node
  
  handlePositions.top = topPercent
  handlePositions.bottom = bottomPercent
  handlePositions.left = leftPercent
  handlePositions.right = rightPercent
}

const onMouseLeave = () => {
  isHovered.value = false
}

watch(content, (val) => {
  props.data.content = val
})

watch(() => props.data.content, (val) => {
  if (val !== content.value) {
    content.value = val
  }
})

watch(() => props.data.isCollapsed, (val) => {
  if (val !== isCollapsed.value) {
    isCollapsed.value = !!val
  }
})

const toggleCollapse = () => {
  const node = findNode(props.id)
  isCollapsed.value = !isCollapsed.value
  props.data.isCollapsed = isCollapsed.value

  if (node) {
    const style = (node.style || {}) as Record<string, any>
    if (isCollapsed.value) {
      // Collapsing
      if (style.height && style.height !== 'auto') {
        props.data.expandedHeight = style.height
      }
      node.style = { ...style, height: 'auto' }
    } else {
      // Expanding
      if (props.data.expandedHeight) {
        node.style = { ...style, height: props.data.expandedHeight }
      }
    }
  }

  saveHistory()
  saveData()
}

const resetSize = () => {
  const node = findNode(props.id)
  if (node) {
    const style = (node.style || {}) as Record<string, any>
    node.style = { 
      ...style, 
      height: 'auto',
      width: undefined 
    }
    if (props.data.expandedHeight) {
      delete props.data.expandedHeight
    }
    saveHistory()
  }
}

import TurndownService from 'turndown'
import { gfm } from 'turndown-plugin-gfm'
import { useToast } from '../../composables/useToast'

const { addToast } = useToast()

const copyToMarkdown = () => {
  if (!props.data.content) {
    addToast('无内容可复制', 'info')
    return
  }
  
  const turndownService = new TurndownService()
  turndownService.use(gfm)
  
  const markdown = turndownService.turndown(props.data.content)
  navigator.clipboard.writeText(markdown)
  addToast('已复制为 Markdown', 'success')
}

const toggleFullscreen = () => {
  openPreview(props.id)
}

const startTitleEdit = () => {
  if (props.data.editable === false) return
  isTitleEditing.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}

const stopTitleEdit = () => {
  isTitleEditing.value = false
  saveHistory()
}

const onDblClickCapture = (event: MouseEvent) => {
  if (!isEditing.value) {
    event.stopPropagation()
    enterEditMode()
  }
}

const handleDblClickBubble = () => {
  // If we are already editing, do nothing on double click (let the text selection happen)
  // The .stop modifier on the template ensures propagation is stopped to prevent canvas actions
  if (isEditing.value) {
    return
  }
  enterEditMode()
}

const enterEditMode = () => {
  if (props.data.editable === false) return
  isEditing.value = true
  if (isCollapsed.value) {
    isCollapsed.value = false
    nextTick(() => {
      editorRef.value?.focus()
    })
  } else {
    nextTick(() => {
      editorRef.value?.focus()
    })
  }
}

const exitEditMode = () => {
  isEditing.value = false
  saveHistory()
}

const onResizeEnd = (event: any) => {
  const node = findNode(props.id)
  if (node) {
    const h = event.params.height
    const w = event.params.width
    const style = (node.style || {}) as Record<string, any>
    node.style = {
      ...style,
      width: `${w}px`,
      height: `${h}px`,
      minHeight: undefined
    }
  }
  saveHistory()
}

onMounted(() => {
  if (props.data.initialFocus) {
    // Small delay to ensure editor is ready
    setTimeout(() => {
      enterEditMode()
      // Clear initialFocus so it doesn't trigger again on reload
      props.data.initialFocus = false
      saveData()
    }, 100)
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.drag-handle {
  cursor: grab;
}
.drag-handle:active {
  cursor: grabbing;
}

.nodrag {
  cursor: text;
}

:deep(.ProseMirror) {
  color: inherit;
  font-size: inherit;
}

:deep(.ProseMirror p) {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}
</style>
