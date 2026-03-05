<template>
  <div class="fixed inset-0 z-[100] bg-white flex flex-col">
    <div class="h-16 bg-red-50 border-b flex items-center justify-between px-6 shadow-sm">
      <div>
        <h2 class="text-lg font-bold text-red-700 flex items-center gap-2">
          <AlertTriangle class="w-5 h-5" />
          检测到数据冲突
        </h2>
        <p class="text-sm text-gray-600 mt-1">本地缓存与服务器数据存在差异，请比对后选择处理方式。您可以在两侧画布间自由复制粘贴。</p>
      </div>
      <div class="text-xs text-gray-500">
        <span class="mr-4">本地时间: {{ formatDate(localDate) }}</span>
        <span>服务器时间: {{ formatDate(serverDate) }}</span>
      </div>
    </div>
    
    <div class="flex-1 flex overflow-hidden">
      <!-- Local (Offline) -->
      <div class="flex-1 border-r border-gray-300 relative flex flex-col">
        <div class="p-2 bg-gray-100 font-bold text-center border-b flex justify-between items-center px-4">
          <span>本地版本 (Offline)</span>
          <span class="text-xs font-normal text-gray-500">{{ localNodes.length }} 节点 / {{ localEdges.length }} 连线</span>
        </div>
        <div class="flex-1 relative bg-gray-50">
           <VueFlow 
            id="conflict-flow-local"
            v-model="localNodesState" 
            v-model:edges="localEdgesState"
            :node-types="nodeTypes"
             :fit-view-on-init="true"
             :min-zoom="0.1"
             :max-zoom="4"
             class="conflict-flow-local"
             @move="onLocalMove"
           >
             <Background pattern-color="#ccc" :gap="20" />
             <Controls />
           </VueFlow>
        </div>
      </div>

      <!-- Server (Online) -->
      <div class="flex-1 relative flex flex-col">
        <div class="p-2 bg-blue-100 font-bold text-center border-b flex justify-between items-center px-4">
          <span>云端版本 (Server)</span>
          <span class="text-xs font-normal text-gray-500">{{ serverNodes.length }} 节点 / {{ serverEdges.length }} 连线</span>
        </div>
        <div class="flex-1 relative bg-gray-50">
           <VueFlow 
            id="conflict-flow-server"
            v-model="serverNodesState" 
            v-model:edges="serverEdgesState"
            :node-types="nodeTypes"
             :fit-view-on-init="true"
             :min-zoom="0.1"
             :max-zoom="4"
             class="conflict-flow-server"
             @move="onServerMove"
           >
             <Background pattern-color="#ccc" :gap="20" />
             <Controls />
           </VueFlow>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="h-20 border-t bg-white flex items-center justify-center gap-4 px-6 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
      <div class="flex gap-2">
        <button 
          @click="$emit('resolve', 'overwrite_local')" 
          class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 text-gray-700 flex flex-col items-center min-w-[140px]"
          title="丢弃本地修改，使用云端版本"
        >
          <span class="font-bold">使用云端版本</span>
          <span class="text-xs text-gray-500">覆盖本地 (丢弃修改)</span>
        </button>
        
        <button 
          @click="$emit('resolve', 'overwrite_server')" 
          class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white flex flex-col items-center min-w-[140px]"
          title="将本地修改推送到云端"
        >
          <span class="font-bold">使用本地版本</span>
          <span class="text-xs text-blue-100">覆盖云端</span>
        </button>
      </div>

      <div class="w-px h-10 bg-gray-300 mx-2"></div>

      <button 
        @click="$emit('resolve', 'smart_merge')" 
        class="px-4 py-2 rounded border border-purple-200 bg-purple-50 hover:bg-purple-100 text-purple-700 flex flex-col items-center min-w-[140px]"
      >
        <span class="font-bold">智能合并</span>
        <span class="text-xs text-purple-500">保留双方所有节点</span>
      </button>

      <div class="w-px h-10 bg-gray-300 mx-2"></div>

      <div class="flex gap-2">
        <button 
          @click="$emit('resolve', 'save_online_copy')" 
          class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 text-gray-700 flex flex-col items-center min-w-[140px]"
          title="保留本地为当前版本，云端旧版另存为新文件"
        >
          <span class="font-bold">另存云端副本</span>
          <span class="text-xs text-gray-500">使用本地 + 备份云端</span>
        </button>

        <button 
          @click="$emit('resolve', 'save_offline_copy')" 
          class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 text-gray-700 flex flex-col items-center min-w-[140px]"
          title="保留云端为当前版本，本地修改另存为新文件"
        >
          <span class="font-bold">另存本地副本</span>
          <span class="text-xs text-gray-500">使用云端 + 备份本地</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, markRaw } from 'vue'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { AlertTriangle } from 'lucide-vue-next'
