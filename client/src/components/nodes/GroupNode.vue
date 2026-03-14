<template>
  <div 
    class="group-node border-2 border-dashed border-gray-300 rounded-lg h-full w-full relative transition-colors duration-200"
    :style="{ 
      backgroundColor: data.backgroundColor || 'rgba(239, 246, 255, 0.2)',
      fontSize: (data.fontSize || 14) + 'px',
      color: data.fontColor || '#1e40af'
    }"
    @mousemove="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <NodeResizer :min-width="200" :min-height="200" is-visible @resize-end="saveHistory" />

    <Handle 
      id="top-target" 
      type="target" 
      :position="Position.Top" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: '50%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="top-source" 
      type="source" 
      :position="Position.Top" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: '50%', opacity: isHovered ? 1 : 0 }" 
    />

    <Handle 
      id="right-target" 
      type="target" 
      :position="Position.Right" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: '50%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="right-source" 
      type="source" 
      :position="Position.Right" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: '50%', opacity: isHovered ? 1 : 0 }" 
    />

    <Handle 
      id="bottom-target" 
      type="target" 
      :position="Position.Bottom" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: '50%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="bottom-source" 
      type="source" 
      :position="Position.Bottom" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ left: '50%', opacity: isHovered ? 1 : 0 }" 
    />

    <Handle 
      id="left-target" 
      type="target" 
      :position="Position.Left" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: '50%', opacity: isHovered ? 1 : 0 }" 
    />
    <Handle 
      id="left-source" 
      type="source" 
      :position="Position.Left" 
      class="!bg-blue-400 !w-3 !h-3 transition-opacity duration-200" 
      :style="{ top: '50%', opacity: isHovered ? 1 : 0 }" 
    />
    <div class="absolute -top-7 left-0 px-2 py-0.5 bg-blue-100 rounded-t text-xs font-bold text-blue-800"
         :style="{ color: data.fontColor || '#1e40af' }"
         @dblclick.stop="startEdit"
    >
      <div 
        v-if="!isEditing" 
        class="w-24 truncate cursor-text"
        :style="{ fontSize: (data.fontSize || 12) + 'px' }"
        :title="data.label || '组名称'"
      >
        {{ data.label || '组名称' }}
      </div>
      <input 
        v-else
        ref="inputRef"
        v-model="data.label" 
        class="bg-transparent focus:outline-none w-24 nodrag" 
        placeholder="组名称" 
        :style="{ fontSize: (data.fontSize || 12) + 'px' }"
        @blur="stopEdit"
        @keydown.enter="stopEdit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, ref, nextTick } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { NodeResizer } from '@vue-flow/node-resizer'
import '@vue-flow/node-resizer/dist/style.css'

const props = defineProps<{
  data: { label: string, backgroundColor?: string, fontSize?: number, fontColor?: string, editable?: boolean }
}>()

const saveHistory = inject('saveHistory', () => {})
const isEditing = ref(false)
const inputRef = ref<HTMLInputElement>()
const isHovered = ref(false)

const startEdit = () => {
  if (props.data.editable === false) return
  isEditing.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const stopEdit = () => {
  isEditing.value = false
  saveHistory()
}
</script>

<style scoped>
.group-node {}
</style>
