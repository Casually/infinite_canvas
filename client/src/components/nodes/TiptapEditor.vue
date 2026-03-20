<template>
  <div class="tiptap-editor relative" @click="handleEditorClick" @contextmenu.prevent.stop="handleContextMenu">
    <editor-content :editor="editor" class="prose prose-sm max-w-none focus:outline-none" />
    
    <DragHandle v-if="editor && editable" :editor="editor" />

    <bubble-menu
      v-if="editor"
      :editor="editor"
      :tippy-options="{ duration: 100, placement: 'top' }"
      :should-show="shouldShowTableMenu"
      class="flex items-center gap-1 p-1 bg-white border rounded shadow-sm z-50"
    >
      <button @click="editor.chain().focus().addColumnBefore().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="前插入列">
        <ArrowLeftToLine class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().addColumnAfter().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="后插入列">
        <ArrowRightToLine class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().deleteColumn().run()" class="p-1 hover:bg-gray-100 rounded text-red-500" title="删除列">
        <Trash2 class="w-4 h-4" />
      </button>
      <div class="w-px h-4 bg-gray-200 mx-1"></div>
      <button @click="editor.chain().focus().addRowBefore().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="上插入行">
        <ArrowUpToLine class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().addRowAfter().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="下插入行">
        <ArrowDownToLine class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().deleteRow().run()" class="p-1 hover:bg-gray-100 rounded text-red-500" title="删除行">
        <Trash2 class="w-4 h-4" />
      </button>
      <div class="w-px h-4 bg-gray-200 mx-1"></div>
      <button @click="editor.chain().focus().mergeCells().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="合并单元格">
        <Merge class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().splitCell().run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" title="拆分单元格">
        <Split class="w-4 h-4" />
      </button>
      <div class="w-px h-4 bg-gray-200 mx-1"></div>
      <button @click="editor.chain().focus().setTextAlign('left').run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" :class="{ 'bg-gray-200': editor.isActive({ textAlign: 'left' }) }" title="左对齐">
        <AlignLeft class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().setTextAlign('center').run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" :class="{ 'bg-gray-200': editor.isActive({ textAlign: 'center' }) }" title="居中对齐">
        <AlignCenter class="w-4 h-4" />
      </button>
      <button @click="editor.chain().focus().setTextAlign('right').run()" class="p-1 hover:bg-gray-100 rounded text-gray-600" :class="{ 'bg-gray-200': editor.isActive({ textAlign: 'right' }) }" title="右对齐">
        <AlignRight class="w-4 h-4" />
      </button>
      <div class="w-px h-4 bg-gray-200 mx-1"></div>
      <div class="relative">
        <button 
          @click="showColorPicker = !showColorPicker" 
          class="p-1 hover:bg-gray-100 rounded text-gray-600" 
          :class="{ 'bg-gray-100': showColorPicker }"
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
      <button @click="openTableMaximizeModal" class="p-1 hover:bg-gray-100 rounded text-blue-600" title="放大表格">
        <Maximize2 class="w-4 h-4" />
      </button>
    </bubble-menu>

    <Teleport to="body">
      <ImagePreview 
        v-if="previewSrc" 
        :src="previewSrc" 
        @close="previewSrc = ''" 
      />
      
      <FilePreviewModal
        v-if="showFilePreview"
        :show="showFilePreview"
        :url="previewFile.url"
        :name="previewFile.name"
        @close="showFilePreview = false"
      />

      <div
        v-if="showMentionPopover"
        class="fixed inset-0 z-[9998]"
        @click="closeMentionPopover"
      />
      <div
        v-if="showMentionPopover && mentionPopoverUser"
        class="fixed z-[9999] bg-white border border-gray-200 rounded-lg shadow-xl p-4 w-[260px]"
        :style="{ left: mentionPopoverPos.x + 'px', top: mentionPopoverPos.y + 'px' }"
        @click.stop
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center text-sm font-bold text-gray-600">
            <img v-if="mentionPopoverUser.avatar" :src="fullAvatarUrl(mentionPopoverUser.avatar)" class="w-full h-full object-cover" />
            <span v-else>{{ (mentionPopoverUser.username || '?').charAt(0).toUpperCase() }}</span>
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-bold text-gray-900 truncate">{{ mentionPopoverUser.username }}</div>
            <div v-if="mentionPopoverUser.email" class="text-xs text-gray-500 truncate">{{ mentionPopoverUser.email }}</div>
          </div>
          <button class="p-1 rounded hover:bg-gray-100 text-gray-500" @click="closeMentionPopover">
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <TableMaximizeModal
        v-if="showTableMaximizeModal"
        :initial-content="maximizeContent"
        @close="showTableMaximizeModal = false"
        @save="handleTableUpdate"
      />
      
      <!-- Context Menu -->
      <div 
        v-if="showContextMenu" 
        class="fixed inset-0 z-[100]" 
        @click="closeContextMenu" 
        @contextmenu.prevent="closeContextMenu"
      >
        <div 
          class="absolute bg-white border rounded-lg shadow-lg py-1 w-48"
          :style="{ left: `${contextMenuPos.x}px`, top: `${contextMenuPos.y}px` }"
        >
          <button 
            @click.stop="insertBelow" 
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <ArrowDownToLine class="w-4 h-4" /> 下面插入文本
          </button>
          <button 
            @click.stop="deleteBlock" 
            class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 flex items-center gap-2"
          >
            <Trash2 class="w-4 h-4" /> 删除当前块内容
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent, BubbleMenu, VueNodeViewRenderer } from '@tiptap/vue-3'
import { InputRule } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import TaskList from '@tiptap/extension-task-list'
import CustomTaskItem from './CustomTaskItem'
import { Table, TableRow, TableHeader, CustomTableCell } from './TableExtensions'
import TableNodeComponent from './TableNode.vue'
import ResizableImage from './ResizableImage'
import Link from '@tiptap/extension-link'
import TextAlign from '@tiptap/extension-text-align'
import { watch, onBeforeUnmount, inject, ref } from 'vue'
import SlashCommand from './SlashCommand'
import { getSuggestion } from './suggestion'
import MentionExtension from './MentionExtension'
import { getMentionSuggestion } from './MentionSuggestion'
import WebsiteCard from './WebsiteCard'
import EChartsExtension from './EChartsExtension'
import VideoExtension from './VideoExtension'
import AudioExtension from './AudioExtension'
import Highlight from '@tiptap/extension-highlight'
import MathExtension from './MathExtension'
import CalloutExtension from './CalloutExtension'
import CalendarExtension from './CalendarExtension'
import MermaidExtension from './MermaidExtension'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import MusicPlayerExtension from './MusicPlayerExtension'
import ColumnsExtension, { Column } from './ColumnsExtension'
import { common, createLowlight } from 'lowlight'
import css from 'highlight.js/lib/languages/css'
import js from 'highlight.js/lib/languages/javascript'
import ts from 'highlight.js/lib/languages/typescript'
import html from 'highlight.js/lib/languages/xml'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import c from 'highlight.js/lib/languages/c'
import cpp from 'highlight.js/lib/languages/cpp'
import csharp from 'highlight.js/lib/languages/csharp'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import php from 'highlight.js/lib/languages/php'
import sql from 'highlight.js/lib/languages/sql'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import yaml from 'highlight.js/lib/languages/yaml'

