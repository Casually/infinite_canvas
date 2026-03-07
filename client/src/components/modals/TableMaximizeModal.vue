<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[90vw] h-[90vh] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
        <h3 class="text-lg font-medium text-gray-900">表格编辑与导出</h3>
        <div class="flex items-center gap-2">
          <button 
            @click="handleSave" 
            class="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 flex items-center gap-1"
          >
            <Save class="w-4 h-4" /> 保存并关闭
          </button>
          <button 
            @click="exportToExcel" 
            class="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700 flex items-center gap-1"
          >
            <Download class="w-4 h-4" /> 导出 Excel
          </button>
          <button 
            @click="exportToImage" 
            class="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 flex items-center gap-1"
          >
            <ImageIcon class="w-4 h-4" /> 导出图片
          </button>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500 ml-2" title="取消">
            <X class="w-6 h-6" />
          </button>
        </div>
      </div>
      
      <div class="flex-1 overflow-auto p-6 bg-white" ref="contentRef">
        <editor-content :editor="editor" class="prose prose-sm max-w-none focus:outline-none min-h-full" />
      </div>
      
      <div v-if="editor" class="border-t p-2 flex gap-2 justify-center bg-gray-50">
        <button @click="editor.chain().focus().addColumnBefore().run()" class="p-1 hover:bg-gray-200 rounded" title="前插入列">
          <ArrowLeftToLine class="w-4 h-4" />
        </button>
        <button @click="editor.chain().focus().addColumnAfter().run()" class="p-1 hover:bg-gray-200 rounded" title="后插入列">
          <ArrowRightToLine class="w-4 h-4" />
        </button>
        <button @click="editor.chain().focus().deleteColumn().run()" class="p-1 hover:bg-gray-200 rounded text-red-500" title="删除列">
          <Trash2 class="w-4 h-4" />
        </button>
        <div class="w-px h-4 bg-gray-300 mx-1"></div>
        <button @click="editor.chain().focus().addRowBefore().run()" class="p-1 hover:bg-gray-200 rounded" title="上插入行">
          <ArrowUpToLine class="w-4 h-4" />
        </button>
        <button @click="editor.chain().focus().addRowAfter().run()" class="p-1 hover:bg-gray-200 rounded" title="下插入行">
          <ArrowDownToLine class="w-4 h-4" />
        </button>
        <button @click="editor.chain().focus().deleteRow().run()" class="p-1 hover:bg-gray-200 rounded text-red-500" title="删除行">
          <Trash2 class="w-4 h-4" />
        </button>
        <div class="w-px h-4 bg-gray-300 mx-1"></div>
        <button @click="editor.chain().focus().mergeCells().run()" class="p-1 hover:bg-gray-200 rounded" title="合并单元格">
          <Merge class="w-4 h-4" />
        </button>
        <button @click="editor.chain().focus().splitCell().run()" class="p-1 hover:bg-gray-200 rounded" title="拆分单元格">
          <Split class="w-4 h-4" />
        </button>
        <div class="w-px h-4 bg-gray-300 mx-1"></div>
        <div class="relative">
          <button 
            @click="showColorPicker = !showColorPicker" 
            class="p-1 hover:bg-gray-200 rounded" 
            :class="{ 'bg-gray-200': showColorPicker }"
            title="单元格背景色"
          >
            <PaintBucket class="w-4 h-4" />
          </button>
          <div v-if="showColorPicker" class="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-white shadow-lg border rounded p-2 grid grid-cols-4 gap-1 z-50 w-40">
            <button
              v-for="item in tableColors"
              :key="item.label"
              @click="setCellColor(item.color)"
              class="w-6 h-6 rounded border border-gray-200 hover:scale-110 transition-transform"
              :style="{ backgroundColor: item.color || '#fff' }"
              :title="item.label"
            >
              <div v-if="!item.color" class="w-full h-full relative overflow-hidden">
                <div class="absolute inset-0 border-red-500 border-t transform rotate-45 top-1/2"></div>
              </div>
            </button>
            <!-- Custom Color Input -->
            <label class="w-6 h-6 rounded border border-gray-200 hover:scale-110 transition-transform cursor-pointer overflow-hidden relative" title="自定义颜色">
              <input type="color" class="opacity-0 absolute inset-0 w-full h-full cursor-pointer" @input="setCellColor(($event.target as HTMLInputElement).value)" />
              <div class="w-full h-full bg-gradient-to-br from-red-500 via-green-500 to-blue-500"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, onMounted } from 'vue'
