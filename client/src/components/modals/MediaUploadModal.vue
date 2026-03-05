<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[500px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">插入{{ mediaLabel }}</h3>
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
          网络地址
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
            <input type="file" ref="fileInput" class="hidden" :accept="acceptTypes" @change="handleFileSelect" />
            
            <div v-if="uploading" class="absolute inset-0 bg-white bg-opacity-80 flex flex-col items-center justify-center z-10">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
              <span class="text-sm text-blue-500">上传中...</span>
            </div>

            <div v-if="previewUrl && !uploading" class="relative group">
               <template v-if="mediaType === 'image'">
                 <img :src="previewUrl" class="max-h-48 mx-auto rounded shadow-sm object-contain" />
               </template>
               <template v-else-if="mediaType === 'video'">
                 <video :src="previewUrl" controls class="max-h-48 mx-auto rounded shadow-sm"></video>
               </template>
               <template v-else-if="mediaType === 'audio'">
                 <audio :src="previewUrl" controls class="w-full mt-4"></audio>
                 <div class="text-center mt-2 text-sm text-gray-500 break-all">{{ fileName }}</div>
               </template>
               <template v-else-if="mediaType === 'file'">
                 <div class="flex flex-col items-center justify-center py-4">
                    <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <div class="text-center mt-2 text-sm text-gray-700 font-medium break-all px-4">{{ fileName }}</div>
                 </div>
               </template>
               
               <div class="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded">
                 <span class="text-white text-sm font-medium">点击更换</span>
               </div>
            </div>
            <div v-else-if="!uploading">
               <div class="text-gray-400 mb-2">
                 <svg v-if="mediaType === 'image'" class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                 <svg v-else-if="mediaType === 'video'" class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                 <svg v-else-if="mediaType === 'audio'" class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path></svg>
                 <svg v-else class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
               </div>
               <p class="text-gray-500 text-sm font-medium">点击选择或拖拽{{ mediaLabel }}到此处</p>
               <p v-if="mediaType === 'image'" class="text-gray-400 text-xs mt-1">支持粘贴截图 (Ctrl+V)</p>
            </div>
          </div>
        </div>

        <!-- URL Input -->
        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ mediaLabel }}链接</label>
            <input 
              v-model="inputUrl" 
              type="text" 
              class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
              :placeholder="`https://example.com/${mediaType}.mp4`"
            />
          </div>
          <div v-if="inputUrl" class="border rounded p-2 bg-gray-50 flex justify-center min-h-[100px] items-center">
            <template v-if="mediaType === 'image'">
                <img :src="inputUrl" class="max-h-48 object-contain" @error="loadError = true" @load="loadError = false" v-show="!loadError" />
            </template>
            <template v-else-if="mediaType === 'video'">
                <video :src="inputUrl" controls class="max-h-48 object-contain" @error="loadError = true" @loadeddata="loadError = false" v-show="!loadError"></video>
            </template>
            <template v-else-if="mediaType === 'audio'">
                <audio :src="inputUrl" controls class="w-full" @error="loadError = true" @loadeddata="loadError = false" v-show="!loadError"></audio>
            </template>
            <span v-if="loadError" class="text-red-500 text-sm">加载失败</span>
          </div>
        </div>
      </div>

      <div class="p-4 border-t flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded text-sm font-medium">取消</button>
        <button 
          @click="confirm" 
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          :disabled="!canConfirm || uploading"
        >
          插入{{ mediaLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'
import { uploadFile } from '../../utils/upload'

const props = defineProps<{
  mediaType: 'image' | 'video' | 'audio' | 'file'
}>()

const emit = defineEmits(['close', 'save'])

const activeTab = ref<'local' | 'url'>('local')
const inputUrl = ref('')
const previewUrl = ref('') // URL returned from server or blob url (temporarily)
const loadError = ref(false)
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const fileName = ref('')

const mediaLabel = computed(() => {
  const map = { image: '图片', video: '视频', audio: '音频', file: '附件' }
  return map[props.mediaType]
})

const acceptTypes = computed(() => {
  const map = { image: 'image/*', video: 'video/*', audio: 'audio/*', file: '*/*' }
  return map[props.mediaType]
})

const canConfirm = computed(() => {
  if (activeTab.value === 'local') return !!previewUrl.value
  return !!inputUrl.value && !loadError.value
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
  if (file) {
    if (props.mediaType === 'file' || file.type.startsWith(props.mediaType + '/')) {
      processFile(file)
    }
  }
}

const processFile = async (file: File) => {
  uploading.value = true
  fileName.value = file.name
  
  try {
      const url = await uploadFile(file)
      previewUrl.value = url
  } catch (e) {
      console.error(e)
      // uploadFile already handles 401 alert
      if (e instanceof Error && e.message !== 'Unauthorized') {
          alert('上传失败，请重试')
      }
  } finally {
      uploading.value = false
  }
}

const handlePaste = (e: ClipboardEvent) => {
  if (activeTab.value !== 'local' || props.mediaType !== 'image') return
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
  const url = activeTab.value === 'local' ? previewUrl.value : inputUrl.value
  const name = activeTab.value === 'local' ? fileName.value : ''
  emit('save', { url, name })
}
</script>