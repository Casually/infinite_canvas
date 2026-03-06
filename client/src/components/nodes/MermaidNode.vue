<template>
  <node-view-wrapper class="mermaid-diagram relative group my-4">
    <div class="absolute right-2 top-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10 print:hidden">
      <button 
        class="p-1 text-gray-400 hover:text-gray-600 bg-white/80 hover:bg-white rounded shadow-sm border border-gray-200 transition-colors"
        @click="openPreview"
        title="预览图片"
      >
        <Eye class="w-4 h-4" />
      </button>
      <button 
        class="p-1 text-gray-400 hover:text-gray-600 bg-white/80 hover:bg-white rounded shadow-sm border border-gray-200 transition-colors"
        @click="editDiagram"
        title="编辑图表"
      >
        <Edit3 class="w-4 h-4" />
      </button>
    </div>
    
    <div 
      ref="diagramRef" 
      class="p-4 bg-white rounded-lg border border-gray-200 shadow-sm overflow-x-auto flex justify-center min-h-[100px] cursor-pointer"
      v-html="svgContent"
      @dblclick="openPreview"
    ></div>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div v-if="isPreviewing" class="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm flex items-center justify-center overflow-hidden" @click="closePreview">
        <div class="absolute top-4 right-4 flex gap-2 z-20" @click.stop>
          <button 
            class="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
            @click="scale = Math.min(scale + 0.1, 5)"
            title="放大"
          >
            <ZoomIn class="w-5 h-5" />
          </button>
          <button 
            class="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
            @click="scale = Math.max(scale - 0.1, 0.1)"
            title="缩小"
          >
            <ZoomOut class="w-5 h-5" />
          </button>
          <button 
            class="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
            @click="resetZoom"
            title="重置"
          >
            <Maximize class="w-5 h-5" />
          </button>
          <button 
            class="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
            @click="closePreview"
            title="关闭"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
        
        <div 
          class="w-full h-full flex items-center justify-center overflow-hidden cursor-move"
          @click.stop
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
          @wheel.prevent="onWheel"
        >
          <img 
            :src="svgDataUrl" 
            class="max-w-none bg-white rounded-lg shadow-2xl transition-transform duration-75 ease-linear select-none"
            :style="{
              transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`
            }"
            draggable="false"
          />
        </div>
      </div>
    </Teleport>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div v-if="isEditing" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4">
        <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <div class="flex items-center gap-2">
              <h3 class="font-semibold text-gray-800">编辑 Mermaid 图表</h3>
              <a 
                href="https://mermaid.js.org/intro/" 
                target="_blank" 
                class="text-gray-400 hover:text-blue-500 transition-colors"
                title="查看 Mermaid 语法文档"
              >
                <HelpCircle class="w-4 h-4" />
              </a>
            </div>
            <div class="flex items-center gap-2">
              <button 
                @click="saveAndClose"
                class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-medium transition-colors"
              >
                保存
              </button>
              <button 
                @click="close"
                class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
              >
                取消
              </button>
            </div>
          </div>
          
          <div class="flex-1 flex overflow-hidden">
            <!-- Code Editor -->
            <div class="w-1/2 border-r border-gray-200 flex flex-col">
              <div class="px-4 py-2 bg-gray-50 text-xs text-gray-500 border-b border-gray-200 font-mono">
                Mermaid 代码
              </div>
              <textarea 
                v-model="tempContent"
                class="flex-1 w-full p-4 font-mono text-sm resize-none outline-none focus:bg-gray-50/50"
                spellcheck="false"
              ></textarea>
            </div>
            
            <!-- Preview -->
            <div class="w-1/2 flex flex-col bg-gray-50">
              <div class="px-4 py-2 bg-gray-100 text-xs text-gray-500 border-b border-gray-200">
                预览
              </div>
              <div class="flex-1 p-4 overflow-auto flex justify-center items-center">
                <div v-html="previewSvg" class="max-w-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'
import { Edit3, HelpCircle, Eye, X, ZoomIn, ZoomOut, Maximize } from 'lucide-vue-next'

const props = defineProps(nodeViewProps)

const diagramRef = ref<HTMLElement | null>(null)
const svgContent = ref('')
const isEditing = ref(false)
const isPreviewing = ref(false)
const tempContent = ref('')
const previewSvg = ref('')
const svgDataUrl = ref('')

// Preview controls
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)

// Initialize mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
})

const renderDiagram = async (content: string) => {
  try {
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`
    const { svg } = await mermaid.render(id, content)
    return svg
  } catch (error) {
    console.error('Mermaid render error:', error)
    return `<div class="text-red-500 text-sm font-mono p-2">渲染错误: 请检查 Mermaid 语法</div>`
  }
}

