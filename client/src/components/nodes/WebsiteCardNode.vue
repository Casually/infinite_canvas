<template>
  <node-view-wrapper class="website-card-node">
    <BaseBlockWrapper :editor="editor" :node="node" :get-pos="getPos">
      <div 
        class="flex items-start p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer max-w-2xl"
        :class="{ 'ring-2 ring-blue-500': selected && props.editor.isEditable }"
        @click="handleClick"
      >
        <!-- Loading State -->
        <div v-if="loading" class="p-4 flex items-center gap-3">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          <span class="text-sm text-gray-500">正在加载网站信息...</span>
        </div>

        <!-- Content State -->
        <div v-else class="h-full flex flex-col">
          <!-- Image -->
          <div v-if="metadata.image" class="h-48 w-full overflow-hidden border-b border-gray-100 relative bg-gray-50 shrink-0">
             <img :src="metadata.image" class="w-full h-full object-cover" :alt="metadata.title" @error="metadata.image = ''" />
          </div>
          
          <!-- Info -->
          <div class="p-3 flex flex-col justify-between min-w-0 flex-1">
            <div>
              <h3 class="font-bold text-gray-800 text-sm line-clamp-1 mb-1 group-hover:text-blue-600 transition-colors" :title="metadata.title">
                {{ metadata.title || url }}
              </h3>
              <p class="text-xs text-gray-500 line-clamp-2">
                {{ metadata.description || '无描述信息' }}
              </p>
            </div>
            <div class="flex items-center gap-2 mt-2 pt-2 border-t border-gray-50">
              <img :src="`https://www.google.com/s2/favicons?domain=${domain}`" class="w-4 h-4" />
              <span class="text-xs text-gray-400 truncate">{{ domain }}</span>
            </div>
          </div>
        </div>
      </div>
    </BaseBlockWrapper>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { computed, onMounted, ref } from 'vue'
import BaseBlockWrapper from './BaseBlockWrapper.vue'

const props = defineProps(nodeViewProps)

const url = computed(() => props.node.attrs.url)
const domain = computed(() => {
  try {
    return new URL(url.value).hostname
  } catch {
    return url.value
  }
})

const loading = ref(true)
const metadata = ref({
  title: '',
  description: '',
  image: ''
})

let clickTimer: ReturnType<typeof setTimeout> | null = null

const handleClick = (e: MouseEvent) => {
  // Check for Alt key during edit mode
  if (props.editor.isEditable && e.altKey) {
    window.open(url.value, '_blank')
    e.preventDefault()
    return
  }

  if (!props.editor.isEditable) {
    if (clickTimer) {
      clearTimeout(clickTimer)
      clickTimer = null
      return
    }
    
    clickTimer = setTimeout(() => {
      window.open(url.value, '_blank')
      clickTimer = null
    }, 250)
  }
}

onMounted(async () => {
  try {
    // Check if we already have metadata stored in attributes (optional optimization)
    // For now, let's always fetch to keep it fresh, or maybe we should store it?
    // Storing it in the node attributes is better for persistence!
    
    if (props.node.attrs.title) {
      metadata.value = {
        title: props.node.attrs.title,
        description: props.node.attrs.description,
        image: props.node.attrs.image
      }
      loading.value = false
      return
    }

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/fetch-metadata`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value })
    })
    
    const data = await res.json()
    metadata.value = data
    
    // Update node attributes so we don't fetch again next time
    props.updateAttributes({
      title: data.title,
      description: data.description,
      image: data.image
    })
    
  } catch (e) {
    console.error('Failed to fetch metadata', e)
    metadata.value.title = url.value
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.website-card-wrapper {
  max-width: 600px;
}
</style>