<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[400px] overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">插入链接</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      
      <div class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">链接文本 (可选)</label>
          <input 
            v-model="text" 
            type="text" 
            class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
            placeholder="显示的文字"
            @keydown.enter="confirm"
            v-focus
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">链接地址 (URL)</label>
          <input 
            v-model="url" 
            type="text" 
            class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
            placeholder="https://example.com"
            @keydown.enter="confirm"
          />
        </div>
      </div>

      <div class="p-4 border-t flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded text-sm font-medium">取消</button>
        <button 
          @click="confirm" 
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          :disabled="!isValid"
        >
          确认插入
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits(['close', 'save'])

const url = ref('')
const text = ref('')

const isValid = computed(() => {
  try {
    if (!url.value) return false
    return url.value.length > 0
  } catch {
    return false
  }
})

const confirm = () => {
  if (isValid.value) {
    emit('save', { url: url.value, text: text.value })
    emit('close')
  }
}

// Custom directive for auto-focus
const vFocus = {
  mounted: (el: HTMLElement) => el.focus()
}
</script>