import NoteNode from '../nodes/NoteNode.vue'
import GroupNode from '../nodes/GroupNode.vue'

const props = defineProps<{
  localNodes: Node[]
  localEdges: Edge[]
  localDate?: number
  serverNodes: Node[]
  serverEdges: Edge[]
  serverDate?: string | number
}>()

const emit = defineEmits<{
  (e: 'resolve', action: 'overwrite_local' | 'overwrite_server' | 'smart_merge' | 'save_online_copy' | 'save_offline_copy'): void
}>()

const nodeTypes: any = {
  note: markRaw(NoteNode),
  group: markRaw(GroupNode),
}

const localNodesState = ref<Node[]>([])
const localEdgesState = ref<Edge[]>([])
const serverNodesState = ref<Node[]>([])
const serverEdgesState = ref<Edge[]>([])

// Sync Logic
const isSyncingLocal = ref(false)
const isSyncingServer = ref(false)

const onLocalMove = (params: { flowTransform: { x: number, y: number, zoom: number } }) => {
  if (isSyncingServer.value) return
  isSyncingLocal.value = true
  const { setViewport } = useVueFlow({ id: 'conflict-flow-server' })
  setViewport(params.flowTransform)
  setTimeout(() => isSyncingLocal.value = false, 10)
}

const onServerMove = (params: { flowTransform: { x: number, y: number, zoom: number } }) => {
  if (isSyncingLocal.value) return
  isSyncingServer.value = true
  const { setViewport } = useVueFlow({ id: 'conflict-flow-local' })
  setViewport(params.flowTransform)
  setTimeout(() => isSyncingServer.value = false, 10)
}

// Highlight Differences
const computeDiffs = () => {
   const localMap = new Map(props.localNodes.map(n => [n.id, n]))
   const serverMap = new Map(props.serverNodes.map(n => [n.id, n]))

   // Process Local Nodes
   localNodesState.value = props.localNodes.map(n => {
      const serverNode = serverMap.get(n.id)
      const newNode = JSON.parse(JSON.stringify(n))
      
      // Reset class
      newNode.class = (newNode.class || '').replace(/ring-\d+ ring-\w+-\d+/g, '').trim()

      if (!serverNode) {
         newNode.class = `${newNode.class} ring-4 ring-green-500 rounded-lg`.trim() // Added locally
      } else if (JSON.stringify(n.data) !== JSON.stringify(serverNode.data)) {
         newNode.class = `${newNode.class} ring-4 ring-yellow-500 rounded-lg`.trim() // Modified
      }
      return newNode
   })

   // Process Server Nodes
   serverNodesState.value = props.serverNodes.map(n => {
      const localNode = localMap.get(n.id)
      const newNode = JSON.parse(JSON.stringify(n))
      
      // Reset class
      newNode.class = (newNode.class || '').replace(/ring-\d+ ring-\w+-\d+/g, '').trim()

      if (!localNode) {
         newNode.class = `${newNode.class} ring-4 ring-green-500 rounded-lg`.trim() // Added on server (New relative to local)
      } else if (JSON.stringify(n.data) !== JSON.stringify(localNode.data)) {
         newNode.class = `${newNode.class} ring-4 ring-yellow-500 rounded-lg`.trim() // Modified
      }
      return newNode
   })
   
   localEdgesState.value = JSON.parse(JSON.stringify(props.localEdges))
   serverEdgesState.value = JSON.parse(JSON.stringify(props.serverEdges))
}

watch(() => [props.localNodes, props.serverNodes], computeDiffs, { immediate: true })

const formatDate = (date?: string | number) => {
  if (!date) return '未知时间'
  return new Date(date).toLocaleString()
}
</script>

<style scoped>
.conflict-flow-local {
  background-color: #f9fafb;
}
.conflict-flow-server {
  background-color: #f0f9ff;
}
</style>