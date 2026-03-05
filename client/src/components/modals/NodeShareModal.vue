<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[600px] h-[700px] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b shrink-0">
        <h2 class="text-lg font-bold text-gray-800">分享节点</h2>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Body -->
      <div class="flex-1 overflow-y-auto flex flex-col p-6">
        <div v-if="!shareResult">
          <!-- Search -->
          <div class="mb-4">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索节点..." 
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Node List -->
          <div class="border rounded-md flex-1 overflow-y-auto h-[300px] mb-4">
            <div v-if="filteredNodes.length === 0" class="p-4 text-center text-gray-500 text-sm">
              没有找到匹配的节点
            </div>
            <div 
              v-for="node in filteredNodes" 
              :key="node.id"
              class="flex items-center p-3 hover:bg-gray-50 border-b last:border-b-0 cursor-pointer"
              @click="toggleNode(node.id)"
            >
              <input 
                type="checkbox" 
                :checked="selectedNodeIds.has(node.id)"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mr-3"
                readonly
              />
              <div class="flex-1 truncate">
                <div class="text-sm font-medium text-gray-900">{{ getNodeLabel(node) }}</div>
                <div class="text-xs text-gray-500">ID: {{ node.id }} | Type: {{ node.type }}</div>
              </div>
            </div>
          </div>
          
          <!-- Selection Info -->
          <div class="flex justify-between items-center mb-6 text-sm">
            <span class="text-gray-600">已选择 {{ selectedNodeIds.size }} 个节点</span>
            <div class="space-x-2">
              <button @click="selectAll" class="text-blue-600 hover:text-blue-800">全选</button>
              <button @click="deselectAll" class="text-gray-600 hover:text-gray-800">清空</button>
            </div>
          </div>

          <!-- Settings -->
          <div class="border-t pt-4 space-y-4">
            <h3 class="font-medium text-gray-900">分享设置</h3>
            
            <!-- Guest Edit -->
            <div class="flex items-center justify-between">
              <div>
                <div class="text-sm text-gray-700">允许访客编辑</div>
                <div class="text-xs text-gray-500">无需登录即可修改节点内容</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="settings.allow_edit" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <!-- Password -->
            <div>
              <div class="text-sm text-gray-700 mb-1">访问密码 (可选)</div>
              <input 
                v-model="settings.password" 
                type="text" 
                placeholder="设置密码以保护内容" 
                class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <!-- Result View -->
        <div v-else class="flex-1 flex flex-col items-center justify-center space-y-6">
          <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">分享链接已生成!</h3>
          
          <div class="w-full p-4 bg-gray-50 rounded border flex items-center gap-2">
            <div class="flex-1 truncate text-sm text-gray-600">{{ shareResult.link }}</div>
            <button 
              @click="copyLink"
              class="text-blue-600 hover:text-blue-800 text-sm font-medium whitespace-nowrap"
            >
              {{ copied ? '已复制' : '复制链接' }}
            </button>
          </div>
          
          <div class="text-sm text-gray-500 text-center">
            包含 {{ selectedNodeIds.size }} 个节点<br>
            {{ settings.password ? '已设置密码保护' : '无密码' }} | {{ settings.allow_edit ? '允许编辑' : '仅阅读' }}
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 shrink-0">
        <template v-if="!shareResult">
          <button 
            @click="$emit('close')" 
            class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-100"
          >
            取消
          </button>
          <button 
            @click="createShare" 
            :disabled="selectedNodeIds.size === 0 || creating"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="creating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ creating ? '创建中...' : '生成分享链接' }}
          </button>
        </template>
        <template v-else>
          <button 
            @click="$emit('close')" 
            class="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900"
          >
            关闭
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useToast } from '../../composables/useToast'

const props = defineProps<{
  canvasId: string
  nodes: any[]
  preSelectedNodeIds?: string[]
}>()

const emit = defineEmits(['close'])
const { addToast } = useToast()

const searchQuery = ref('')
const selectedNodeIds = reactive(new Set<string>(props.preSelectedNodeIds || []))
const creating = ref(false)
const copied = ref(false)
const shareResult = ref<any>(null)

const settings = reactive({
  allow_edit: false,
  password: ''
})

const filteredNodes = computed(() => {
  if (!searchQuery.value) return props.nodes
  const query = searchQuery.value.toLowerCase()
  return props.nodes.filter(node => {
    const label = getNodeLabel(node).toLowerCase()
    return label.includes(query)
  })
})

function getNodeLabel(node: any): string {
  if (node.label) return node.label
  if (node.data?.label) return node.data.label
  if (node.data?.content) return node.data.content.substring(0, 20)
  return '未命名节点'
}

function toggleNode(id: string) {
  if (selectedNodeIds.has(id)) {
    selectedNodeIds.delete(id)
  } else {
    selectedNodeIds.add(id)
  }
}

function selectAll() {
  filteredNodes.value.forEach(node => selectedNodeIds.add(node.id))
}

function deselectAll() {
  selectedNodeIds.clear()
}

async function createShare() {
  if (selectedNodeIds.size === 0) return
  
  creating.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/shares`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        canvas_id: props.canvasId,
        node_ids: Array.from(selectedNodeIds),
        settings: settings
      })
    })
    
    const data = await response.json()
    if (response.ok) {
      const baseUrl = window.location.origin + window.location.pathname
      // Assuming route will be /?shareId=... or similar
      // Since backend returned /share/UUID, we might need to adjust frontend routing or parameter
      // Let's use ?shareId=UUID
      shareResult.value = {
        ...data,
        link: `${baseUrl}?shareId=${data.id}`
      }
      addToast('分享链接已生成', 'success')
    } else {
      addToast(data.message || '创建分享失败', 'error')
    }
  } catch (e) {
    addToast('网络错误', 'error')
    console.error(e)
  } finally {
    creating.value = false
  }
}

function copyLink() {
  if (!shareResult.value) return
  navigator.clipboard.writeText(shareResult.value.link)
  copied.value = true
  addToast('链接已复制到剪贴板', 'success')
  setTimeout(() => copied.value = false, 2000)
}
</script>
