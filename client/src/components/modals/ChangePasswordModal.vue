<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-96 overflow-hidden">
      <div class="flex border-b px-6 py-4 justify-between items-center">
        <h2 class="text-lg font-bold text-gray-800">修改密码</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-6">
        <form @submit.prevent="handleSubmit">
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">原密码</label>
            <input 
              v-model="form.oldPassword" 
              type="password" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入原密码"
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">新密码</label>
            <input 
              v-model="form.newPassword" 
              type="password" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入新密码"
            />
          </div>

          <div class="mb-6">
            <label class="block text-xs font-medium text-gray-700 mb-1">确认新密码</label>
            <input 
              v-model="form.confirmPassword" 
              type="password" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请再次输入新密码"
            />
          </div>
          
          <div v-if="error" class="mb-4 text-xs text-red-600">
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="w-full py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            :disabled="loading"
          >
            {{ loading ? '处理中...' : '确认修改' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useToast } from '../../composables/useToast'

const emit = defineEmits(['close'])
const { addToast } = useToast()

const loading = ref(false)
const error = ref('')

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const handleSubmit = async () => {
  error.value = ''
  
  if (form.newPassword !== form.confirmPassword) {
    error.value = '两次输入的新密码不一致'
    return
  }
  
  if (form.newPassword.length < 6) {
    error.value = '新密码长度至少需6位'
    return
  }

  loading.value = true
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      error.value = '请先登录'
      return
    }

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/change-password`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        old_password: form.oldPassword,
        new_password: form.newPassword
      })
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.message || '修改失败')
    }
    
    addToast('密码修改成功', 'success')
    emit('close')
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
