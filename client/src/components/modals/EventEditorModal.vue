<template>
  <div class="fixed inset-0 z-[1000] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[80vw] h-[80vh] flex flex-col overflow-hidden animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
        <h3 class="text-lg font-medium text-gray-900">{{ title || '编辑内容' }}</h3>
        <div class="flex items-center gap-2">
          <button 
            @click="handleSave" 
            class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 flex items-center gap-1 transition-colors"
          >
            <Save class="w-4 h-4" /> 保存
          </button>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100 transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
      </div>
      
      <!-- Editor Content -->
      <div class="flex-1 overflow-hidden bg-white relative flex flex-col">
        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
           <TiptapEditor 
            ref="editorRef" 
            v-model="localContent" 
            :editable="true" 
            class="min-h-full"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X, Save } from 'lucide-vue-next'
import TiptapEditor from '../nodes/TiptapEditor.vue'

const props = defineProps<{
  initialContent: string
  title?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', content: string): void
}>()

const localContent = ref('')
const editorRef = ref()

onMounted(() => {
  localContent.value = props.initialContent
})

const handleSave = () => {
  emit('save', localContent.value)
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>