import { useEditor, EditorContent, VueNodeViewRenderer } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Table, TableRow, TableHeader, CustomTableCell } from '../nodes/TableExtensions'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'
import MathExtension from '../nodes/MathExtension'
import MermaidExtension from '../nodes/MermaidExtension'
import MusicPlayerExtension from '../nodes/MusicPlayerExtension'
import WebsiteCard from '../nodes/WebsiteCard'
import EChartsExtension from '../nodes/EChartsExtension'
import VideoExtension from '../nodes/VideoExtension'
import AudioExtension from '../nodes/AudioExtension'
import CalloutExtension from '../nodes/CalloutExtension'
import CalendarExtension from '../nodes/CalendarExtension'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { common, createLowlight } from 'lowlight'
import CodeBlockComponent from '../nodes/CodeBlockComponent.vue'
import { Download, Image as ImageIcon, X, ArrowLeftToLine, ArrowRightToLine, Trash2, ArrowUpToLine, ArrowDownToLine, Merge, Split, PaintBucket, Save } from 'lucide-vue-next'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'

const lowlight = createLowlight(common)

const props = defineProps<{
  initialContent: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', content: any): void
}>()

const contentRef = ref<HTMLElement | null>(null)
const showColorPicker = ref(false)

const handleKeyDown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    handleSave()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
  editor.value?.destroy()
})

const tableColors = [
  { color: null, label: '无颜色' },
  { color: '#f8f9fa', label: '灰色' },
  { color: '#ffe3e3', label: '红色' },
  { color: '#e7f5ff', label: '蓝色' },
  { color: '#e6fcf5', label: '绿色' },
  { color: '#fff9db', label: '黄色' },
  { color: '#f3d9fa', label: '紫色' },
]

const editor = useEditor({
  content: props.initialContent,
  extensions: [
    StarterKit.configure({
      codeBlock: false,
    }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableHeader,
    CustomTableCell,
    Image,
    Link.configure({
      openOnClick: false,
      autolink: true,
      HTMLAttributes: {
        target: '_blank',
        rel: 'noopener noreferrer nofollow',
      },
    }),
    TaskList,
    TaskItem.configure({
      nested: true,
    }),
    TextAlign.configure({
      types: ['heading', 'paragraph', 'tableCell', 'tableHeader'],
    }),
    Highlight,
    CodeBlockLowlight.configure({
      lowlight,
    }).extend({
      addNodeView() {
        return VueNodeViewRenderer(CodeBlockComponent)
      },
    }),
    MathExtension,
    MermaidExtension,
    MusicPlayerExtension,
    WebsiteCard,
    EChartsExtension,
    VideoExtension,
    AudioExtension,
    CalloutExtension,
    CalendarExtension,
  ],
})

// Remove duplicate onBeforeUnmount since we handled it above
// onBeforeUnmount(() => {
//   editor.value?.destroy()
// })

const handleSave = () => {
  if (editor.value) {
    emit('save', editor.value.getJSON())
    emit('close')
  }
}

const setCellColor = (color: string | null) => {
  if (editor.value) {
    editor.value.chain().focus().setCellAttribute('backgroundColor', color).run()
  }
  showColorPicker.value = false
}

const exportToExcel = () => {
  if (!contentRef.value) return
  
  const table = contentRef.value.querySelector('table')
  if (!table) {
    alert('未找到表格')
    return
  }

  const wb = XLSX.utils.table_to_book(table)
  XLSX.writeFile(wb, 'table_export.xlsx')
}

const exportToImage = async () => {
  if (!contentRef.value) return
  
  const table = contentRef.value.querySelector('table')
  if (!table) {
    alert('未找到表格')
    return
  }

  try {
    const canvas = await html2canvas(table as HTMLElement, {
      backgroundColor: '#ffffff',
      scale: 2 // Higher resolution
    })
    
    const link = document.createElement('a')
    link.download = 'table_export.png'
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (e) {
    console.error('Export image failed:', e)
    alert('导出图片失败')
  }
}
</script>

<style scoped>
/* Ensure table borders are visible for export/viewing */
:deep(table) {
  border-collapse: collapse;
  table-layout: fixed;
  min-width: 100%;
  margin: 0;
  overflow: hidden;
}

:deep(td), :deep(th) {
  border: 1px solid #ced4da;
  padding: 3px 5px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
  min-width: 1em;
}

:deep(th) {
  font-weight: bold;
  text-align: left;
  background-color: #f1f3f5;
}

:deep(.selectedCell:after) {
  z-index: 2;
  position: absolute;
  content: "";
  left: 0; right: 0; top: 0; bottom: 0;
  background: rgba(200, 200, 255, 0.4);
  pointer-events: none;
}

:deep(.column-resize-handle) {
  position: absolute;
  right: -6px;
  top: 0;
  bottom: 0;
  width: 12px;
  background-color: transparent;
  z-index: 100;
  cursor: col-resize;
  pointer-events: auto;
}

:deep(.column-resize-handle:hover),
:deep(.column-resize-handle.selected) {
  background-color: #adf;
  opacity: 1;
}

:deep(.ProseMirror) {
  min-height: 100%;
}
</style>
