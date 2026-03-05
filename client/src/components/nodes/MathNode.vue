<template>
  <node-view-wrapper class="math-node relative inline-block">
    <div 
      v-if="!isEditable" 
      v-html="renderedMath" 
      class="cursor-pointer px-1 rounded hover:bg-gray-100"
      @click="isEditable = true"
    ></div>
    <div v-else class="flex items-center">
      <span class="mr-1 text-gray-400">$</span>
      <input
        ref="inputRef"
        v-model="latex"
        class="border-b border-gray-300 outline-none min-w-[50px] font-mono text-sm"
        @blur="handleBlur"
        @keydown.enter.prevent="handleBlur"
        placeholder="E=mc^2"
        autofocus
      />
      <span class="ml-1 text-gray-400">$</span>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps(nodeViewProps)

const latex = ref(props.node.attrs.latex || '')
const isEditable = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

const renderedMath = computed(() => {
  try {
    return katex.renderToString(latex.value || 'E=mc^2', {
      throwOnError: false,
      displayMode: false
    })
  } catch (e) {
    return 'Invalid Equation'
  }
})

const handleBlur = () => {
  if (latex.value.trim()) {
    props.updateAttributes({ latex: latex.value })
    isEditable.value = false
  }
}

watch(isEditable, (val) => {
  if (val) {
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

onMounted(() => {
  if (!props.node.attrs.latex) {
    isEditable.value = true
  }
})
</script>

<style>
.math-node {
  display: inline-block;
}
</style>
