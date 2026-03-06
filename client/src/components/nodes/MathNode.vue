<template>
  <node-view-wrapper class="math-node inline-block align-middle mx-1">
    <div 
      v-if="!isEditing" 
      class="cursor-pointer px-1 rounded hover:bg-gray-100 transition-colors inline-flex items-center"
      @click="startEditing"
      title="点击编辑公式"
      v-html="renderedHtml"
    ></div>
    
    <div v-else class="relative inline-flex items-center bg-white border border-blue-500 rounded shadow-sm z-10">
      <div class="flex items-center px-2 py-1 gap-2">
        <span class="text-gray-400 font-mono text-sm select-none">$</span>
        <input
          ref="inputRef"
          v-model="latex"
          class="outline-none min-w-[100px] font-mono text-sm text-gray-800 bg-transparent"
          @keydown.enter.prevent="finishEditing"
          @keydown.esc="cancelEditing"
          @blur="finishEditing"
          placeholder="E=mc^2"
        />
        <span class="text-gray-400 font-mono text-sm select-none">$</span>
      </div>
      
      <!-- Live Preview Popover -->
      <div class="absolute left-0 top-full mt-1 bg-white border border-gray-200 rounded shadow-lg p-3 min-w-[200px] z-20" @mousedown.prevent>
        <div class="text-xs text-gray-500 mb-2 font-semibold">预览</div>
        <div v-html="previewHtml" class="text-center text-lg py-2"></div>
        <div class="text-[10px] text-gray-400 mt-2 border-t pt-2 flex justify-between">
           <span>Enter 确认</span>
           <span>Esc 取消</span>
        </div>
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps(nodeViewProps)

const latex = ref(props.node.attrs.latex || 'E=mc^2')
const isEditing = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

// Render for the non-editing state
const renderedHtml = computed(() => {
  try {
    return katex.renderToString(props.node.attrs.latex || 'E=mc^2', {
      throwOnError: false,
      displayMode: false,
      output: 'html'
    })
  } catch (e) {
    return `<span class="text-red-500 text-xs">Error</span>`
  }
})

// Render for the live preview
const previewHtml = computed(() => {
  try {
    return katex.renderToString(latex.value || ' ', {
      throwOnError: false,
      displayMode: true, // Display mode for better visibility in preview
      output: 'html'
    })
  } catch (e) {
    return `<span class="text-red-500 text-sm">语法错误</span>`
  }
})

const startEditing = () => {
  latex.value = props.node.attrs.latex || 'E=mc^2'
  isEditing.value = true
  nextTick(() => {
    inputRef.value?.focus()
    inputRef.value?.select()
  })
}

const finishEditing = () => {
  if (latex.value.trim()) {
    props.updateAttributes({ latex: latex.value })
  }
  isEditing.value = false
}

const cancelEditing = () => {
  latex.value = props.node.attrs.latex
  isEditing.value = false
}

onMounted(() => {
    // If just created and default value, maybe auto edit?
    // But for now let's keep it simple.
})
</script>

<style>
.math-node input {
    background: transparent;
}
</style>
