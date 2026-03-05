<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[600px] h-[600px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">我的分享管理</h2>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
        <div v-else-if="shares.length === 0" class="text-center py-8 text-gray-500">
          暂无分享记录
        </div>
        <div v-else class="space-y-4">
          <div 
            v-for="share in shares" 
            :key="share.id"
            class="border rounded-lg p-4 hover:shadow-sm transition-shadow bg-white"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-medium text-gray-900">{{ share.canvas_title }}</h3>
                <div class="text-sm text-gray-500 mt-1">
                  包含 {{ share.node_count }} 个节点
                  <span v-if="share.has_password" class="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">密码保护</span>
                  <span v-if="share.allow_edit" class="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">允许编辑</span>
                  <span v-else class="ml-2 px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full">仅浏览</span>
                </div>
                <div class="text-xs text-gray-400 mt-2">
                  创建于 {{ formatDate(share.created_at) }}
                </div>
              </div>
              <div class="flex flex-col gap-2">
                <button 
                  @click="copyLink(share.id)"
                  class="text-blue-600 hover:text-blue-800 text-sm"
                >
                  复制链接
                </button>
                <button 
                  @click="deleteShare(share.id)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  删除分享
                </button>
              </div>
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
import { ref, onMounted } from 'vue'
import { useToast } from '../../composables/useToast'
import ConfirmationModal from './ConfirmationModal.vue'

const emit = defineEmits(['close'])
const { addToast } = useToast()

const shares = ref<any[]>([])
const loading = ref(true)

// Confirmation Modal State
const showConfirmModal = ref(false)
const confirmMessage = ref('')
const itemToDeleteId = ref<string | null>(null)

async function loadShares() {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/my-shares`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await response.json()
    if (response.ok) {
      shares.value = data.shares
    } else {
      addToast('加载分享记录失败', 'error')
    }
  } catch (e) {
    console.error(e)
    addToast('网络错误', 'error')
  } finally {
    loading.value = false
  }
}

async function deleteShare(id: string) {
  itemToDeleteId.value = id
  confirmMessage.value = '确定要删除这个分享吗？链接将失效。'
  showConfirmModal.value = true
}

async function executeDelete() {
  if (!itemToDeleteId.value) return
  const id = itemToDeleteId.value
  showConfirmModal.value = false
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/shares/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      addToast('删除成功', 'success')
      shares.value = shares.value.filter(s => s.id !== id)
    } else {
      addToast('删除失败', 'error')
    }
  } catch (e) {
    console.error(e)
    addToast('网络错误', 'error')
  } finally {
    itemToDeleteId.value = null
  }
}

function copyLink(id: string) {
  const baseUrl = window.location.origin + window.location.pathname
  const link = `${baseUrl}?shareId=${id}`
  navigator.clipboard.writeText(link)
  addToast('链接已复制', 'success')
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  loadShares()
})
</script>
