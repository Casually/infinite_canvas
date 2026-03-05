<template>
  <div class="base-block-wrapper relative group my-4">
    <!-- Unified Drag Handle -->
    <div 
      v-if="editor.isEditable"
      class="absolute -top-3 -left-4 p-1 cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100 transition-opacity z-10 bg-gray-100 rounded shadow-sm hover:bg-gray-200 border border-gray-200"
      contenteditable="false"
      data-drag-handle
      title="拖动块 (右键打开菜单)"
      @contextmenu.prevent.stop="showContextMenu"
    >
      <GripVertical class="w-4 h-4 text-gray-500" />
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div 
        v-if="isMenuVisible" 
        class="fixed z-[9999] bg-white border border-gray-200 rounded-lg shadow-xl py-1 w-40 text-sm"
        :style="{ left: menuPos.x + 'px', top: menuPos.y + 'px' }"
        @click.stop="closeContextMenu"
      >
        <button 
          class="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center gap-2"
          @click="handleCopy"
        >
          <Copy class="w-4 h-4 text-gray-500" />
          <span>复制块</span>
        </button>
        <div class="h-px bg-gray-100 my-1"></div>
        <button 
          class="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center gap-2"
          @click="addParagraphBefore"
        >
          <ArrowUpToLine class="w-4 h-4 text-gray-500" />
          <span>向上插入段落</span>
        </button>
        <button 
          class="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center gap-2"
          @click="addParagraphAfter"
        >
          <ArrowDownToLine class="w-4 h-4 text-gray-500" />
          <span>向下插入段落</span>
        </button>
        <div class="h-px bg-gray-100 my-1"></div>
        <button 
          class="w-full text-left px-3 py-2 hover:bg-red-50 text-red-600 flex items-center gap-2"
          @click="handleDelete"
        >
          <Trash2 class="w-4 h-4" />
          <span>删除块</span>
        </button>
      </div>
    </Teleport>

    <!-- Content Slot -->
    <slot></slot>

    <!-- Bottom Insert Button -->
    <div 
      v-if="editor.isEditable" 
      class="h-4 -mb-2 hover:bg-blue-50 cursor-text flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity text-xs text-blue-400 mt-1"
      @click="addParagraphAfter"
      title="点击在下方插入新段落"
      contenteditable="false"
    >
      <span class="bg-white px-2 py-0.5 rounded shadow-sm border border-blue-100 select-none">+ 插入段落</span>
    </div>

    <!-- Overlay to close menu -->
    <div 
      v-if="isMenuVisible" 
      class="fixed inset-0 z-[9998]" 
      @click="closeContextMenu"
      @contextmenu.prevent="closeContextMenu"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Editor } from '@tiptap/core'
import { type NodeViewProps } from '@tiptap/vue-3'
import { GripVertical, Copy, Trash2, ArrowUpToLine, ArrowDownToLine } from 'lucide-vue-next'

const props = defineProps<{
  editor: Editor
  node: NodeViewProps['node']
  getPos: () => number | boolean
}>()

const isMenuVisible = ref(false)
const menuPos = ref({ x: 0, y: 0 })

const showContextMenu = (e: MouseEvent) => {
  if (!props.editor.isEditable) return
  
  e.preventDefault()
  isMenuVisible.value = true
  menuPos.value = { x: e.clientX, y: e.clientY }
  
  // Select the node when right-clicking the handle
  const pos = props.getPos()
  if (typeof pos === 'number') {
    props.editor.commands.setNodeSelection(pos)
  }
}

const closeContextMenu = () => {
  isMenuVisible.value = false
}

const addParagraphBefore = () => {
  const pos = props.getPos()
  if (typeof pos !== 'number') return
  
  props.editor.chain().insertContentAt(pos, { type: 'paragraph' }).focus(pos).run()
  closeContextMenu()
}

const addParagraphAfter = () => {
  const pos = props.getPos()
  if (typeof pos !== 'number') return
  
  const afterPos = pos + props.node.nodeSize
  const targetPos = Math.min(afterPos, props.editor.state.doc.content.size)
  
  props.editor.chain()
    .insertContentAt(targetPos, { type: 'paragraph' })
    .setTextSelection(targetPos + 1)
    .focus()
    .run()
    
  closeContextMenu()
}

const handleCopy = () => {
  const pos = props.getPos()
  if (typeof pos !== 'number') return
  
  // Select node first
  props.editor.commands.setNodeSelection(pos)
  
  // Execute copy command
  // Note: execCommand is deprecated but still the most reliable way for rich text copy without Clipboard API complexity
  document.execCommand('copy')
  
  closeContextMenu()
}

const handleDelete = () => {
  const pos = props.getPos()
  if (typeof pos !== 'number') return
  
  props.editor.commands.deleteSelection()
  closeContextMenu()
}
</script>
