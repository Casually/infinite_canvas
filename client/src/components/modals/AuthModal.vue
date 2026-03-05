<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-96 overflow-hidden">
      <div class="flex border-b px-6 py-4">
        <h2 class="text-lg font-bold text-gray-800">{{ isResetMode ? '找回密码' : '登录 / 注册' }}</h2>
      </div>
      
      <div class="p-6">
        <!-- Reset Password Form -->
        <form v-if="isResetMode" @submit.prevent="handleResetSubmit">
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">邮箱</label>
            <input 
              v-model="form.email" 
              type="email" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入注册邮箱"
            />
          </div>

          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">验证码</label>
            <div class="flex gap-2">
              <input 
                v-model="form.code" 
                type="text" 
                required
                class="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入验证码"
              />
              <button 
                type="button"
                class="px-3 py-2 bg-gray-100 text-gray-600 text-xs rounded-md hover:bg-gray-200 disabled:opacity-50"
                :disabled="countdown > 0 || !form.email"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
              </button>
            </div>
          </div>

          <div class="mb-6">
            <label class="block text-xs font-medium text-gray-700 mb-1">新密码</label>
            <input 
              v-model="form.password" 
              type="password" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入新密码"
            />
          </div>

          <div v-if="error" class="mb-4 text-xs text-red-600">
            {{ error }}
          </div>

          <button 
            type="submit" 
            class="w-full py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 mb-3"
            :disabled="loading"
          >
            {{ loading ? '处理中...' : '重置密码' }}
          </button>

          <div class="text-center">
            <button 
              type="button" 
              @click="toggleMode" 
              class="text-xs text-gray-500 hover:text-gray-700"
            >
              返回登录
            </button>
          </div>
        </form>

        <!-- Login/Register Form -->
        <form v-else @submit.prevent="handleSubmit">
          <div class="mb-4">
            <label class="block text-xs font-medium text-gray-700 mb-1">邮箱</label>
            <input 
              v-model="form.email" 
              type="email" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入邮箱"
            />
          </div>
          
          <div class="mb-4">
            <div class="flex justify-between items-center mb-1">
              <label class="block text-xs font-medium text-gray-700">密码</label>
              <button 
                type="button" 
                @click="toggleMode" 
                class="text-xs text-blue-600 hover:text-blue-800"
                tabindex="-1"
              >
                忘记密码?
              </button>
            </div>
            <input 
              v-model="form.password" 
              type="password" 
              required
              class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入密码"
            />
          </div>
          
          <div class="mb-6">
            <label class="block text-xs font-medium text-gray-700 mb-1">
              验证码 
              <span class="text-gray-400 font-normal">(新用户注册需要)</span>
            </label>
            <div class="flex gap-2">
              <input 
                v-model="form.code" 
                type="text" 
                class="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="验证码"
              />
              <button 
                type="button"
                class="px-3 py-2 bg-gray-100 text-gray-600 text-xs rounded-md hover:bg-gray-200 disabled:opacity-50"
                :disabled="countdown > 0 || !form.email"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
              </button>
            </div>
          </div>
          
          <div v-if="error" class="mb-4 text-xs text-red-600">
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="w-full py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            :disabled="loading"
          >
            {{ loading ? '处理中...' : '登录 / 注册' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useToast } from '../../composables/useToast'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'login-success'])
const { addToast } = useToast()

const loading = ref(false)
const error = ref('')
const countdown = ref(0)
const isResetMode = ref(false)

const form = reactive({
  email: '',
  password: '',
  code: ''
})

const toggleMode = () => {
  isResetMode.value = !isResetMode.value
  error.value = ''
  form.password = ''
  form.code = ''
}

const handleResetSubmit = async () => {
  if (!form.email || !form.code || !form.password) {
    error.value = '请填写完整信息'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: form.email,
        code: form.code,
        new_password: form.password
      })
    })
    
    const data = await res.json()
    
    if (!res.ok) throw new Error(data.message)
    
    addToast('密码重置成功，请登录', 'success')
    isResetMode.value = false
    form.password = ''
    form.code = ''
    
  } catch (e: any) {
    error.value = e.message
    addToast(e.message, 'error')
  } finally {
    loading.value = false
  }
}

const sendCode = async () => {
  if (!form.email) return
  
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/send-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: form.email })
    })
    
    const data = await res.json()
    
    if (!res.ok) throw new Error(data.message)
    
    // Start countdown
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
    
    addToast(`验证码已发送: ${data.code}`, 'success')
    
  } catch (e: any) {
    error.value = e.message
    addToast(e.message, 'error')
  }
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/authenticate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: form.email,
        password: form.password,
        code: form.code
      })
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      if (data.require_code) {
        addToast(data.message, 'info')
        error.value = data.message
        return
      }
      throw new Error(data.message)
    }
    
    emit('login-success', data)
    emit('close')
    
    const actionText = data.action === 'register' ? '注册并登录成功' : '登录成功'
    addToast(actionText, 'success')
    
  } catch (e: any) {
    error.value = e.message
    addToast(e.message, 'error')
  } finally {
    loading.value = false
  }
}
</script>