import { marked } from 'marked'

let updateTimer: ReturnType<typeof setTimeout> | null = null

const lowlight = createLowlight(common)
lowlight.register('css', css)
lowlight.register('javascript', js)
lowlight.register('typescript', ts)
lowlight.register('html', html)
lowlight.register('python', python)
lowlight.register('java', java)
lowlight.register('c', c)
lowlight.register('cpp', cpp)
lowlight.register('csharp', csharp)
lowlight.register('go', go)
lowlight.register('rust', rust)
lowlight.register('php', php)
lowlight.register('sql', sql)
lowlight.register('bash', bash)
lowlight.register('json', json)
lowlight.register('markdown', markdown)
lowlight.register('yaml', yaml)

import CodeBlockComponent from './CodeBlockComponent.vue'
import { uploadFile } from '../../utils/upload'
import { DOMSerializer } from '@tiptap/pm/model'
import ImagePreview from '../ImagePreview.vue'
import FilePreviewModal from '../ui/FilePreviewModal.vue'
import TableMaximizeModal from '../modals/TableMaximizeModal.vue'
import DragHandle from '../ui/DragHandle.vue'
import { Maximize2, ArrowLeftToLine, ArrowRightToLine, Trash2, ArrowUpToLine, ArrowDownToLine, Merge, Split, PaintBucket, AlignLeft, AlignCenter, AlignRight, X } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string
  editable?: boolean
  disableTableResize?: boolean
  nodeId?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
}>()

