<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[400px] overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">插入网站卡片</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      
      <div class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">网站链接 (URL)</label>
          <div class="flex gap-2">
            <input 
              v-model="url" 
              type="text" 
              class="flex-1 border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
              placeholder="https://example.com"
              @keydown.enter="fetchMetadata"
              v-focus
            />
            <button 
              @click="fetchMetadata"
              class="px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm disabled:opacity-50"
              :disabled="loading"
            >
              {{ loading ? '获取中...' : '获取信息' }}
            </button>
          </div>
        </div>

        <div v-if="hasFetched" class="space-y-3 animate-fade-in">
           <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input 
              v-model="metadata.title" 
              type="text" 
              class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
            <textarea 
              v-model="metadata.description" 
              rows="3"
              class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">封面图片 URL</label>
            <input 
              v-model="metadata.image" 
              type="text" 
              class="w-full border rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm"
              placeholder="https://..."
            />
          </div>

          <!-- Preview -->
          <div class="border rounded-lg overflow-hidden bg-gray-50 mt-2">
            <div v-if="metadata.image" class="h-32 w-full overflow-hidden border-b border-gray-100">
              <img :src="metadata.image" class="w-full h-full object-cover" alt="Preview" @error="metadata.image = ''" />
            </div>
            <div class="p-3">
               <h4 class="font-bold text-sm text-gray-800 mb-1 truncate">{{ metadata.title || url }}</h4>
               <p class="text-xs text-gray-500 line-clamp-2">{{ metadata.description || '无描述信息' }}</p>
               <div class="flex items-center gap-2 mt-2 pt-2 border-t border-gray-200">
                  <span class="text-xs text-gray-400">{{ previewHostname }}</span>
               </div>
            </div>
          </div>
        </div>
      </div>

      <div class="p-4 border-t flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded text-sm font-medium">取消</button>
        <button 
          @click="confirm" 
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          :disabled="!isValid"
        >
          插入卡片
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'

const emit = defineEmits(['close', 'save'])

const url = ref('')
const loading = ref(false)
const hasFetched = ref(false)
const metadata = reactive({
  title: '',
  description: '',
  image: ''
})

const isValid = computed(() => {
  return url.value.length > 0
})

const previewHostname = computed(() => {
  try {
    return new URL(url.value).hostname
  } catch {
    return url.value
  }
})

const fetchMetadata = async () => {
  if (!url.value) return
  
  // Basic URL validation
  if (!url.value.startsWith('http')) {
    url.value = 'https://' + url.value
  }

  loading.value = true
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/fetch-metadata`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value })
    })
    
    if (res.ok) {
      const data = await res.json()
      metadata.title = data.title || ''
      metadata.description = data.description || ''
      metadata.image = data.image || ''
      hasFetched.value = true
    }
  } catch (e) {
    console.error('Failed to fetch metadata', e)
    // Fallback
    metadata.title = url.value
    hasFetched.value = true
  } finally {
    loading.value = false
  }
}

const confirm = () => {
  if (isValid.value) {
    if (!hasFetched.value) {
       // If user didn't click fetch, try to fetch or just use raw URL
       // Let's just emit raw URL and let the node handle it? 
       // No, we want to force manual check if possible, but for UX speed, maybe just emit.
       // But the requirement is "allow manual modification".
       // If I emit just URL, the node will fetch again.
       // Let's emit what we have. If hasFetched is false, metadata is empty.
       // We can trigger fetch here? Or just emit URL string if no metadata.
       // But to support the new signature, we should emit object.
       emit('save', { url: url.value, ...metadata })
    } else {
       emit('save', { url: url.value, ...metadata })
    }
    emit('close')
  }
}

const vFocus = {
  mounted: (el: HTMLElement) => el.focus()
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>