<template>
  <div 
    class="group-node border-2 border-dashed border-gray-300 rounded-lg h-full w-full relative transition-colors duration-200"
    :style="{ 
      backgroundColor: data.backgroundColor || 'rgba(239, 246, 255, 0.2)',
      fontSize: (data.fontSize || 14) + 'px',
      color: data.fontColor || '#1e40af'
    }"
  >
    <NodeResizer :min-width="200" :min-height="200" is-visible @resize-end="saveHistory" />
    <div class="absolute -top-7 left-0 px-2 py-0.5 bg-blue-100 rounded-t text-xs font-bold text-blue-800"
         :style="{ color: data.fontColor || '#1e40af' }"
         @dblclick.stop="startEdit"
    >
      <div 
        v-if="!isEditing" 
        class="w-24 truncate cursor-text"
        :style="{ fontSize: (data.fontSize || 12) + 'px' }"
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
import { NodeResizer } from '@vue-flow/node-resizer'
import '@vue-flow/node-resizer/dist/style.css'

const props = defineProps<{
  data: { label: string, backgroundColor?: string, fontSize?: number, fontColor?: string, editable?: boolean }
}>()

const saveHistory = inject('saveHistory', () => {})
const isEditing = ref(false)
const inputRef = ref<HTMLInputElement>()

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
.group-node {
  /* Ensure it doesn't block clicks on the canvas for selection if empty, 
     but we want to be able to select the group itself. */
}
</style>