const openDrawingModal = inject('openDrawingModal') as (callback: (dataUrl: string) => void) => void
const openMediaModal = inject('openMediaModal') as (type: 'image' | 'video' | 'audio' | 'file', callback: (url: string, name?: string) => void) => void
const openLinkModal = inject('openLinkModal') as (callback: (data: { url: string, text: string }) => void) => void
const openWebsiteCardModal = inject('openWebsiteCardModal') as (callback: (data: string | any) => void) => void
const openEChartsModal = inject('openEChartsModal') as (callback: (option: any) => void, initialData?: any, type?: string) => void
const openNodeLinkModal = inject('openNodeLinkModal') as ((sourceNodeId: string) => void) | undefined
const getMentionUsers = inject('getMentionUsers', () => [] as any[])

const previewSrc = ref('')
const previewFile = ref<{ url: string, name: string }>({ url: '', name: '' })
const showFilePreview = ref(false)
const showTableMaximizeModal = ref(false)
const showColorPicker = ref(false)
const editingTablePos = ref<number | null>(null)
const maximizeContent = ref<any>(null)

const shouldShowTableMenu = ({ editor }: { editor: any }) => {
  return editor.isActive('table')
}

const tableColors = [
  { color: null, label: '无颜色' },
  { color: '#f8f9fa', label: '灰色' },
  { color: '#ffe3e3', label: '红色' },
  { color: '#e7f5ff', label: '蓝色' },
  { color: '#e6fcf5', label: '绿色' },
  { color: '#fff9db', label: '黄色' },
  { color: '#f3d9fa', label: '紫色' },
]

const openTableMaximizeModal = () => {
  if (!editor.value) return
  
  const { state } = editor.value
  const { selection } = state
  const { $from } = selection
  
  // Find the table node
  for (let d = $from.depth; d > 0; d--) {
    const node = $from.node(d)
    if (node.type.name === 'table') {
      const pos = $from.before(d)
      editingTablePos.value = pos
      // Create a document JSON with just this table
      maximizeContent.value = {
        type: 'doc',
        content: [node.toJSON()]
      }
      showTableMaximizeModal.value = true
      return
    }
  }
}

const handleTableUpdate = (content: any) => {
  if (editor.value && editingTablePos.value !== null) {
    const tableNodeJSON = content.content?.[0]
    
    if (tableNodeJSON && tableNodeJSON.type === 'table') {
      const { state, view } = editor.value
      const tr = state.tr
      const oldNode = state.doc.nodeAt(editingTablePos.value)
      
      if (oldNode && oldNode.type.name === 'table') {
        const newNode = state.schema.nodeFromJSON(tableNodeJSON)
        tr.replaceWith(editingTablePos.value, editingTablePos.value + oldNode.nodeSize, newNode)
        view.dispatch(tr)
        emit('update:modelValue', editor.value.getHTML())
      }
    }
  }
}

const setCellColor = (color: string | null) => {
  if (editor.value) {
    editor.value.chain().focus().setCellAttribute('backgroundColor', color).run()
  }
  showColorPicker.value = false
}

const handleEditorClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement

  const mentionEl = target.closest('[data-type="mention"]') as HTMLElement | null
  if (mentionEl) {
    e.preventDefault()
    e.stopPropagation()
    const id = mentionEl.getAttribute('data-mention-id') || ''
    const name = mentionEl.getAttribute('data-mention-name') || ''
    openMentionPopover(mentionEl, id, name)
    return
  }
  
  // Handle Image Preview
  if (target.tagName === 'IMG') {
    if (!props.editable || (props.editable && e.altKey)) {
       previewSrc.value = (target as HTMLImageElement).src
       e.preventDefault()
       return
    }
  }
  
  // Handle Links (Attachments are also links)
  const link = (target as HTMLElement).closest('a')
  if (link) {
    const href = link.getAttribute('href')
    if (href) {
      const parts = href.split('?')[0].split('.')
      if (parts.length > 1) {
        const ext = parts.pop()?.toLowerCase()
        if (ext && ['pdf', 'xlsx', 'xls', 'docx', 'ppt', 'pptx'].includes(ext)) {
          e.preventDefault()
          e.stopPropagation()
          previewFile.value = { url: href, name: (link as HTMLElement).innerText || '' }
          showFilePreview.value = true
          return
        }
      }
    }

     if (!props.editable || (props.editable && e.altKey)) {
        window.open(link.href, '_blank')
        e.preventDefault()
        return
     }
  }
}

const showMentionPopover = ref(false)
const mentionPopoverPos = ref({ x: 0, y: 0 })
const mentionPopoverUser = ref<any>(null)

const fullAvatarUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
}

const openMentionPopover = (el: HTMLElement, id: string, name: string) => {
  const rect = el.getBoundingClientRect()
  mentionPopoverPos.value = { x: rect.left + rect.width + 8, y: rect.top - 6 }
  const users = getMentionUsers()
  const found = users.find((u: any) => u.id === id || u.username === name)
  mentionPopoverUser.value = found || { id, username: name }
  showMentionPopover.value = true
}

const closeMentionPopover = () => {
  showMentionPopover.value = false
  mentionPopoverUser.value = null
}

const context = {
  openDrawing: () => {
    openDrawingModal((dataUrl) => {
      if (editor.value) {
        editor.value.chain().focus().setImage({ src: dataUrl }).run()
      }
    })
  },
  openImage: () => {
    openMediaModal('image', (url) => {
      if (editor.value) {
        editor.value.chain().focus().setImage({ src: url }).run()
      }
    })
  },
  openVideo: () => {
    openMediaModal('video', (url) => {
      if (editor.value) {
        editor.value.chain().focus().setVideo({ src: url }).run()
      }
    })
  },
  openAudio: () => {
    openMediaModal('audio', (url) => {
      if (editor.value) {
        editor.value.chain().focus().setAudio({ src: url }).run()
      }
    })
  },
  openFile: () => {
    openMediaModal('file', (url, name) => {
      if (editor.value) {
        const text = name || '附件'
        editor.value.chain().focus()
          .insertContent({
            type: 'text',
            text: text,
            marks: [{ type: 'link', attrs: { href: url, target: '_blank' } }]
          })
          .run()
      }
    })
  },
  openLink: () => {
    openLinkModal((data) => {
      if (editor.value) {
        if (data.text) {
          editor.value.chain().focus()
            .insertContent({
              type: 'text',
              text: data.text,
              marks: [{ type: 'link', attrs: { href: data.url } }]
            })
            .run()
        } else {
          editor.value.chain().focus().setLink({ href: data.url }).run()
        }
      }
    })
  },
  openWebsiteCard: () => {
    openWebsiteCardModal((data) => {
      if (editor.value) {
        const attrs = typeof data === 'string' ? { url: data } : data
        editor.value.chain().focus().insertContent({
          type: 'websiteCard',
          attrs
        }).run()
      }
    })
  },
  openECharts: (initialData?: any, type?: string) => {
    openEChartsModal((data) => {
      if (editor.value) {
        editor.value.chain().focus().setECharts(data).run()
      }
    }, initialData, type)
  },
  linkNodes: () => {
    if (!props.nodeId) return
    if (!openNodeLinkModal) return
    openNodeLinkModal(props.nodeId)
  },
}

