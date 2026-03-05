<template>
  <node-view-wrapper as="td" class="relative group" :style="cellStyle" v-bind="attributes">
    <div v-if="isDateColumn" class="flex items-center justify-between h-full">
      <node-view-content class="flex-1 min-w-0" />
      <div class="relative ml-1">
        <input 
          type="date" 
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          @input="handleDateChange"
          :value="currentDate"
        />
        <Calendar class="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
      </div>
    </div>
    <node-view-content v-else class="h-full" />
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NodeViewWrapper, NodeViewContent, nodeViewProps } from '@tiptap/vue-3'
import { Calendar } from 'lucide-vue-next'

const props = defineProps(nodeViewProps)

const isDateColumn = computed(() => {
  return props.node.attrs.cellType === 'date'
})

const cellStyle = computed(() => {
  const style: Record<string, string> = {}
  
  const bg = props.node.attrs.backgroundColor
  if (bg) {
    style.backgroundColor = bg
  }

  const colwidth = props.node.attrs.colwidth
  if (colwidth && colwidth.length) {
    const totalWidth = colwidth.reduce((sum: number, w: number) => sum + w, 0)
    if (totalWidth > 0) {
      style.width = `${totalWidth}px`
    }
  }
  
  return style
})

const attributes = computed(() => {
  const attrs: Record<string, any> = {}
  
  if (props.node.attrs.colwidth) {
    attrs['data-colwidth'] = props.node.attrs.colwidth.join(',')
  }
  
  if (props.node.attrs.colspan > 1) {
    attrs.colspan = props.node.attrs.colspan
  }
  
  if (props.node.attrs.rowspan > 1) {
    attrs.rowspan = props.node.attrs.rowspan
  }
  
  return attrs
})

const currentDate = computed(() => {
  // Extract text content from the cell
  return props.node.textContent.trim()
})

const handleDateChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.value) {
    // Replace content with new date
    // We need to find the range of this node's content
    const pos = props.getPos()
    if (typeof pos !== 'number') return

    // Clear content and insert text
    // A table cell usually contains a paragraph. We should replace the text inside it.
    // Simpler: Just replace the whole content of the cell with a new paragraph containing the date.
    const tr = props.editor.state.tr
    const start = pos + 1 // Inside the cell
    const end = pos + props.node.nodeSize - 1
    
    tr.replaceWith(start, end, props.editor.schema.nodes.paragraph.create(null, props.editor.schema.text(input.value)))
    props.editor.view.dispatch(tr)
  }
}
</script>

<style scoped>
td {
  min-width: 1em;
  border: 2px solid #ced4da;
  padding: 3px 5px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
}
</style>