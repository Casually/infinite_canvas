<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">画布管理</h2>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-4 border-b bg-gray-50 flex justify-between items-center">
        <div v-if="!isCreating" class="relative flex-1 mr-4">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索画布..." 
            class="w-full pl-8 pr-4 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 absolute left-2.5 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div v-else class="flex-1 mr-4 flex gap-2">
            <input 
            v-model="newCanvasTitle" 
            type="text" 
            placeholder="输入画布名称" 
            class="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="createCanvas"
            ref="newCanvasInput"
          />
          <button @click="createCanvas" class="px-3 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700">确定</button>
          <button @click="isCreating = false" class="px-3 py-2 bg-gray-200 text-gray-700 rounded-md text-sm hover:bg-gray-300">取消</button>
        </div>
        
        <button 
          v-if="!isCreating"
          @click="startCreating" 
          class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 flex items-center gap-1"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新建画布
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
        
        <div v-else-if="filteredCanvases.length === 0" class="text-center py-8 text-gray-500">
          {{ searchQuery ? '未找到相关画布' : '暂无画布，快去创建一个吧' }}
        </div>
        
        <div v-else class="grid gap-3">
          <div 
            v-for="canvas in filteredCanvases" 
            :key="canvas.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow flex justify-between items-center bg-white group cursor-pointer"
            @click="editingCanvasId !== canvas.id && $emit('select', canvas.id)"
            :class="{'ring-2 ring-blue-500': currentCanvasId === canvas.id && editingCanvasId !== canvas.id}"
          >
            <div class="flex-1 mr-4">
              <div v-if="editingCanvasId === canvas.id" class="flex items-center gap-2" @click.stop>
                <input 
                  v-model="editTitle" 
                  class="flex-1 px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @keyup.enter="saveEditing"
                  @keyup.esc="cancelEditing"
                  ref="editInput"
                  @blur="saveEditing"
                />
              </div>
              <div v-else class="font-medium text-gray-800 flex items-center gap-2">
                {{ canvas.title }}
                <span v-if="canvas.is_public" class="text-xs bg-green-100 text-green-600 px-1.5 py-0.5 rounded">公开</span>
                <span v-if="canvas.has_password" class="text-xs bg-yellow-100 text-yellow-600 px-1.5 py-0.5 rounded">加密</span>
              </div>
              <div class="text-xs text-gray-500 mt-1">
                更新时间: {{ formatDate(canvas.updated_at) }}
              </div>
            </div>
            
            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                v-if="editingCanvasId !== canvas.id"
                @click.stop="startEditing(canvas)"
                class="p-1.5 text-gray-500 hover:bg-gray-100 rounded"
                title="重命名"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <button 
                @click.stop="handleDuplicate(canvas)"
                class="p-1.5 text-blue-500 hover:bg-blue-50 rounded"
                title="复制"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              <button 
                @click.stop="handleDelete(canvas)"
                class="p-1.5 text-red-500 hover:bg-red-50 rounded"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ConfirmationModal
      v-if="showConfirmModal"
      title="删除确认"
      :message="confirmMessage"
      confirm-text="删除"
      cancel-text="取消"
      @confirm="executeDelete"
      @cancel="showConfirmModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from '../../composables/useToast'
import ConfirmationModal from './ConfirmationModal.vue'

const props = defineProps<{
  currentCanvasId?: string
}>()

const emit = defineEmits(['close', 'select'])
const { addToast } = useToast()

const canvases = ref<any[]>([])
const loading = ref(true)
const searchQuery = ref('')
const isCreating = ref(false)
const newCanvasTitle = ref('')
const newCanvasInput = ref<HTMLInputElement | null>(null)

// Editing State
const editingCanvasId = ref<string | null>(null)
const editTitle = ref('')
const editInput = ref<HTMLInputElement | null>(null)

// Confirmation Modal State
const showConfirmModal = ref(false)
const confirmMessage = ref('')
const itemToDelete = ref<any>(null)

const startCreating = () => {
  isCreating.value = true
  newCanvasTitle.value = ''
  // Focus next tick
  setTimeout(() => {
    newCanvasInput.value?.focus()
  }, 50)
}

const filteredCanvases = computed(() => {
  if (!searchQuery.value) return canvases.value
  const query = searchQuery.value.toLowerCase()
  return canvases.value.filter(c => c.title.toLowerCase().includes(query))
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const fetchCanvases = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (res.ok) {
      const data = await res.json()
      canvases.value = data.canvases
    }
  } catch (e) {
    console.error(e)
    addToast('获取画布列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const createCanvas = async () => {
  const title = newCanvasTitle.value.trim() || '新画布'
  
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({ title })
    })

    if (res.ok) {
      const data = await res.json()
      addToast('创建成功', 'success')
      isCreating.value = false
      emit('select', data.id)
      emit('close')
    } else {
      throw new Error('Create failed')
    }
  } catch (e) {
    addToast('创建失败', 'error')
  }
}

const startEditing = (canvas: any) => {
  editingCanvasId.value = canvas.id
  editTitle.value = canvas.title
  setTimeout(() => {
    editInput.value?.focus()
  }, 50)
}

const cancelEditing = () => {
  editingCanvasId.value = null
  editTitle.value = ''
}

const saveEditing = async () => {
  if (!editingCanvasId.value) return
  
  const title = editTitle.value.trim()
  const canvasId = editingCanvasId.value
  const originalCanvas = canvases.value.find(c => c.id === canvasId)
  
  // If no change or empty, just cancel
  if (!title || title === originalCanvas?.title) {
    cancelEditing()
    return
  }

  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${canvasId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({ title })
    })

    if (res.ok) {
      addToast('重命名成功', 'success')
      // Update local list
      const canvas = canvases.value.find(c => c.id === canvasId)
      if (canvas) canvas.title = title
      
      // If renaming current canvas, might want to reload or emit update, 
      // but InfiniteCanvas handles its own title state.
      // If we are renaming the CURRENTLY open canvas, we might want to refresh the page 
      // or at least let the parent know.
      if (props.currentCanvasId === canvasId) {
        window.location.reload()
      }
    } else {
      throw new Error('Update failed')
    }
  } catch (e) {
    addToast('重命名失败', 'error')
  } finally {
    cancelEditing()
  }
}

const handleDuplicate = async (canvas: any) => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${canvas.id}/duplicate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      addToast('复制成功', 'success')
      fetchCanvases()
    } else {
      throw new Error('Duplicate failed')
    }
  } catch (e) {
    addToast('复制失败', 'error')
  }
}

const handleDelete = (canvas: any) => {
  itemToDelete.value = canvas
  confirmMessage.value = `确定要删除画布 "${canvas.title}" 吗？此操作不可恢复。`
  showConfirmModal.value = true
}

const executeDelete = async () => {
  if (!itemToDelete.value) return
  const canvas = itemToDelete.value
  showConfirmModal.value = false
  
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${canvas.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (res.ok) {
      addToast('删除成功', 'success')
      canvases.value = canvases.value.filter(c => c.id !== canvas.id)
      if (props.currentCanvasId === canvas.id) {
        // If deleted current, reload or handle gracefully
        window.location.reload()
      }
    } else {
      throw new Error('Delete failed')
    }
  } catch (e) {
    addToast('删除失败', 'error')
  } finally {
    itemToDelete.value = null
  }
}

onMounted(() => {
  fetchCanvases()
})
</script>