const markDirty = inject('markDirty', () => {})

const editor = useEditor({
  content: props.modelValue,
  editable: props.editable ?? true,
  extensions: [
    StarterKit.configure({
      codeBlock: false,
      bulletList: {
        keepMarks: true,
        keepAttributes: false,
      },
      orderedList: {
        keepMarks: true,
        keepAttributes: false,
      },
    }),
    CodeBlockLowlight.configure({
      lowlight,
    }).extend({
      addNodeView() {
        return VueNodeViewRenderer(CodeBlockComponent)
      },
      addKeyboardShortcuts() {
        return {
          Tab: ({ editor }) => {
            if (editor.isActive('codeBlock')) {
              return editor.commands.insertContent('  ')
            }
            return false
          },
        }
      },
    }),
    Placeholder.configure({
      placeholder: ({ node }) => {
        if (node.type.name === 'heading') {
          return '标题 ' + node.attrs.level
        }
        return "输入 '/' 唤起命令..."
      },
    }),
    TaskList,
    CustomTaskItem.configure({
      nested: true,
    }),
    Table.configure({
      resizable: !props.disableTableResize,
    }).extend({
      addNodeView() {
        return VueNodeViewRenderer(TableNodeComponent)
      }
    }),
    TableRow,
    TableHeader,
    CustomTableCell,
    ColumnsExtension,
    Column,
    TextAlign.configure({
      types: ['heading', 'paragraph', 'tableCell', 'tableHeader'],
    }),
    ResizableImage.configure({
      inline: true,
      allowBase64: true,
    }),
    Link.configure({
      openOnClick: false,
      autolink: true,
      HTMLAttributes: {
        target: '_blank',
        rel: 'noopener noreferrer nofollow',
      },
    }).extend({
      addInputRules() {
        return [
          new InputRule({
            find: /\[([^\]]+)\]\(([^)]+)\)$/,
            handler: ({ state, range, match }) => {
              const { tr } = state
              const [_, text, url] = match
              
              if (text && url) {
                tr.replaceWith(range.from, range.to, state.schema.text(text))
                const linkMark = state.schema.marks.link.create({ href: url })
                tr.addMark(range.from, range.from + text.length, linkMark)
              }
            },
          })
        ]
      }
    }),
    SlashCommand.configure({
      suggestion: getSuggestion(context),
    }),
    MentionExtension.configure({
      suggestion: {
        command: ({ editor, range, props }: any) => {
          editor
            .chain()
            .focus()
            .deleteRange(range)
            .insertContent({
              type: 'mention',
              attrs: { id: props.id, label: props.username },
            })
            .insertContent(' ')
            .run()
        },
        ...getMentionSuggestion(getMentionUsers),
      },
    }),
    WebsiteCard,
    EChartsExtension,
    VideoExtension,
    AudioExtension,
    Highlight.configure({ multicolor: true }),
    MathExtension,
    CalloutExtension,
    CalendarExtension,
    MermaidExtension,
    MusicPlayerExtension,
  ],
  onUpdate: ({ editor }) => {
    // Debounce the update emit to avoid frequent re-renders in parent
    if (updateTimer) clearTimeout(updateTimer)
    updateTimer = setTimeout(() => {
      const html = editor.getHTML()
      if (html !== props.modelValue) {
        emit('update:modelValue', html)
        markDirty()
      }
    }, 300)
  },
  onBlur: () => {
    // Ensure final state is saved on blur
    if (updateTimer) clearTimeout(updateTimer)
    if (editor.value) {
      emit('update:modelValue', editor.value.getHTML())
    }
    markDirty()
    emit('blur')
  },
  editorProps: {
    attributes: {
      class: 'focus:outline-none min-h-[100px]',
    },
    handleDOMEvents: {
      dragstart: (view, event) => {
        const e = event as DragEvent
        if (!e.dataTransfer) return false
        const sel = view.state.selection
        if (sel.empty) return false
        const slice = sel.content()
        const serializer = DOMSerializer.fromSchema(view.state.schema)
        const div = document.createElement('div')
        div.appendChild(serializer.serializeFragment(slice.content))
        const html = div.innerHTML
        if (!html) return false
        e.dataTransfer.setData('application/x-icanvas-html', html)
        e.dataTransfer.setData('text/html', html)
        e.dataTransfer.effectAllowed = 'copy'
        return false
      },
    },
    handlePaste: (view, event) => {
      const isInCodeBlock = (() => {
        try {
          const { $from } = view.state.selection
          for (let d = $from.depth; d > 0; d--) {
            if ($from.node(d).type.name === 'codeBlock') return true
          }
          return false
        } catch {
          return false
        }
      })()

      if (isInCodeBlock) {
        const plainText = event.clipboardData?.getData('text/plain')
        if (plainText != null) {
          event.preventDefault()
          view.dispatch(view.state.tr.insertText(plainText))
          return true
        }
      }

      const item = event.clipboardData?.items[0]
      if (item) {
        if (item.type === 'text/plain') {
           const plainText = event.clipboardData?.getData('text/plain')
           if (plainText) {
              // Heuristic check
              const looksLikeMarkdown = /^(#|\-|\*|>|`|\[|1\.)/m.test(plainText) || /(\*\*|__)/.test(plainText)
              
              if (looksLikeMarkdown) {
                 try {
                   // Synchronous parsing
                   const html = marked.parse(plainText, { async: false }) as string
                   
                   if (html) {
                      if (editor.value) {
                         editor.value.commands.insertContent(html)
                         return true
                      }
                   }
                 } catch (e) {
                   console.error('Markdown parse error', e)
                 }
              }
           }
        }
        
        const file = item.getAsFile()
        if (file) {
          if (item.type.startsWith('image/')) {
            event.preventDefault()
            uploadFile(file).then(url => {
               view.dispatch(view.state.tr.replaceSelectionWith(
                 view.state.schema.nodes.image.create({ src: url })
               ))
            }).catch(console.error)
            return true
          } else if (item.type.startsWith('video/')) {
             event.preventDefault()
             uploadFile(file).then(url => {
               view.dispatch(view.state.tr.replaceSelectionWith(
                 view.state.schema.nodes.video.create({ src: url })
               ))
            }).catch(console.error)
            return true
          } else if (item.type.startsWith('audio/')) {
             event.preventDefault()
             uploadFile(file).then(url => {
               view.dispatch(view.state.tr.replaceSelectionWith(
                 view.state.schema.nodes.audio.create({ src: url })
               ))
            }).catch(console.error)
            return true
          }
        }
      }
      return false
    },
    handleDrop: (view, event) => {
      const file = event.dataTransfer?.files?.[0]
      if (file) {
        const { schema } = view.state
        const coordinates = view.posAtCoords({ left: event.clientX, top: event.clientY })
        if (!coordinates) return false

        if (file.type.startsWith('image/')) {
          event.preventDefault()
          uploadFile(file).then(url => {
            view.dispatch(view.state.tr.insert(coordinates.pos, schema.nodes.image.create({ src: url })))
          }).catch(console.error)
          return true
        } else if (file.type.startsWith('video/')) {
          event.preventDefault()
          uploadFile(file).then(url => {
            view.dispatch(view.state.tr.insert(coordinates.pos, schema.nodes.video.create({ src: url })))
          }).catch(console.error)
          return true
        } else if (file.type.startsWith('audio/')) {
          event.preventDefault()
          uploadFile(file).then(url => {
            view.dispatch(view.state.tr.insert(coordinates.pos, schema.nodes.audio.create({ src: url })))
          }).catch(console.error)
          return true
        }
      }
      const html = event.dataTransfer?.getData('application/x-icanvas-html') || event.dataTransfer?.getData('text/html')
      if (html) {
        const coordinates = view.posAtCoords({ left: event.clientX, top: event.clientY })
        if (!coordinates) return false
        event.preventDefault()
        editor.value?.chain().focus().insertContentAt(coordinates.pos, html).run()
        return true
      }
      return false
    }
  },
})

