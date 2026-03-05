<template>
  <node-view-wrapper class="table-node-wrapper">
    <BaseBlockWrapper :editor="props.editor" :node="props.node" :get-pos="props.getPos">
      <!-- Table Content -->
      <div class="overflow-x-auto">
        <table class="border-collapse table-fixed min-w-full">
          <node-view-content as="tbody" />
        </table>
      </div>
    </BaseBlockWrapper>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper, NodeViewContent } from '@tiptap/vue-3'
import BaseBlockWrapper from './BaseBlockWrapper.vue'

const props = defineProps(nodeViewProps)
</script>

<style scoped>
:deep(table) {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
}

:deep(td),
:deep(th) {
  min-width: 1em;
  border: 1px solid #ced4da;
  padding: 6px 8px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
}

:deep(th) {
  font-weight: bold;
  text-align: left;
  background-color: #f8f9fa;
}

:deep(.selectedCell:after) {
  z-index: 2;
  position: absolute;
  content: "";
  left: 0; right: 0; top: 0; bottom: 0;
  background: rgba(200, 200, 255, 0.4);
  pointer-events: none;
}

:deep(.column-resize-handle) {
  position: absolute;
  right: -6px;
  top: 0;
  bottom: 0;
  width: 12px;
  background-color: transparent;
  z-index: 100;
  cursor: col-resize;
  pointer-events: auto;
}

:deep(.column-resize-handle:hover),
:deep(.column-resize-handle.selected) {
  background-color: #adf;
  opacity: 1;
}
</style>