const updateDiagram = async () => {
  if (props.node.attrs.content) {
    svgContent.value = await renderDiagram(props.node.attrs.content)
  }
}

const updatePreview = async () => {
  previewSvg.value = await renderDiagram(tempContent.value)
}

const openPreview = () => {
  if (!svgContent.value) return
  
  // Create a proper SVG data URL by cleaning up the SVG content
  // Mermaid sometimes returns SVG without namespace or with extra attributes that might break direct img src
  
  let svg = svgContent.value
  
  // Ensure xmlns is present
  if (!svg.includes('xmlns="http://www.w3.org/2000/svg"')) {
    svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
  }
  
  // Ensure width and height are present if missing but viewBox exists
  // This is crucial for img src rendering in some browsers
  if (svg.includes('viewBox')) {
      const viewBoxMatch = svg.match(/viewBox="([^"]+)"/)
      if (viewBoxMatch) {
          const parts = viewBoxMatch[1].split(/\s+/)
          if (parts.length === 4) {
              const width = parseFloat(parts[2])
              const height = parseFloat(parts[3])
              if (!svg.includes('width=')) {
                 svg = svg.replace('<svg', `<svg width="${width}"`)
              }
              if (!svg.includes('height=')) {
                 svg = svg.replace('<svg', `<svg height="${height}"`)
              }
          }
      }
  } else {
     // If no viewBox, default to 100% or some reasonable size
     if (!svg.includes('width=')) svg = svg.replace('<svg', '<svg width="800"')
     if (!svg.includes('height=')) svg = svg.replace('<svg', '<svg height="600"')
  }
  
  // Reset preview state
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
  
  // Try to use Base64 encoding for better compatibility
  try {
      const base64 = btoa(unescape(encodeURIComponent(svg)))
      svgDataUrl.value = `data:image/svg+xml;base64,${base64}`
  } catch (e) {
      // Fallback to Blob if base64 fails
      const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
      svgDataUrl.value = URL.createObjectURL(svgBlob)
  }
  
  isPreviewing.value = true
}

const closePreview = () => {
  isPreviewing.value = false
  // Clean up if it was a blob URL
  if (svgDataUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(svgDataUrl.value)
  }
  svgDataUrl.value = ''
}

const resetZoom = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  startX.value = e.clientX - translateX.value
  startY.value = e.clientY - translateY.value
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  translateX.value = e.clientX - startX.value
  translateY.value = e.clientY - startY.value
}

const stopDrag = () => {
  isDragging.value = false
}

const onWheel = (e: WheelEvent) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const newScale = Math.min(Math.max(scale.value + delta, 0.1), 5)
  scale.value = newScale
}

watch(() => tempContent.value, () => {
  if (isEditing.value) {
    updatePreview()
  }
})

const editDiagram = () => {
  tempContent.value = props.node.attrs.content
  isEditing.value = true
  updatePreview()
}

const saveAndClose = () => {
  props.updateAttributes({ content: tempContent.value })
  updateDiagram()
  isEditing.value = false
}

const close = () => {
  isEditing.value = false
}

onMounted(() => {
  updateDiagram()
})
</script>

<style>
.mermaid-diagram svg {
  max-width: 100%;
  height: auto;
}
</style>