const showContextMenu = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })

const handleContextMenu = (e: MouseEvent) => {
  if (!props.editable) return
  
  e.preventDefault()
  e.stopPropagation()

  if (editor.value) {
    const pos = editor.value.view.posAtCoords({ left: e.clientX, top: e.clientY })
    if (pos) {
      editor.value.commands.setTextSelection(pos.pos)
    }
  }

  contextMenuPos.value = { x: e.clientX, y: e.clientY }
  showContextMenu.value = true
}

const closeContextMenu = () => {
  showContextMenu.value = false
}

const insertBelow = () => {
  if (editor.value) {
    const { $to } = editor.value.state.selection
    // Check if we are at the root level (depth 0), where after() is not available
    if ($to.depth === 0) {
      editor.value.chain().focus().insertContentAt($to.pos, { type: 'paragraph' }).run()
    } else {
      const endPos = $to.after()
      editor.value.chain().focus().insertContentAt(endPos, { type: 'paragraph' }).run()
    }
  }
  closeContextMenu()
}

const deleteBlock = () => {
  if (editor.value) {
    const { $from } = editor.value.state.selection
    const parentName = $from.parent.type.name
    if (parentName !== 'doc') {
       editor.value.chain().focus().deleteNode(parentName).run()
    }
  }
  closeContextMenu()
}

watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue)
  }
})

watch(() => props.editable, (newValue) => {
  editor.value?.setEditable(newValue ?? true)
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

defineExpose({
  focus: () => {
    if (editor.value) {
      editor.value.commands.focus('end')
    }
  }
})
</script>

<style>
/* Tiptap specific styles */
.ProseMirror p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.ProseMirror:focus {
    outline: none;
}

/* Media Interaction Rules */
/* When editable (ProseMirror has contenteditable="true"), disable pointer events on media to allow selection */
.ProseMirror[contenteditable="true"] video,
.ProseMirror[contenteditable="true"] audio {
    pointer-events: none;
}

/* When NOT editable (ProseMirror has contenteditable="false"), show zoom cursor on images */
.ProseMirror[contenteditable="false"] img {
    cursor: zoom-in;
}

/* Media Selection Styles */
.ProseMirror-selectednode {
  outline: 2px solid #3b82f6; /* blue-500 */
  outline-offset: 2px;
  border-radius: 4px;
}

/* Table Styles */
.ProseMirror table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
  margin: 0;
  overflow: hidden;
}
.ProseMirror td,
.ProseMirror th {
  min-width: 1em;
  border: 2px solid #ced4da;
  padding: 3px 5px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
}
.ProseMirror th {
  font-weight: bold;
  text-align: left;
  background-color: #f1f3f5;
}
.ProseMirror .selectedCell:after {
  z-index: 2;
  position: absolute;
  content: "";
  left: 0; right: 0; top: 0; bottom: 0;
  background: rgba(200, 200, 255, 0.4);
  pointer-events: none;
}
.ProseMirror .column-resize-handle {
  position: absolute;
  right: -2px;
  top: 0;
  bottom: -2px;
  width: 4px;
  background-color: #adf;
  z-index: 20;
}

/* Task List Styles */
ul[data-type="taskList"] {
  list-style: none;
  padding: 0;
}
ul[data-type="taskList"] > li {
  display: flex;
  align-items: flex-start;
}
ul[data-type="taskList"] > li > label {
  flex: 0 0 auto;
  margin-right: 0.5rem;
  user-select: none;
  /* Align with the first line of text */
  margin-top: 0.35em;
}
ul[data-type="taskList"] > li > div {
  flex: 1 1 auto;
}
ul[data-type="taskList"] > li > div > p {
    margin-top: 0;
    margin-bottom: 0;
}
</style>
