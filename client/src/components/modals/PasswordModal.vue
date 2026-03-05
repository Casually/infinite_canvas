<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-sm flex flex-col overflow-hidden p-6">
      <h3 class="font-bold text-lg mb-4 text-gray-800">请输入访问密码</h3>
      
      <input 
        v-model="password"
        type="password"
        class="w-full border rounded px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
        placeholder="密码"
        @keyup.enter="confirm"
        ref="inputRef"
      />
      
      <div class="flex justify-end gap-2">
        <button 
          @click="$emit('close')"
          class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
        >
          取消
        </button>
        <button 
          @click="confirm"
          class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded transition-colors"
          :disabled="!password"
        >
          确认
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits(['close', 'confirm'])
const password = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  setTimeout(() => {
    inputRef.value?.focus()
  }, 50)
})

const confirm = () => {
  if (password.value) {
    emit('confirm', password.value)
  }
}
</script>