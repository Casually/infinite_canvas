<template>
  <node-view-wrapper class="callout-node-wrapper">
    <BaseBlockWrapper :editor="editor" :node="node" :get-pos="getPos">
      <div 
        class="callout-node p-4 rounded-lg border border-l-4 flex items-start gap-3 transition-colors"
        :style="{
          backgroundColor: style.bg,
          borderColor: style.border,
          borderLeftColor: style.color
        }"
      >
        <div ref="iconWrapRef" class="mt-0.5 select-none relative" contenteditable="false">
          <button 
            @click.stop="togglePicker"
            class="p-1 rounded hover:bg-black/5 transition-colors"
            :style="{ color: style.color }"
            :disabled="!editor.isEditable"
          >
            <component :is="iconComponent" class="w-5 h-5" />
          </button>
          
          <!-- Type Selector Tooltip -->
          <div v-if="showPicker" class="absolute top-full left-0 mt-1 bg-white shadow-lg border rounded p-1 flex gap-1 z-10">
            <button 
              v-for="t in types" 
              :key="t"
              @click.stop="setType(t)"
              class="p-1 rounded hover:bg-gray-100"
              :class="{ 'bg-gray-100': node.attrs.type === t }"
              :title="t"
            >
              <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: getStyle(t).color }"></div>
            </button>
          </div>
        </div>
        <node-view-content class="flex-1 min-w-0" />
      </div>
    </BaseBlockWrapper>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { nodeViewProps, NodeViewWrapper, NodeViewContent } from '@tiptap/vue-3'
import { Info, AlertTriangle, XCircle, CheckCircle, Lightbulb, HelpCircle, AlertOctagon, Flame } from 'lucide-vue-next'
import BaseBlockWrapper from './BaseBlockWrapper.vue'

const props = defineProps(nodeViewProps)

const types = ['info', 'warning', 'error', 'success', 'tip', 'question', 'important', 'bug']
const showPicker = ref(false)
const iconWrapRef = ref<HTMLElement | null>(null)

const getStyle = (type: string) => {
  switch (type) {
    case 'warning': return { bg: '#fff9db', border: '#ffe066', color: '#f59f00' }
    case 'error': return { bg: '#ffe3e3', border: '#ffa8a8', color: '#fa5252' }
    case 'success': return { bg: '#e6fcf5', border: '#63e6be', color: '#20c997' }
    case 'tip': return { bg: '#e7f5ff', border: '#74c0fc', color: '#339af0' }
    case 'question': return { bg: '#f3f0ff', border: '#b197fc', color: '#845ef7' }
    case 'important': return { bg: '#f8f0fc', border: '#faa2c1', color: '#e64980' }
    case 'bug': return { bg: '#fff5f5', border: '#ff8787', color: '#e03131' }
    default: return { bg: '#f8f9fa', border: '#dee2e6', color: '#495057' } // info
  }
}

const style = computed(() => getStyle(props.node.attrs.type))

const iconComponent = computed(() => {
  switch (props.node.attrs.type) {
    case 'warning': return AlertTriangle
    case 'error': return XCircle
    case 'success': return CheckCircle
    case 'tip': return Lightbulb
    case 'question': return HelpCircle
    case 'important': return AlertOctagon
    case 'bug': return Flame
    default: return Info
  }
})

const setType = (type: string) => {
  if (!props.editor.isEditable) return
  props.updateAttributes({ type })
  showPicker.value = false
}

const togglePicker = () => {
  if (!props.editor.isEditable) return
  showPicker.value = !showPicker.value
}

const onDocMouseDown = (e: MouseEvent) => {
  if (!showPicker.value) return
  const el = iconWrapRef.value
  if (!el) return
  if (e.target instanceof Node && el.contains(e.target)) return
  showPicker.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', onDocMouseDown)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onDocMouseDown)
})
</script>

<style>
/* Callout Styles */
.callout-node p {
  margin: 0;
}
</style>
