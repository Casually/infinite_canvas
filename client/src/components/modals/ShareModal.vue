<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[500px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">分享设置</h2>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-6">
        <div v-if="loading" class="text-center py-4">加载中...</div>
        <div v-else>
          <!-- Public Access Toggle -->
          <div class="flex items-center justify-between mb-6">
            <div>
              <div class="font-medium text-gray-800">开启链接分享</div>
              <div class="text-xs text-gray-500">开启后，获得链接的人可以访问此画布</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.is_public" class="sr-only peer" @change="updateSettings">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div v-if="settings.is_public" class="space-y-6">
            <!-- Share Link -->
            <div class="p-3 bg-gray-50 rounded border flex items-center gap-2">
              <div class="flex-1 truncate text-sm text-gray-600">{{ shareLink }}</div>
              <button 
                @click="copyLink"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium whitespace-nowrap"
              >
                {{ copied ? '已复制' : '复制链接' }}
              </button>
            </div>

            <!-- Guest Edit Permission -->
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-gray-800">允许访客编辑</div>
                <div class="text-xs text-gray-500">无需登录即可修改画布内容</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="settings.allow_guest_edit" class="sr-only peer" @change="updateSettings">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <!-- Password Protection -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <div>
                  <div class="font-medium text-gray-800">访问密码</div>
                  <div class="text-xs text-gray-500">设置后需要密码才能访问（留空表示不需要密码）</div>
                </div>
              </div>
              <div class="flex gap-2">
                <input 
                  v-model="passwordInput" 
                  type="text" 
                  placeholder="设置访问密码" 
                  class="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button 
                  @click="updatePassword"
                  class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200"
                >
                  保存密码
                </button>
              </div>
              <div v-if="settings.has_password" class="mt-1 text-xs text-green-600 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                当前已设置密码
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useToast } from '../../composables/useToast'

const props = defineProps<{
  canvasId: string
}>()

const emit = defineEmits(['close'])
const { addToast } = useToast()

const loading = ref(true)
const copied = ref(false)
const passwordInput = ref('')

const settings = reactive({
  is_public: false,
  allow_guest_edit: false,
  has_password: false
})

const shareLink = computed(() => {
  const baseUrl = window.location.origin + window.location.pathname
  return `${baseUrl}?canvasId=${props.canvasId}`
})

const copyLink = () => {
  navigator.clipboard.writeText(shareLink.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

const fetchSettings = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) return

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${props.canvasId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (res.ok) {
      const data = await res.json()
      settings.is_public = data.is_public
      settings.allow_guest_edit = data.allow_guest_edit
      settings.has_password = data.has_password
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const updateSettings = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${props.canvasId}/share`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({
        is_public: settings.is_public,
        allow_guest_edit: settings.allow_guest_edit
      })
    })

    if (res.ok) {
      addToast('设置已更新', 'success')
    } else {
      throw new Error('Update failed')
    }
  } catch (e) {
    addToast('设置更新失败', 'error')
    // Revert?
  }
}

const updatePassword = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${props.canvasId}/share`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({
        password: passwordInput.value
      })
    })

    if (res.ok) {
      addToast('密码已更新', 'success')
      settings.has_password = !!passwordInput.value
      passwordInput.value = ''
    } else {
      throw new Error('Update failed')
    }
  } catch (e) {
    addToast('密码更新失败', 'error')
  }
}

onMounted(() => {
  fetchSettings()
})
</script>