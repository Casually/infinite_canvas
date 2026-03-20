<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-50" @click.self="onCancel">
    <div class="bg-white rounded-lg shadow-xl w-96 overflow-hidden transform transition-all">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">{{ title || '确认' }}</h3>
        <button @click="onCancel" class="text-gray-400 hover:text-gray-500">
          <span class="sr-only">Close</span>
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="px-6 py-4">
        <p class="text-sm text-gray-500">{{ message }}</p>
        <label v-if="checkboxLabel" class="mt-3 flex items-center gap-2 text-sm text-gray-700 select-none">
          <input v-model="checked" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
          <span>{{ checkboxLabel }}</span>
        </label>
      </div>
      
      <div class="bg-gray-50 px-6 py-3 flex flex-row-reverse gap-2">
        <button 
          @click="onConfirm" 
          class="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:text-sm"
        >
          {{ confirmText || '确认' }}
        </button>
        <button 
          @click="onCancel" 
          class="inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm"
        >
          {{ cancelText || '取消' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  checkboxLabel?: string
  checkboxDefaultChecked?: boolean
}>()

const emit = defineEmits(['confirm', 'cancel'])

const checked = ref(!!props.checkboxDefaultChecked)

const onConfirm = () => {
  emit('confirm', checked.value)
}

const onCancel = () => {
  emit('cancel')
}
</script>
