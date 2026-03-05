<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[500px] max-h-[80vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg flex items-center gap-2">
          <History class="w-5 h-5 text-gray-500" />
          历史记录
        </h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="loading" class="flex justify-center py-8 text-gray-500">
          加载中...
        </div>
        
        <div v-else-if="historyList.length === 0" class="text-center py-8 text-gray-500">
          暂无历史记录
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="item in historyList" 
            :key="item.id"
            class="border rounded-lg p-3 hover:bg-gray-50 transition-colors flex items-center justify-between group"
          >
            <div>
              <div class="text-sm font-medium text-gray-800">
                {{ formatTime(item.created_at) }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ item.user_nickname || '未知用户' }}
              </div>
            </div>
            
            <button 
              @click="restore(item)"
              :disabled="restoring"
              class="px-3 py-1.5 text-sm bg-white border hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 rounded text-gray-600 transition-colors flex items-center gap-1 opacity-0 group-hover:opacity-100 focus:opacity-100"
              :class="{ 'opacity-50 cursor-not-allowed': restoring }"
            >
              <RotateCcw class="w-3.5 h-3.5" />
              <span>恢复</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="p-3 bg-gray-50 border-t text-xs text-gray-500 text-center">
        仅显示最近 50 条记录
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X, History, RotateCcw } from 'lucide-vue-next'

const props = defineProps<{
  canvasId: string
}>()

const emit = defineEmits(['close', 'restore'])

const historyList = ref<any[]>([])
const loading = ref(true)
const restoring = ref(false)

const formatTime = (isoString: string) => {
  return new Date(isoString).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${props.canvasId}/history`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (res.ok) {
      const data = await res.json()
      historyList.value = data.history
    }
  } catch (e) {
    console.error('Failed to fetch history:', e)
  } finally {
    loading.value = false
  }
}

const restore = async (item: any) => {
  if (!confirm('确定要恢复到此版本吗？当前未保存的更改将会丢失。')) return
  
  restoring.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${props.canvasId}/history/${item.id}/restore`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (res.ok) {
      emit('restore')
      emit('close')
    } else {
        const data = await res.json()
        alert(data.message || '恢复失败')
    }
  } catch (e) {
    console.error('Failed to restore history:', e)
    alert('恢复失败')
  } finally {
    restoring.value = false
  }
}

onMounted(() => {
  fetchHistory()
})
</script>
