<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[500px] max-h-[80vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">快捷键设置</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="space-y-4">
          <div 
            v-for="shortcut in shortcuts" 
            :key="shortcut.id"
            class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            :class="{ 'ring-2 ring-blue-500 bg-blue-50': recordingId === shortcut.id }"
          >
            <span class="text-gray-700 font-medium">{{ shortcut.label }}</span>
            
            <button 
              @click="startRecording(shortcut.id)"
              class="flex items-center gap-2 px-3 py-1.5 rounded border text-sm min-w-[120px] justify-center transition-all"
              :class="recordingId === shortcut.id ? 'bg-white text-blue-600 border-blue-200' : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'"
            >
              <template v-if="recordingId === shortcut.id">
                <span class="animate-pulse">请输入...</span>
              </template>
              <template v-else>
                <div class="flex gap-1">
                  <span v-if="shortcut.isCtrlOrMeta" class="font-mono">Ctrl/Cmd</span>
                  <span v-for="(k, i) in shortcut.keys" :key="i" class="font-mono">
                    <span v-if="i > 0 || shortcut.isCtrlOrMeta">+</span>
                    {{ k.toUpperCase() }}
                  </span>
                </div>
              </template>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t bg-gray-50 flex justify-between items-center">
        <button 
          @click="handleReset"
          class="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          恢复默认
        </button>
        <button 
          @click="$emit('close')"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
        >
          完成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'
import { useShortcuts } from '../../composables/useShortcuts'

const emit = defineEmits(['close'])
const { shortcuts, updateShortcut, resetShortcuts } = useShortcuts()

const recordingId = ref<string | null>(null)

const startRecording = (id: string) => {
  if (recordingId.value === id) {
    recordingId.value = null // Cancel if clicking again
    return
  }
  recordingId.value = id
}

const handleKeyDown = (e: KeyboardEvent) => {
  if (!recordingId.value) return

  e.preventDefault()
  e.stopPropagation()

  // Ignore modifier-only keydowns
  if (['Control', 'Meta', 'Shift', 'Alt'].includes(e.key)) return

  const keys: string[] = []
  let isCtrlOrMeta = false

  // Detect modifiers
  if (e.ctrlKey || e.metaKey) {
    isCtrlOrMeta = true
  }
  
  if (e.altKey) {
    keys.push('Alt')
  }
  
  if (e.shiftKey) {
    keys.push('Shift')
  }

  // Main key
  keys.push(e.key)

  // Update the shortcut
  updateShortcut(recordingId.value, keys, isCtrlOrMeta)
  
  // Stop recording
  recordingId.value = null
}

const handleReset = () => {
  if (confirm('确定要恢复默认快捷键吗？')) {
    resetShortcuts()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown, { capture: true })
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown, { capture: true })
})
</script>
