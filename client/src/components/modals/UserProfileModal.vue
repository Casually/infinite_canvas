<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[400px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">个人信息</h2>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-6">
        <!-- Avatar -->
        <div class="flex flex-col items-center mb-6">
          <div class="relative group cursor-pointer" @click="triggerFileInput">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-gray-200 bg-gray-100 flex items-center justify-center">
              <img v-if="avatarUrl" :src="fullAvatarUrl" class="w-full h-full object-cover" />
              <span v-else class="text-3xl text-gray-400">{{ (localNickname || email || '?')[0].toUpperCase() }}</span>
            </div>
            <div class="absolute inset-0 bg-black bg-opacity-30 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
          <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileChange" />
          <p class="text-xs text-gray-500 mt-2">点击更换头像</p>
        </div>

        <!-- Nickname -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">昵称</label>
          <input 
            v-model="localNickname" 
            type="text" 
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="设置一个昵称"
          />
        </div>

        <!-- Email (Read-only) -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <div class="w-full px-3 py-2 bg-gray-50 border rounded-md text-gray-500">
            {{ email }}
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button @click="$emit('close')" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">取消</button>
          <button @click="saveProfile" class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700" :disabled="loading">
            {{ loading ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  user: any
}>()

const emit = defineEmits(['close', 'update'])

const fileInput = ref<HTMLInputElement | null>(null)
const localNickname = ref(props.user.nickname || '')
const email = ref(props.user.email || '')
const avatarUrl = ref(props.user.avatar || '')
const loading = ref(false)

const fullAvatarUrl = computed(() => {
  if (!avatarUrl.value) return ''
  if (avatarUrl.value.startsWith('http')) return avatarUrl.value
  return `${import.meta.env.VITE_API_BASE_URL}${avatarUrl.value}`
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    await uploadAvatar(file)
  }
}

const uploadAvatar = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/user/avatar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (res.ok) {
      const data = await res.json()
      avatarUrl.value = data.avatar
    }
  } catch (e) {
    console.error('Upload failed', e)
  }
}

const saveProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/user/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        nickname: localNickname.value
      })
    })
    
    if (res.ok) {
      const data = await res.json()
      emit('update', { ...props.user, nickname: data.nickname, avatar: data.avatar })
      emit('close')
    }
  } catch (e) {
    console.error('Save failed', e)
  } finally {
    loading.value = false
  }
}
</script>
