<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[500px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">插入图片</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <X class="w-6 h-6" />
        </button>
      </div>
      
      <div class="flex border-b">
        <button 
          class="flex-1 py-2 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'local' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'local'"
        >
          本地上传
        </button>
        <button 
          class="flex-1 py-2 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'url' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'url'"
        >
          网络图片
        </button>
      </div>

      <div class="p-6">
        <!-- Local Upload -->
        <div v-if="activeTab === 'local'" class="space-y-4">
          <div 
            class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:bg-gray-50 transition-colors cursor-pointer relative"
            @click="triggerFileInput"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileSelect" />
            <div v-if="previewUrl" class="relative group">
               <img :src="previewUrl" class="max-h-48 mx-auto rounded shadow-sm object-contain" />
               <div class="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded">
                 <span class="text-white text-sm font-medium">点击更换</span>
               </div>
            </div>
            <div v-else>
               <div class="text-gray-400 mb-2">
                 <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
               </div>
               <p class="text-gray-500 text-sm font-medium">点击选择或拖拽图片到此处</p>
               <p class="text-gray-400 text-xs mt-1">支持粘贴截图 (Ctrl+V)</p>
            </div>
          </div>
        </div>

        <!-- URL Input -->
        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">图片链接</label>
            <input 
              v-model="imageUrl" 
              type="text" 
              class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
              placeholder="https://example.com/image.png"
            />
          </div>
          <div v-if="imageUrl" class="border rounded p-2 bg-gray-50 flex justify-center min-h-[100px] items-center">
            <img :src="imageUrl" class="max-h-48 object-contain" @error="imageError = true" @load="imageError = false" v-show="!imageError" />
            <span v-if="imageError" class="text-red-500 text-sm">图片加载失败</span>
          </div>
        </div>
      </div>

      <div class="p-4 border-t flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded text-sm font-medium">取消</button>
        <button 
          @click="confirm" 
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          :disabled="!canConfirm"
        >
          插入图片
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'

const emit = defineEmits(['close', 'save'])

const activeTab = ref<'local' | 'url'>('local')
const imageUrl = ref('')
const previewUrl = ref('')
const imageError = ref(false)
const fileInput = ref<HTMLInputElement>()

const canConfirm = computed(() => {
  if (activeTab.value === 'local') return !!previewUrl.value
  return !!imageUrl.value && !imageError.value
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processFile(file)
}

const handleDrop = (e: DragEvent) => {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

const processFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const handlePaste = (e: ClipboardEvent) => {
  if (activeTab.value !== 'local') return
  const item = e.clipboardData?.items[0]
  if (item && item.type.startsWith('image/')) {
    const file = item.getAsFile()
    if (file) processFile(file)
  }
}

onMounted(() => {
  window.addEventListener('paste', handlePaste)
})

onUnmounted(() => {
  window.removeEventListener('paste', handlePaste)
})

const confirm = () => {
  if (activeTab.value === 'local') {
    emit('save', previewUrl.value)
  } else {
    emit('save', imageUrl.value)
  }
}
</script>