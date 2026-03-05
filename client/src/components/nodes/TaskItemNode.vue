<template>
  <node-view-wrapper as="li" class="task-item flex items-start gap-3 my-1">
    <label class="flex-none mt-1.5 select-none cursor-pointer" contenteditable="false">
      <input 
        type="checkbox" 
        :checked="node.attrs.checked" 
        @change="handleChange"
        class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 transition-colors cursor-pointer"
      />
    </label>
    <div class="flex-1 min-w-0">
      <node-view-content class="task-content" />
      <div class="text-[10px] text-gray-400 mt-0.5 flex flex-wrap gap-x-3 gap-y-1 select-none font-mono opacity-60 hover:opacity-100 transition-opacity" contenteditable="false">
        <span v-if="node.attrs.createdAt" title="创建时间">
          🕒 {{ formatDate(node.attrs.createdAt) }}
        </span>
        <span v-if="node.attrs.completedAt" title="完成时间" class="text-green-600">
          ✅ {{ formatDate(node.attrs.completedAt) }}
        </span>
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper, NodeViewContent } from '@tiptap/vue-3'
import { onMounted } from 'vue'

const props = defineProps(nodeViewProps)

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const checked = target.checked
  
  props.updateAttributes({
    checked,
    completedAt: checked ? new Date().toISOString() : null
  })
}

const formatDate = (isoString: string) => {
  try {
    const date = new Date(isoString)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch {
    return ''
  }
}

onMounted(() => {
  if (!props.node.attrs.createdAt) {
    props.updateAttributes({
      createdAt: new Date().toISOString()
    })
  }
})
</script>

<style scoped>
.task-item {
  display: flex;
}

.task-content {
  flex: 1;
}

/* Override ProseMirror's default task list styles to prevent duplication or conflict */
:deep(p) {
  margin: 0 !important;
}
</style>