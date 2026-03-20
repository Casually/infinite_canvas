<template>
  <div class="h-full w-full relative" :class="{ 'locked-canvas': isReadOnly }" @contextmenu.prevent>
    <VueFlow
      v-model="nodes"
      v-model:edges="edges"
      :node-types="nodeTypes as any"
      @pane-ready="onPaneReady"
      @pane-dbl-click="onPaneDblClick"
      @pane-context-menu="onPaneContextMenu"
      @selection-context-menu="onSelectionContextMenu"
      @node-context-menu="onNodeContextMenu"
      @connect="onConnect"
      @click="closeMenu"
      :select-nodes-on-drag="true"
      :selection-key-code="'Shift'"
      :multi-selection-key-code="['Meta', 'Control']"
      :snap-to-grid="true"
      :snap-grid="[20, 20]"
      :min-zoom="0.1"
      :max-zoom="4"
      :delete-keys="isReadOnly ? [] : ['Backspace', 'Delete']"
      :pan-on-scroll="interactionMode === 'trackpad'"
      :zoom-on-scroll="interactionMode === 'mouse'"
      :zoom-on-pinch="interactionMode === 'trackpad'"
      :pan-on-drag="true"
      :nodes-draggable="!isReadOnly"
      :nodes-connectable="!isReadOnly"
      :edges-updatable="!isReadOnly"
      fit-view-on-init
      class="bg-gray-50"
    >
      <Background pattern-color="#aaa" :gap="20" />
      <Controls>
        <div class="vue-flow__controls-button" title="撤销 (Undo)" @click="undo" :class="{ '!cursor-not-allowed !opacity-50': !canUndo }">
          <Undo class="w-4 h-4" />
        </div>
        <div class="vue-flow__controls-button" title="重做 (Redo)" @click="redo" :class="{ '!cursor-not-allowed !opacity-50': !canRedo }">
          <Redo class="w-4 h-4" />
        </div>
      </Controls>
      <MiniMap pannable zoomable />
    </VueFlow>

    <!-- Offline Indicator -->
    <div v-if="isOfflineMode" class="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 bg-orange-100 border border-orange-200 text-orange-800 px-3 py-1.5 rounded-full text-xs flex items-center gap-2 shadow-sm">
       <WifiOff class="w-3 h-3" />
       <span>当前为离线使用，请勿清理浏览器缓存</span>
    </div>

    <!-- Context Menu -->
    <div
      v-if="menu.visible"
      class="fixed z-50 bg-white border rounded-lg shadow-xl py-1 w-56 text-sm text-gray-700"
      :style="{ top: `${menu.y}px`, left: `${menu.x}px` }"
    >
      <div v-if="menu.type === 'pane'">
        <button @click="addNote" class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center">
          新建便签
        </button>
        <button @click="addGroup" class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center">
          新建分组
        </button>
      </div>

      <div v-if="menu.type === 'node' || menu.type === 'selection'">
        <button @click="openShareForSelection" class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center">
           分享...
        </button>
        <button
          v-if="selectedNodes.length <= 1"
          @click="openTimersForSelection"
          class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center"
        >
          定时任务...
        </button>
        <button
          v-if="menu.type === 'node' && selectedNodes.length <= 1 && isContextGroupNode"
          @click="autoLayoutGroupChildren"
          class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center"
        >
          组内一键布局
        </button>
        <div class="border-t my-1"></div>

        <div v-if="selectedNodes.length > 1">
          <button @click="groupNodes" class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center">
            所选节点编组
          </button>
          <div class="border-t my-1"></div>
          <button @click="autoLayoutNodes" class="w-full text-left px-4 py-2 hover:bg-gray-100">一键布局</button>
          <button @click="connectSelectedNodes" class="w-full text-left px-4 py-2 hover:bg-gray-100">一键连线</button>
          <div class="px-4 py-1 text-xs text-gray-400">对齐</div>
          <button @click="alignNodes('left')" class="w-full text-left px-4 py-2 hover:bg-gray-100">左对齐</button>
          <button @click="alignNodes('top')" class="w-full text-left px-4 py-2 hover:bg-gray-100">顶部对齐</button>
        </div>
        
        <div v-if="selectedNodes.length > 0">
           <div class="border-t my-1"></div>
           <button @click="duplicateNodes" class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2">
             <Copy class="w-4 h-4" /> 复制节点
           </button>
        </div>
        
          <div v-if="menu.type === 'node' && selectedNodes.length <= 1">
           <div class="px-4 py-2 border-b border-gray-100">
             <div class="text-xs text-gray-500 mb-2 font-medium">外观</div>
             <div class="flex gap-2 flex-wrap mb-3">
               <button 
                 v-for="color in colors" 
                 :key="color"
                 class="w-6 h-6 rounded-full border border-gray-200 hover:ring-2 ring-blue-300 transition-all"
                 :style="{ backgroundColor: color }"
                 @click="setNodeColor(color)"
                 :title="color"
               />
               <!-- Custom Color Picker -->
               <div class="relative w-6 h-6 rounded-full border border-gray-200 overflow-hidden hover:ring-2 ring-blue-300 transition-all flex items-center justify-center bg-white">
                 <span class="text-xs text-gray-400">+</span>
                 <input 
                   type="color" 
                   class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                   @input="(e) => setNodeColor((e.target as HTMLInputElement).value)"
                   title="自定义颜色"
                 />
               </div>
             </div>
             
             <!-- Font Settings -->
             <div class="mb-3 border-t border-gray-50 pt-2">
               <div class="text-xs text-gray-500 mb-2 font-medium">字体样式</div>
               <div class="flex items-center gap-2 mb-2">
                 <span class="text-xs text-gray-400 w-8">大小</span>
                 <input 
                   type="number" 
                   v-model.number="currentFontSize"
                   @change="updateFontStyle"
                   class="w-12 h-6 text-xs border rounded px-1"
                   min="8" max="72"
                 />
                 <span class="text-xs text-gray-400">px</span>
               </div>
               <div class="flex items-center gap-2">
                 <span class="text-xs text-gray-400 w-8">颜色</span>
                 <input 
                   type="color" 
                   v-model="currentFontColor"
                   @input="updateFontStyle"
                   class="w-6 h-6 border-0 p-0 rounded cursor-pointer bg-transparent"
                 />
               </div>
             </div>
           </div>

           <button @click="deleteNode" class="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- Node Content Preview Modal -->
    <div v-if="previewNode" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="closePreview">
      <div 
        class="bg-white shadow-xl flex flex-col overflow-hidden transition-all duration-300"
        :class="isPreviewFullscreen ? 'fixed inset-0 w-full h-full rounded-none' : 'w-3/4 h-3/4 rounded-lg'"
      >
        <div class="flex items-center justify-between p-4 border-b">
          <h3 class="font-bold text-lg">{{ previewNode.data.label || '无标题' }}</h3>
          <div class="flex items-center gap-2">
            <button 
              @click="showTableOfContents = !showTableOfContents" 
              class="p-1 hover:bg-gray-100 rounded text-gray-500"
              :class="{ 'bg-gray-100 text-blue-600': showTableOfContents }"
              title="目录"
            >
              <List class="w-5 h-5" />
            </button>
            <button 
              @click="isPreviewFullscreen = !isPreviewFullscreen" 
              class="p-1 hover:bg-gray-100 rounded text-gray-500"
              :title="isPreviewFullscreen ? '退出全屏' : '全屏'"
            >
              <Minimize2 v-if="isPreviewFullscreen" class="w-5 h-5" />
              <Maximize2 v-else class="w-5 h-5" />
            </button>
            <button @click="closePreview" class="p-1 hover:bg-gray-100 rounded text-gray-500">
              <X class="w-6 h-6" />
            </button>
          </div>
        </div>
        <div class="flex-1 flex overflow-hidden">
          <TableOfContents 
            :content="previewNode.data.content" 
            :is-open="showTableOfContents"
            :container-ref="previewContainerRef"
          />
          <div ref="previewContainerRef" class="flex-1 overflow-y-auto p-4 relative">
             <TiptapEditor v-model="previewNode.data.content" :editable="true" :node-id="previewNode.id" />
          </div>
        </div>
      </div>
    </div>

    <DrawingModal 
      v-if="showDrawingModal" 
      @close="showDrawingModal = false" 
      @save="handleDrawingSave" 
    />

    <MediaUploadModal 
      v-if="showMediaModal" 
      :media-type="currentMediaType"
      @close="showMediaModal = false" 
      @save="handleMediaSave" 
    />

    <LinkInputModal 
      v-if="showLinkModal" 
      @close="showLinkModal = false" 
      @save="handleLinkSave" 
    />

    <WebsiteCardModal 
      v-if="showCardModal" 
      @close="showCardModal = false" 
      @save="handleCardSave" 
    />
    
    <EChartsModal
      v-if="showEChartsModal"
      :initial-data="echartsInitialData"
      :initial-type="echartsInitialType"
      :readonly="echartsReadonly"
      @close="showEChartsModal = false"
      @save="handleEChartsSave"
    />

    <ConfirmationModal
      v-if="showConfirmModal"
      :message="confirmModalMessage"
      :checkbox-label="confirmModalCheckboxLabel || undefined"
      :checkbox-default-checked="confirmModalCheckboxDefaultChecked"
      @confirm="handleConfirm"
      @cancel="handleCancelConfirm"
    />

    <ShortcutSettingsModal
      v-if="showShortcutSettingsModal"
      @close="showShortcutSettingsModal = false"
    />

    <AuthModal
      v-if="showAuthModal"
      :show="showAuthModal"
      @close="showAuthModal = false"
      @login-success="handleLoginSuccess"
    />

    <ChangePasswordModal
      v-if="showChangePasswordModal"
      @close="showChangePasswordModal = false"
    />

    <TechSupportModal
      v-if="showTechSupportModal"
      @close="showTechSupportModal = false"
    />

    <SearchBar
      :visible="showSearch"
      :nodes="nodes"
      @close="showSearch = false"
      @select="handleSearchResult"
    />

    <NodeLinkModal
      v-if="showNodeLinkModal && linkSourceNodeId"
      :nodes="nodes"
      :exclude-node-id="linkSourceNodeId"
      @close="showNodeLinkModal = false"
      @confirm="handleNodeLinkConfirm"
    />

    <AlarmNotifications
      :notifications="alarmNotifications"
      @close="closeAlarmNotification"
      @locate="focusNodeById"
    />

    <NodeTimerManagerModal
      v-if="showNodeTimerModal && activeTimerNode"
      :node-id="activeTimerNode.id"
      :node-title="activeTimerNode.data?.label"
      v-model="activeTimerNodeTimers"
      @close="showNodeTimerModal = false"
    />
    
    <!-- Canvas Title -->
    <div class="absolute top-4 left-4 z-10 bg-white rounded-md shadow border px-3 py-2 flex items-center gap-2">
       <input 
         v-if="isEditingTitle && !isReadOnly"
         ref="titleInput"
         v-model="tempTitle" 
         @blur="saveTitle" 
         @keyup.enter="saveTitle"
         class="font-bold text-gray-800 outline-none bg-transparent min-w-[150px]"
       />
       <span 
         v-else 
         @dblclick="!isReadOnly && startEditingTitle()"
         class="font-bold text-gray-800 select-none"
         :class="{ 'cursor-pointer': !isReadOnly }"
         title="双击重命名"
       >
         {{ canvasTitle || '未命名画布' }}
       </span>
    </div>

    <!-- User Controls -->
    <div class="absolute top-4 right-4 z-10 flex items-center gap-2">
      <ActiveUsers :users="activeUsers" />
      
      <button 
        v-if="currentCanvasId && !isReadOnly"
        @click="showHistoryModal = true"
        class="bg-white px-3 py-2 rounded-md shadow border hover:bg-gray-50 transition-colors text-sm font-medium text-gray-600 flex items-center gap-1"
        title="历史记录"
      >
        <History class="w-4 h-4" />
      </button>

      <button 
        v-if="currentCanvasId"
        @click="openShareForSelection"
        class="bg-white px-3 py-2 rounded-md shadow border hover:bg-gray-50 transition-colors text-sm font-medium text-blue-600 flex items-center gap-1"
      >
        <span>分享</span>
      </button>

      <button 
        @click="openHelp"
        class="bg-white px-3 py-2 rounded-md shadow border hover:bg-gray-50 transition-colors text-sm font-medium text-gray-600 flex items-center gap-1"
        title="帮助文档"
      >
        <HelpCircle class="w-4 h-4" />
      </button>

      <CanvasSwitcherDropdown
        :current-canvas-id="currentCanvasId"
        :current-title="canvasTitle"
        :disabled="!user"
        @select="handleCanvasSelect"
      />

      <UserMenu 
      v-model:interactionMode="interactionMode"
      :user="user"
      @login="showAuthModal = true"
      @logout="logout"
        @change-password="handleChangePassword"
        @open-shortcuts="showShortcutSettingsModal = true"
        @open-canvas-manager="showCanvasManagerModal = true"
        @open-share-manager="showShareManagerModal = true"
        @update-user="handleUserUpdate"
        @export-data="handleExportData"
        @import-data="handleImportData"
      />
      
      <!-- Hidden File Input for Import -->
      <input 
        type="file" 
        ref="fileInput" 
        accept=".json" 
        class="hidden" 
        @change="onFileSelected"
      />
    </div>

    <CanvasManagerModal
      v-if="showCanvasManagerModal"
      :user="user"
      :current-canvas-id="currentCanvasId || undefined"
      @close="showCanvasManagerModal = false"
      @select="handleCanvasSelect"
    />

    <ShareModal
      v-if="showShareModal"
      :canvas-id="currentCanvasId!"
      :token="user?.token || ''"
      @close="showShareModal = false"
    />

    <NodeShareModal
      v-if="showNodeShareModal"
      :canvas-id="currentCanvasId!"
      :nodes="nodes"
      :pre-selected-node-ids="preSelectedNodeIds"
      @close="showNodeShareModal = false"
    />

    <ShareManagerModal
      v-if="showShareManagerModal"
      @close="showShareManagerModal = false"
    />

    <HistoryModal
      v-if="showHistoryModal"
      :canvas-id="currentCanvasId!"
      @close="showHistoryModal = false"
      @restore="handleHistoryRestore"
    />

    <PasswordModal
      v-if="showPasswordModal"
      @close="showPasswordModal = false"
      @confirm="handlePasswordConfirm"
    />

    <CanvasConflictResolver
      v-if="showConflictResolver"
      :local-nodes="conflictData.local.nodes"
      :local-edges="conflictData.local.edges"
      :local-date="conflictData.local.date"
      :server-nodes="conflictData.server.nodes"
      :server-edges="conflictData.server.edges"
      :server-date="conflictData.server.date"
      @resolve="handleConflictResolve"
    />

    <!-- Tech Support Footer -->
    <div class="absolute bottom-2 right-4 z-10">
      <button 
        @click="showTechSupportModal = true" 
        class="text-xs text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-1 bg-white bg-opacity-80 px-2 py-1 rounded-full shadow-sm backdrop-blur-sm"
      >
        <span>丰小子科技提供技术支持</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw, computed, reactive, onMounted, onUnmounted, watch, triggerRef, nextTick } from 'vue'
import { VueFlow, useVueFlow, type Node, type Edge, type Connection, addEdge, type NodeMouseEvent, type VueFlowStore } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { v4 as uuidv4 } from 'uuid'
import { useRefHistory } from '@vueuse/core'
import NoteNode from './nodes/NoteNode.vue'
import GroupNode from './nodes/GroupNode.vue'
import { Undo, Redo, X, Copy, History, WifiOff, HelpCircle, Maximize2, Minimize2, List } from 'lucide-vue-next'
import { provide } from 'vue'
import TiptapEditor from './nodes/TiptapEditor.vue'
import TableOfContents from './ui/TableOfContents.vue'
import DrawingModal from './modals/DrawingModal.vue'
import MediaUploadModal from './modals/MediaUploadModal.vue'
import LinkInputModal from './modals/LinkInputModal.vue'
import WebsiteCardModal from './modals/WebsiteCardModal.vue'
import EChartsModal from './modals/EChartsModal.vue'
import ConfirmationModal from './modals/ConfirmationModal.vue'
import AuthModal from './modals/AuthModal.vue'
import ChangePasswordModal from './modals/ChangePasswordModal.vue'
import TechSupportModal from './modals/TechSupportModal.vue'
import ShortcutSettingsModal from './modals/ShortcutSettingsModal.vue'
import SearchBar from './ui/SearchBar.vue'
import AlarmNotifications, { type AlarmNotification } from './ui/AlarmNotifications.vue'
import UserMenu from './ui/UserMenu.vue'
import CanvasSwitcherDropdown from './ui/CanvasSwitcherDropdown.vue'
import ActiveUsers from './ActiveUsers.vue'
import CanvasManagerModal from './modals/CanvasManagerModal.vue'
import ShareModal from './modals/ShareModal.vue'
import NodeShareModal from './modals/NodeShareModal.vue'
import ShareManagerModal from './modals/ShareManagerModal.vue'
import HistoryModal from './modals/HistoryModal.vue'
import PasswordModal from './modals/PasswordModal.vue'
import NodeTimerManagerModal, { type NodeTimer } from './modals/NodeTimerManagerModal.vue'
import NodeLinkModal from './modals/NodeLinkModal.vue'
import CanvasConflictResolver from './modals/CanvasConflictResolver.vue'
import { io, type Socket } from 'socket.io-client'
import { useShortcuts } from '../composables/useShortcuts'
import { nextCronTimestamp } from '../utils/cron'

const { matchShortcut } = useShortcuts()

let debouncedSaveTimer: ReturnType<typeof setTimeout> | null = null

const interactionMode = ref<'mouse' | 'trackpad'>(localStorage.getItem('interactionMode') as 'mouse' | 'trackpad' || 'mouse')

watch(interactionMode, (mode) => {
  localStorage.setItem('interactionMode', mode)
})

const showCanvasManagerModal = ref(false)
const showShareModal = ref(false)
const showNodeShareModal = ref(false)
const showShareManagerModal = ref(false)
const showHistoryModal = ref(false)
const showPasswordModal = ref(false)
const pendingCanvasId = ref<string | null>(null)
const preSelectedNodeIds = ref<string[]>([])
const currentCanvasId = ref<string | null>(null)
const canvasTitle = ref('未命名画布')
const activeUsers = ref<any[]>([])
const socket = ref<Socket | null>(null)
const isSharedView = ref(false)
const currentShareId = ref<string | null>(null)
const sharePassword = ref<string | null>(null)
const isReadOnly = ref(false)
const isTemporaryLock = ref(false)
const isRemoteUpdate = ref(false)
const isOfflineMode = ref(false)
const isCheckingConflict = ref(false)
const showConflictResolver = ref(false)
const conflictData = reactive({
  local: { nodes: [] as Node[], edges: [] as Edge[], date: 0 },
  server: { nodes: [] as Node[], edges: [] as Edge[], date: 0 }
})

const checkConnectivity = async () => {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 2000)
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/health`, { 
        method: 'GET', 
        signal: controller.signal 
    })
    clearTimeout(timeoutId)
    return res.ok
  } catch (e) {
    return false
  }
}

const handleConflictResolve = async (action: 'overwrite_local' | 'overwrite_server' | 'smart_merge' | 'save_online_copy' | 'save_offline_copy') => {
  if (action === 'overwrite_local') {
    // Use Server Data (discard local)
    nodes.value = conflictData.server.nodes
    edges.value = conflictData.server.edges
    saveToLocalCache(currentCanvasId.value!, {
      content: { nodes: nodes.value, edges: edges.value, viewport: viewport.value },
      title: canvasTitle.value
    })
    // We are now in sync with server
    isOfflineMode.value = false
  } else if (action === 'overwrite_server') {
    // Use Local Data (overwrite server)
    nodes.value = conflictData.local.nodes
    edges.value = conflictData.local.edges
    // Explicitly set offline mode to false to skip conflict check in saveToServer
    isOfflineMode.value = false 
    await saveToServer()
  } else if (action === 'smart_merge') {
    // Smart Merge: Union of nodes
    const serverNodeMap = new Map(conflictData.server.nodes.map(n => [n.id, n]))
    const serverEdgeMap = new Map(conflictData.server.edges.map(e => [e.id, e]))
    
    const mergedNodes = [...conflictData.server.nodes]
    const mergedEdges = [...conflictData.server.edges]
    
    conflictData.local.nodes.forEach(localNode => {
      const serverNode = serverNodeMap.get(localNode.id)
      if (!serverNode) {
        // New local node
        mergedNodes.push(localNode)
      } else {
        // Conflict: if different, we prefer Local because user was offline? 
        // Or maybe we should keep Server if it's "newer"?
        // User asked for "Smart Merge", let's assume "Keep both if possible" is hard with same ID.
        // Let's just prefer Local for now as it's the "user's latest work".
        // But to be "Smart", maybe we only update if content differs?
        if (JSON.stringify(serverNode.data) !== JSON.stringify(localNode.data) || 
            serverNode.position.x !== localNode.position.x || 
            serverNode.position.y !== localNode.position.y) {
           // Overwrite with local
           const index = mergedNodes.findIndex(n => n.id === localNode.id)
           if (index !== -1) mergedNodes[index] = localNode
        }
      }
    })
    
    conflictData.local.edges.forEach(localEdge => {
       if (!serverEdgeMap.has(localEdge.id)) {
         mergedEdges.push(localEdge)
       }
    })
    
    nodes.value = mergedNodes
    edges.value = mergedEdges
    // Explicitly set offline mode to false to skip conflict check in saveToServer
    isOfflineMode.value = false
    await saveToServer()
    
  } else if (action === 'save_online_copy') {
    // Save Server Data as NEW canvas, keep Local as Current
    // 1. Create backup of Server Data
    await createNewCanvas(conflictData.server, `${canvasTitle.value} (云端备份)`)
    
    // 2. Use Local Data as Current
    nodes.value = conflictData.local.nodes
    edges.value = conflictData.local.edges
    // Explicitly set offline mode to false to skip conflict check in saveToServer
    isOfflineMode.value = false
    await saveToServer()
    
  } else if (action === 'save_offline_copy') {
    // Save Local Data as NEW canvas, keep Server as Current
    // 1. Create backup of Local Data
    await createNewCanvas(conflictData.local, `${canvasTitle.value} (本地备份)`)
    
    // 2. Use Server Data as Current
    nodes.value = conflictData.server.nodes
    edges.value = conflictData.server.edges
    // No need to save to server, it's already there. Just update local cache.
    saveToLocalCache(currentCanvasId.value!, {
      content: { nodes: nodes.value, edges: edges.value, viewport: viewport.value },
      title: canvasTitle.value
    })
    // We are now in sync with server
    isOfflineMode.value = false
  }
  
  showConflictResolver.value = false
  triggerRef(nodes)
  logAndCommit()
}

// Helper to create new canvas
const createNewCanvas = async (data: any, title: string) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.value?.token}`
      },
      body: JSON.stringify({
        title,
        content: { nodes: data.nodes, edges: data.edges }
      })
    })
    if (res.ok) {
      addToast('副本创建成功', 'success')
    } else {
      throw new Error('Backup failed')
    }
  } catch (e) {
    console.error(e)
    addToast('创建副本失败', 'error')
  }
}

const saveToLocalCache = (id: string, data: any) => {
  try {
    localStorage.setItem(`canvas_cache_${id}`, JSON.stringify({
      ...data,
      cachedAt: Date.now()
    }))
  } catch (e) {
    console.error('Failed to save to local cache', e)
  }
}

const loadFromLocalCache = (id: string) => {
  try {
    const cached = localStorage.getItem(`canvas_cache_${id}`)
    if (cached) {
      return JSON.parse(cached)
    }
  } catch (e) {
    console.error('Failed to load from local cache', e)
  }
  return null
}

const initSocket = () => {
  if (socket.value) return
  
  socket.value = io(import.meta.env.VITE_API_BASE_URL, {
    transports: ['websocket'],
    autoConnect: true
  })
  
  socket.value.on('connect', () => {
    console.log('Connected to WebSocket')
    if (currentCanvasId.value) {
      joinCanvasRoom(currentCanvasId.value)
    }
  })
  
  socket.value.on('user_joined', (data: any) => {
    activeUsers.value = data.users || []
    addToast(`${data.username || '有人'} 加入了画布`, 'info')
  })
  
  socket.value.on('user_left', (data: any) => {
    activeUsers.value = data.users || []
  })
  
  socket.value.on('canvas_updated', (data: any) => {
    if (data.sender_id === socket.value?.id) return // Ignore own updates
    
    if (data.title) {
        canvasTitle.value = data.title
    }

    if (data.content) {
        isRemoteUpdate.value = true
        try {
          const content = typeof data.content === 'string' ? JSON.parse(data.content) : data.content
          nodes.value = content.nodes || []
          edges.value = content.edges || []
        } catch (e) {
          console.error('Failed to parse remote update:', e)
        }
        
        // Reset flag after a tick to allow local updates again
        nextTick(() => {
          isRemoteUpdate.value = false
        })
    }
  })
}

const joinCanvasRoom = (canvasId: string) => {
  if (!socket.value) return
  socket.value.emit('join', {
    canvas_id: canvasId,
    username: user.value?.nickname || user.value?.email || 'Guest',
    avatar: user.value?.avatar,
    color: '#' + Math.floor(Math.random()*16777215).toString(16)
  })
}

const handleCanvasSelect = async (id: string) => {
  if (currentCanvasId.value && socket.value) {
    socket.value.emit('leave', { canvas_id: currentCanvasId.value })
  }
  
  currentCanvasId.value = id
  localStorage.setItem('lastCanvasId', id)
  await loadCanvas(id)
  
  joinCanvasRoom(id)
  showCanvasManagerModal.value = false
}

const loadCanvas = async (id: string, password?: string) => {
  const ensureNodeTimestamps = (node: any) => {
    const nowIso = new Date().toISOString()
    if (!node.data) node.data = {}
    if (!node.data.createdAt) node.data.createdAt = node.data.updatedAt || nowIso
    if (!node.data.updatedAt) node.data.updatedAt = node.data.createdAt || nowIso
    return node
  }

  const normalizeNodes = (inputNodes: any[]) => {
    return (inputNodes || []).map((n: any) => {
      const node = ensureNodeTimestamps({ ...n })
      if (n?.type === 'group') {
        const style = (node.style || {}) as any
        if (style.zIndex === -1) {
          return { ...node, style: { ...style, zIndex: 0 } }
        }
      }
      return node
    })
  }

  try {
    const headers: Record<string, string> = {}
    if (user.value) {
      headers['Authorization'] = `Bearer ${user.value.token}`
    }
    if (password) {
      headers['X-Canvas-Password'] = password
    }

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${id}`, {
      headers
    })
    
    if (res.status === 401) {
      if (user.value) logout()
      throw new Error('Unauthorized') // Trigger fallback
    }

    if (res.status === 403) {
      const data = await res.json()
      if (data.requires_password) {
        pendingCanvasId.value = id
        showPasswordModal.value = true
        return
      }
      addToast(data.message || '无权访问', 'error')
      return
    }
    
    if (!res.ok) throw new Error('Load failed')
    
    const data = await res.json()
    canvasTitle.value = data.title
    
    let serverContent = { nodes: [] as any[], edges: [] as any[], viewport: undefined }
    
    // Handle compressed content
    if (data.compressed_content) {
        try {
            const binary = atob(data.compressed_content)
            const len = binary.length
            const bytes = new Uint8Array(len)
            for (let i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i)
            }
            const decompressed = pako.ungzip(bytes, { to: 'string' })
            serverContent = JSON.parse(decompressed)
        } catch (e) {
            console.error('Decompression failed', e)
            addToast('数据解压失败', 'error')
            return
        }
    } else if (data.content) {
      serverContent = typeof data.content === 'string' ? JSON.parse(data.content) : data.content
    }

    // Check Local Cache for Conflict
    const cached = loadFromLocalCache(id)
    if (cached && cached.content) {
       const localContent = cached.content
       
       // Compare (Simple stringify comparison)
       // We compare nodes and edges. Viewport difference is ignored for conflict.
       const serverStr = JSON.stringify({ nodes: serverContent.nodes || [], edges: serverContent.edges || [] })
       const localStr = JSON.stringify({ nodes: localContent.nodes || [], edges: localContent.edges || [] })

       if (serverStr !== localStr) {
          // CONFLICT DETECTED
          conflictData.local = { 
             nodes: localContent.nodes || [], 
             edges: localContent.edges || [], 
             date: cached.cachedAt || 0 
          }
          conflictData.server = { 
             nodes: serverContent.nodes || [], 
             edges: serverContent.edges || [], 
             date: data.updated_at ? new Date(data.updated_at).getTime() : 0 
          }
          
          showConflictResolver.value = true
          
          // Show Local Data initially while resolving
          nodes.value = normalizeNodes(localContent.nodes || [])
          edges.value = localContent.edges || []
          if (localContent.viewport) setViewport(localContent.viewport)
          triggerRef(nodes)
          initializeTimersForNodes()
          isOfflineMode.value = true // Temporarily mark as offline/local until resolved
          return
       }
    }

    // No conflict, use Server Data
    nodes.value = normalizeNodes(serverContent.nodes || [])
    edges.value = serverContent.edges || []
      
    if (serverContent.viewport) {
      setViewport(serverContent.viewport)
    }
      
    triggerRef(nodes)
    initializeTimersForNodes()
    logAndCommit() 
    isOfflineMode.value = false

    // Reset dirty flag after loading
    await nextTick()
    isDirty.value = false

  } catch (e) {
    console.error(e)
    
    // Fallback to local cache
    const cached = loadFromLocalCache(id)
    if (cached && cached.content) {
      const parsed = cached.content
      nodes.value = normalizeNodes(parsed.nodes || [])
      edges.value = parsed.edges || []
      
      if (parsed.viewport) {
        setViewport(parsed.viewport)
      }
      
      canvasTitle.value = cached.title || '未命名画布'
      
      triggerRef(nodes)
      initializeTimersForNodes()
      logAndCommit()
      
      isOfflineMode.value = true
      // Only show toast if we are really offline (network error) or unauth
      addToast('当前为离线使用，请勿清理浏览器缓存', 'info')
      return
    }
    
    // If no local cache and no server data, and user is not logged in, maybe initialize empty?
    if (!user.value) {
       nodes.value = []
       edges.value = []
       isOfflineMode.value = true
       return
    }

    addToast('加载画布失败', 'error')
  }
}

const handleHistoryRestore = () => {
  addToast('已恢复历史版本', 'success')
  if (currentCanvasId.value) {
    loadCanvas(currentCanvasId.value)
  }
}

const handlePasswordConfirm = async (password: string) => {
  if (pendingCanvasId.value) {
    showPasswordModal.value = false
    await loadCanvas(pendingCanvasId.value, password)
    pendingCanvasId.value = null
  }
}


const nodes = ref<Node[]>([
  {
    id: '1',
    type: 'note',
    position: { x: 250, y: 100 },
    data: { label: '系统介绍', content: '<p>双击空白处新建便签<br>拖拽可连接节点<br>右键菜单可编组、对齐、改色</p>', borderWidth: 1 },
    style: { width: '300px', height: 'auto', minHeight: '120px' },
  },
])

const edges = ref<Edge[]>([])
const vueFlowInstance = ref<VueFlowStore | null>(null)

const onPaneReady = (instance: VueFlowStore) => {
  vueFlowInstance.value = instance
}

// Create a graph computed property that combines nodes and edges
const graph = computed({
  get: () => ({ nodes: nodes.value, edges: edges.value }),
  set: (val) => {
    nodes.value = val.nodes
    edges.value = val.edges
  }
})

// Use manual history mode
const { undo, redo, canUndo, canRedo, commit, history } = useRefHistory(graph, {
  capacity: 20,
  manual: true,
  clone: (val: any) => JSON.parse(JSON.stringify(val))
} as any)

const logAndCommit = () => {
  // Only commit if changed
  if (history.value.length > 0) {
    const lastSnapshot = history.value[0].snapshot
    const currentSnapshot = JSON.parse(JSON.stringify(graph.value))
    if (JSON.stringify(lastSnapshot) === JSON.stringify(currentSnapshot)) {
      return
    }
  }
  commit()
}

// Initial commit
commit()

// Provide commit function to children
provide('saveHistory', logAndCommit)

const previewNodeId = ref<string | null>(null)
const isPreviewFullscreen = ref(false)
const showTableOfContents = ref(true)
const previewContainerRef = ref<HTMLElement | null>(null)
const previewNode = computed(() => nodes.value.find(n => n.id === previewNodeId.value))

const showDrawingModal = ref(false)
const showMediaModal = ref(false)
const currentMediaType = ref<'image' | 'video' | 'audio' | 'file'>('image')
const showLinkModal = ref(false)
const showCardModal = ref(false)
const showEChartsModal = ref(false)
const showSearch = ref(false)
const showNodeLinkModal = ref(false)
const linkSourceNodeId = ref<string | null>(null)
const showAuthModal = ref(false)
const showChangePasswordModal = ref(false)
const showTechSupportModal = ref(false)
const showShortcutSettingsModal = ref(false)
const showConfirmModal = ref(false)
const confirmModalMessage = ref('')
const confirmModalCheckboxLabel = ref<string | null>(null)
const confirmModalCheckboxDefaultChecked = ref(false)
const confirmCallback = ref<((checked?: boolean) => void) | null>(null)

const handleConfirm = (checked?: boolean) => {
  confirmCallback.value?.(checked)
  showConfirmModal.value = false
  confirmCallback.value = null
  confirmModalCheckboxLabel.value = null
  confirmModalCheckboxDefaultChecked.value = false
}

const handleCancelConfirm = () => {
  showConfirmModal.value = false
  confirmCallback.value = null
  confirmModalCheckboxLabel.value = null
  confirmModalCheckboxDefaultChecked.value = false
}

const user = ref<{ email: string, token: string, nickname?: string, avatar?: string } | null>(null)
const isEditingTitle = ref(false)
const tempTitle = ref('')
const titleInput = ref<HTMLInputElement | null>(null)

const activeEditorCallback = ref<((data: any) => void) | null>(null)
const mediaCallback = ref<((url: string, name?: string) => void) | null>(null)
const echartsCallback = ref<((data: any) => void) | null>(null)
const echartsInitialData = ref<any>(undefined)
const echartsInitialType = ref<string | undefined>(undefined)
const echartsReadonly = ref(false)

const alarmNotifications = ref<AlarmNotification[]>([])
const closeAlarmNotification = (id: string) => {
  alarmNotifications.value = alarmNotifications.value.filter(n => n.id !== id)
}

const focusNodeById = (id: string) => {
  if (vueFlowInstance.value) {
    vueFlowInstance.value.fitView({ nodes: [id], duration: 800, padding: 0.2 })
  }
  nodes.value = nodes.value.map(n => ({
    ...n,
    selected: n.id === id
  }))
}

const showNodeTimerModal = ref(false)
const activeTimerNodeId = ref<string | null>(null)
const activeTimerNode = computed(() => nodes.value.find(n => n.id === activeTimerNodeId.value) as any)
const activeTimerNodeTimers = computed<NodeTimer[]>({
  get: () => {
    const n: any = activeTimerNode.value
    const timers = n?.data?.timers
    return Array.isArray(timers) ? timers : []
  },
  set: (val) => {
    if (!activeTimerNodeId.value) return
    updateNodeTimers(activeTimerNodeId.value, val)
  }
})

const openNodeTimerManager = (id: string) => {
  activeTimerNodeId.value = id
  showNodeTimerModal.value = true
}

provide('openNodeTimerManager', openNodeTimerManager)

const getMentionUsers = () => {
  const list: any[] = []
  if (user.value) {
    list.push({
      id: user.value.email,
      username: user.value.nickname || user.value.email,
      avatar: user.value.avatar,
      email: user.value.email,
    })
  }
  activeUsers.value.forEach(u => {
    if (!u) return
    list.push({
      id: u.id,
      username: u.username,
      avatar: u.avatar,
      color: u.color,
    })
  })
  const seen = new Set<string>()
  return list.filter(u => {
    const key = (u.id || u.username) as string
    if (!key) return false
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

provide('getMentionUsers', getMentionUsers)

const openTimersForSelection = () => {
  let id: string | null = null
  if (selectedNodes.value.length > 0) id = selectedNodes.value[0].id
  else if (menu.contextNodeId) id = menu.contextNodeId
  if (id) openNodeTimerManager(id)
  closeMenu()
}

type TimerKey = string
const timerTimeouts = new Map<TimerKey, number>()
const MAX_TIMEOUT_MS = 2147483647

const getTimerKey = (nodeId: string, timerId: string) => `${nodeId}:${timerId}`

const clearTimerKey = (key: TimerKey) => {
  const handle = timerTimeouts.get(key)
  if (handle) {
    clearTimeout(handle)
    timerTimeouts.delete(key)
  }
}

const cancelTimersForNode = (nodeId: string) => {
  Array.from(timerTimeouts.keys()).forEach(key => {
    if (key.startsWith(`${nodeId}:`)) clearTimerKey(key)
  })
}

const scheduleAt = (key: TimerKey, targetAt: number, cb: () => void) => {
  const tick = () => {
    const now = Date.now()
    const remaining = targetAt - now
    if (remaining <= 0) {
      cb()
      return
    }
    const step = Math.min(remaining, MAX_TIMEOUT_MS)
    const handle = window.setTimeout(tick, step)
    timerTimeouts.set(key, handle)
  }
  tick()
}

const scheduleNodeTimers = (nodeId: string) => {
  cancelTimersForNode(nodeId)
  const n: any = nodes.value.find(x => x.id === nodeId)
  const timers: NodeTimer[] = Array.isArray(n?.data?.timers) ? n.data.timers : []
  const now = Date.now()

  timers.forEach(t => {
    if (!t || !t.enabled) return
    if (t.mode === 'cron') {
      const expr = t.cron?.trim()
      if (!expr) return
      const fromTs = t.lastRun ? t.lastRun + 1000 : now
      const nextAt = nextCronTimestamp(expr, fromTs)
      if (!nextAt) return
      const key = getTimerKey(nodeId, t.id)
      scheduleAt(key, nextAt, () => fireTimer(nodeId, t.id))
      return
    }

    if (!t.nextTriggerAt || Number.isNaN(t.nextTriggerAt)) return

    if (t.mode !== 'interval' && t.nextTriggerAt <= now) return

    if (t.mode === 'interval' && t.intervalMs) {
      let nextAt = t.nextTriggerAt
      if (!nextAt) nextAt = now + t.intervalMs
      while (nextAt <= now) nextAt += t.intervalMs
      t.nextTriggerAt = nextAt
    }

    const key = getTimerKey(nodeId, t.id)
    scheduleAt(key, t.nextTriggerAt, () => fireTimer(nodeId, t.id))
  })
}

const initializeTimersForNodes = () => {
  nodes.value.forEach(n => scheduleNodeTimers(n.id))
}

const updateNodeTimers = (nodeId: string, timers: NodeTimer[]) => {
  nodes.value = nodes.value.map(n => {
    if (n.id !== nodeId) return n
    return {
      ...n,
      data: {
        ...(n as any).data,
        timers
      }
    } as any
  })
  scheduleNodeTimers(nodeId)
  logAndCommit()
}

const fireTimer = (nodeId: string, timerId: string) => {
  const nodeIndex = nodes.value.findIndex(n => n.id === nodeId)
  if (nodeIndex === -1) return

  const n: any = nodes.value[nodeIndex]
  const timers: NodeTimer[] = Array.isArray(n.data?.timers) ? n.data.timers : []
  const idx = timers.findIndex(t => t.id === timerId)
  if (idx === -1) return

  const t = { ...timers[idx] }
  const now = Date.now()
  if (t.lastRun && now - t.lastRun < 500) {
    return
  }
  t.lastRun = now

  alarmNotifications.value = [
    {
      id: crypto.randomUUID(),
      nodeId,
      title: n.data?.label || '节点提醒',
      message: t.title || '定时提醒',
      triggeredAt: now,
    },
    ...alarmNotifications.value
  ]

  try {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(n.data?.label || '节点提醒', {
          body: t.title || '定时提醒',
          icon: '/favicon.ico',
        })
      } else if (Notification.permission === 'default') {
        Notification.requestPermission().then(p => {
          if (p === 'granted') {
            new Notification(n.data?.label || '节点提醒', {
              body: t.title || '定时提醒',
              icon: '/favicon.ico',
            })
          }
        })
      }
    }
  } catch {}

  if (t.mode === 'interval') {
    if (t.autoClose) {
      t.enabled = false
    } else if (t.intervalMs) {
      t.nextTriggerAt = now + t.intervalMs
    } else {
      t.enabled = false
    }
  } else if (t.mode === 'cron') {
    if (t.autoClose) {
      t.enabled = false
    } else {
      const expr = t.cron?.trim()
      if (!expr) {
        t.enabled = false
      } else {
        const nextAt = nextCronTimestamp(expr, now + 1000)
        if (!nextAt) {
          t.enabled = false
        } else {
          t.nextTriggerAt = nextAt
        }
      }
    }
  } else {
    t.enabled = false
  }

  const nextTimers = timers.map((x, i) => (i === idx ? t : x))
  updateNodeTimers(nodeId, nextTimers)
}

const checkAuth = async () => {
  const token = localStorage.getItem('token')
  const email = localStorage.getItem('email')
  if (token && email) {
    user.value = { token, email }
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        user.value = { ...user.value, nickname: data.nickname, avatar: data.avatar }
      }
    } catch (e) {
      console.error('Failed to fetch profile', e)
    }
  }
}

const handleUserUpdate = (u: any) => {
  if (user.value) {
    user.value = { ...user.value, ...u }
    if (currentCanvasId.value) {
       joinCanvasRoom(currentCanvasId.value)
    }
  }
}

const startEditingTitle = () => {
  if (isReadOnly.value) return
  tempTitle.value = canvasTitle.value
  isEditingTitle.value = true
  nextTick(() => {
    titleInput.value?.focus()
  })
}

const saveTitle = async () => {
  if (!isEditingTitle.value) return
  isEditingTitle.value = false
  if (tempTitle.value.trim() && tempTitle.value !== canvasTitle.value) {
    canvasTitle.value = tempTitle.value
    if (currentCanvasId.value) {
        try {
            await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${currentCanvasId.value}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.value?.token}`
                },
                body: JSON.stringify({
                    title: canvasTitle.value,
                    socket_id: socket.value?.id
                })
            })
        } catch (e) {
            console.error('Failed to save title', e)
        }
    }
  }
}

const handleLoginSuccess = (data: { token: string, email: string, nickname?: string, avatar?: string }) => {
  user.value = data
  localStorage.setItem('token', data.token)
  localStorage.setItem('email', data.email)
  loadFromServer()
  initSocket()
}

const logout = () => {
  user.value = null
  localStorage.removeItem('token')
  localStorage.removeItem('email')
  nodes.value = [] // Clear canvas on logout? Or keep it? Let's keep it or maybe clear. User might expect clear.
  // Actually, let's just clear for safety.
  nodes.value = []
  edges.value = []
}

const handleChangePassword = () => {
  showChangePasswordModal.value = true
}

import { useToast } from '../composables/useToast'

const { addToast } = useToast()
const { viewport, setViewport } = useVueFlow()

const fileInput = ref<HTMLInputElement | null>(null)

const handleExportData = () => {
  const data = {
    title: canvasTitle.value || 'Untitled',
    nodes: nodes.value,
    edges: edges.value,
    viewport: viewport.value,
    version: '1.0.0',
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${data.title}-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  addToast('数据导出成功', 'success')
}

const handleImportData = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
    fileInput.value.click()
  }
}

const onFileSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  
  const file = input.files[0]
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    
    if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
      throw new Error('无效的数据格式')
    }
    
    confirmModalMessage.value = '导入数据将覆盖当前画布内容，是否继续？'
    confirmCallback.value = () => {
        nodes.value = data.nodes
        edges.value = data.edges
        if (data.viewport) {
            setViewport(data.viewport)
        }
        if (data.title) {
            canvasTitle.value = data.title
            // tempTitle.value = data.title 
        }
        
        // Trigger save
        saveToServer()
        addToast('数据导入成功', 'success')
    }
    showConfirmModal.value = true
    
  } catch (error) {
    addToast('导入失败: ' + (error as Error).message, 'error')
  }
}

import pako from 'pako'

const saveToServer = async (silent: boolean = false) => {
  if (isSharedView.value && isReadOnly.value) {
    if (!silent) addToast('只读分享无法保存', 'info')
    return
  }
  
  const contentObj = { 
    nodes: nodes.value, 
    edges: edges.value,
    viewport: viewport.value 
  }
  
  const jsonString = JSON.stringify(contentObj)
  
  // Compress if larger than 1KB
  let body: any = { 
    content: jsonString,
    socket_id: socket.value?.id 
  }
  
  // Optional: Client-side compression before sending?
  // Flask default JSON handling doesn't support automatic decompression of request body easily without middleware.
  // For now, let's keep sending JSON string, but enable gzip on server response and socket.io
  // If we really want to compress UPSTREAM, we need to send binary/blob and handle it in Flask.
  // Given user request "can we use compression", enabling server-side compression (gzip response) and socketio compression is step 1.
  // Step 2 is client-side compression for upload.
  
  // Let's implement client-side compression for large payloads
  if (jsonString.length > 1024) {
     const compressed = pako.gzip(jsonString)
     // We need to send this as blob or base64? Base64 is easier for JSON API but adds 33% overhead.
     // Blob is better but requires multipart/form-data or raw body.
     // Let's use a custom field 'compressed_content' (base64) for simplicity in existing JSON API
     // Convert Uint8Array to binary string then btoa
     let binary = ''
     const len = compressed.byteLength
     for (let i = 0; i < len; i++) {
         binary += String.fromCharCode(compressed[i])
     }
     const base64 = btoa(binary)
     
     body = {
        compressed_content: base64,
        socket_id: socket.value?.id
     }
  }

  let url = ''
  let method = 'POST'
  let headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  
  if (user.value) {
    headers['Authorization'] = `Bearer ${user.value.token}`
  }

  // Cache First Strategy (Always save locally)
  if (currentCanvasId.value) {
    saveToLocalCache(currentCanvasId.value, {
      content: { nodes: nodes.value, edges: edges.value, viewport: viewport.value },
      title: canvasTitle.value
    })
    isDirty.value = false // 本地保存也视为已保存（离线模式下）
  }

  // If offline/guest and not in shared view, stop here
  if (!user.value && !currentShareId.value) {
    isOfflineMode.value = true
    return
  }

  // Network Check & Conflict Detection (Offline -> Online)
  if (isOfflineMode.value && user.value && !isCheckingConflict.value && currentCanvasId.value) {
     const isOnline = await checkConnectivity()
     if (!isOnline) {
        if (!silent) addToast('离线保存，请勿清理浏览器缓存', 'info')
        return 
     }
     
     // Online detected! Check for server changes
     isCheckingConflict.value = true
     try {
        if (debouncedSaveTimer) clearTimeout(debouncedSaveTimer) // Pause auto-save
        
        // Fetch server data
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases/${currentCanvasId.value}`, {
            headers: { 'Authorization': `Bearer ${user.value.token}` }
        })
        
        if (res.ok) {
            const data = await res.json()
            let serverContent = { nodes: [] as any[], edges: [] as any[] }
            if (data.content) {
                serverContent = typeof data.content === 'string' ? JSON.parse(data.content) : data.content
            }
            
            // Compare
            const serverStr = JSON.stringify({ nodes: serverContent.nodes || [], edges: serverContent.edges || [] })
            const localStr = JSON.stringify({ nodes: nodes.value, edges: edges.value })
            
            if (serverStr !== localStr) {
                // Conflict!
                conflictData.local = { 
                    nodes: nodes.value, 
                    edges: edges.value, 
                    date: Date.now() 
                }
                conflictData.server = { 
                    nodes: serverContent.nodes || [], 
                    edges: serverContent.edges || [], 
                    date: data.updated_at ? new Date(data.updated_at).getTime() : 0 
                }
                showConflictResolver.value = true
                isCheckingConflict.value = false
                addToast('检测到云端数据更新，请解决冲突', 'info')
                return // STOP SAVE
            }
        }
     } catch(e) {
        console.error('Conflict check failed', e)
     } finally {
        isCheckingConflict.value = false
     }
     // No conflict, proceed to save (and mark online)
     isOfflineMode.value = false
  }

  // Handle Share View Save
  if (currentShareId.value) {
    url = `${import.meta.env.VITE_API_BASE_URL}/api/shares/${currentShareId.value}`
    method = 'PUT'
    if (sharePassword.value) {
      headers['X-Share-Password'] = sharePassword.value
    }
  } else if (currentCanvasId.value) {
    url = `${import.meta.env.VITE_API_BASE_URL}/api/canvases/${currentCanvasId.value}`
    method = 'PUT'
  } else {
    url = `${import.meta.env.VITE_API_BASE_URL}/api/canvas`
  }
  
  try {
    const res = await fetch(url, {
      method,
      headers,
      body: JSON.stringify(body)
    })
    
    if (res.status === 401) {
      if (user.value) logout()
      throw new Error('Unauthorized')
    }

    if (res.status === 404 && method === 'PUT' && user.value) {
      // Canvas doesn't exist on server (e.g. created offline). Create it now.
      const createRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases`, {
         method: 'POST',
         headers,
         body: JSON.stringify({ 
           title: canvasTitle.value,
           content: contentObj, // Body expects object, not string
           socket_id: socket.value?.id
         })
      })
      
      if (createRes.ok) {
         const newData = await createRes.json()
         currentCanvasId.value = newData.id
         localStorage.setItem('lastCanvasId', newData.id)
         // Update cache with new ID
         saveToLocalCache(newData.id, {
            content: { nodes: nodes.value, edges: edges.value, viewport: viewport.value },
            title: canvasTitle.value
         })
         
         isOfflineMode.value = false
         if (!silent) addToast('已同步到服务器 (新创建)', 'success')
         return
      }
    }
    
    if (!res.ok) throw new Error('Save failed')
    
    isDirty.value = false // 保存成功后重置脏状态
    isOfflineMode.value = false
    if (!silent) {
      addToast('保存到服务器成功', 'success')
    }
  } catch (e) {
    console.error(e)
    isOfflineMode.value = true
    if (!silent) {
      addToast('离线保存，请勿清理浏览器缓存', 'info')
    }
  }
}


const isDirty = ref(false)

const debouncedSave = () => {
  if (debouncedSaveTimer) clearTimeout(debouncedSaveTimer)
  debouncedSaveTimer = setTimeout(() => {
    if (isDirty.value) {
      saveToServer(true)
    }
  }, 2000)
}

// 监听 Vue Flow 的变化事件来标记脏状态，而不是深度监听整个对象
const { onNodesChange, onEdgesChange, onConnect: onVueFlowConnectInternal, onNodeDragStop: onNodeDragStopInternal } = useVueFlow()

// 保留这些监听，但是使用 handleContentChange
onVueFlowConnectInternal(() => {
  handleContentChange()
})

onNodeDragStopInternal(() => {
  handleContentChange()
})

// 新逻辑：
// 我们需要一个方法来处理变更广播和保存触发
const handleContentChange = () => {
  if (isRemoteUpdate.value) return
  
  isDirty.value = true
  
  if (currentCanvasId.value && socket.value) {
    socket.value.emit('update_canvas', {
      canvas_id: currentCanvasId.value,
      content: JSON.stringify({ nodes: nodes.value, edges: edges.value })
    })
  }
  
  debouncedSave()
}

// 由于 Vue Flow 的 onNodesChange 等事件可能在远程更新时也会触发（如果我们在远程更新逻辑中直接修改了 nodes），
// 我们需要确保 isRemoteUpdate 标志在远程更新期间是 true。
// 查看 loadCanvas 和 socket.on('canvas_updated') 逻辑，isRemoteUpdate 确实被使用了。

// 重新绑定变更监听
onNodesChange((changes) => {
  if (changes.length === 0) return
  handleContentChange()
})

onEdgesChange((changes) => {
  if (changes.length === 0) return
  handleContentChange()
})

provide('markDirty', () => {
  handleContentChange()
})

provide('openNodeLinkModal', (sourceNodeId: string) => {
  if (isReadOnly.value) return
  linkSourceNodeId.value = sourceNodeId
  showNodeLinkModal.value = true
})

// 还需要监听 nodes/edges 的直接替换（例如导入数据）
watch([nodes, edges], (newVals, oldVals) => {
  // 如果是引用变化（替换了整个数组），肯定需要保存
  if (newVals[0] !== oldVals[0] || newVals[1] !== oldVals[1]) {
     handleContentChange()
  }
  // 注意：这里没有 deep: true，所以只有数组引用变化或长度变化（对于 reactive 数组）才触发
})

const loadFromServer = async () => {
  if (!user.value) return
  
  try {
    // First try to get the list of canvases to find the last active one
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvases`, {
      headers: { 
        'Authorization': `Bearer ${user.value.token}`
      }
    })
    
    if (res.status === 401) {
      logout()
      return
    }
    
    if (res.ok) {
      const data = await res.json()
      if (data.canvases && data.canvases.length > 0) {
        // Load the most recent one
        const lastCanvas = data.canvases[0]
        currentCanvasId.value = lastCanvas.id
        localStorage.setItem('lastCanvasId', lastCanvas.id)
        await loadCanvas(lastCanvas.id)
        return
      }
    }
    
    // Fallback for legacy or empty: try legacy endpoint
    const legacyRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/canvas`, {
      headers: { 
        'Authorization': `Bearer ${user.value.token}`
      }
    })
    
    if (legacyRes.ok) {
      const data = await legacyRes.json()
      if (data.content) {
         const parsed = typeof data.content === 'string' ? JSON.parse(data.content) : data.content
         nodes.value = parsed.nodes || []
         edges.value = parsed.edges || []
         if (parsed.viewport) setViewport(parsed.viewport)
         triggerRef(nodes)
         initializeTimersForNodes()
         logAndCommit()
      }
    }
  } catch (e) {
    console.error(e)
    // Offline Fallback: Try last active canvas
    const lastId = localStorage.getItem('lastCanvasId')
    if (lastId) {
      currentCanvasId.value = lastId
      await loadCanvas(lastId)
    }
  }
}

provide('saveData', () => saveToServer(true))

const openDrawingModal = (callback: (dataUrl: string) => void) => {
  activeEditorCallback.value = callback
  showDrawingModal.value = true
}

let autoSaveTimer: ReturnType<typeof setInterval> | null = null

const startAutoSave = () => {
  if (autoSaveTimer) clearInterval(autoSaveTimer)
  autoSaveTimer = setInterval(() => {
    // Only save if dirty and user is logged in
    if (user.value && isDirty.value) {
      saveToServer(true)
    }
  }, 60000) // 1 minute
}

const stopAutoSave = () => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }
}

watch(user, (newUser) => {
  if (newUser) {
    startAutoSave()
  } else {
    stopAutoSave()
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
    }
    initSocket()
  }
})

const loadSharedContent = async (shareId: string, password?: string) => {
  try {
    const headers: Record<string, string> = {}
    if (password) {
      headers['X-Share-Password'] = password
    }

    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/shares/${shareId}`, {
      headers
    })
    
    if (res.status === 403) {
      const data = await res.json()
      if (data.requires_password) {
        const pwd = prompt('该分享已加密，请输入密码：')
        if (pwd) {
          await loadSharedContent(shareId, pwd)
          return
        }
      }
      addToast(data.message || '无权访问', 'error')
      return
    }

    if (!res.ok) throw new Error('Load failed')
    
    const data = await res.json()
    canvasTitle.value = "分享内容"
    currentShareId.value = shareId
    if (password) sharePassword.value = password
    
    // We set currentCanvasId to allow WebSocket updates, but we should be careful about saving.
    // Ideally we disable saving back to server if we are in share view unless we have edit permission.
    // For now, let's set it.
    currentCanvasId.value = data.canvas_id 
    
    if (data.content) {
      const parsed = typeof data.content === 'string' ? JSON.parse(data.content) : data.content
      const loadedNodes = parsed.nodes || []
      
      // Update read-only state based on permission
      isReadOnly.value = !data.allow_guest_edit

      // Inject editable prop into node data
      nodes.value = loadedNodes.map((n: any) => ({
        ...n,
        data: {
          ...n.data,
          editable: !isReadOnly.value
        }
      }))
      
      edges.value = parsed.edges || []
      
      if (parsed.viewport) {
        setViewport(parsed.viewport)
      }
      
      triggerRef(nodes)
      initializeTimersForNodes()
    }
    
    isSharedView.value = true
    
    // Disable socket room joining for shared view to prevent full canvas updates
    // if (data.canvas_id) {
    //    joinCanvasRoom(data.canvas_id)
    // }

  } catch (e) {
    console.error(e)
    addToast('加载分享内容失败', 'error')
  }
}

const openShareForSelection = () => {
  if (selectedNodes.value.length > 0) {
    preSelectedNodeIds.value = selectedNodes.value.map(n => n.id)
  } else if (menu.contextNodeId) {
    preSelectedNodeIds.value = [menu.contextNodeId]
  } else {
    preSelectedNodeIds.value = []
  }
  showNodeShareModal.value = true
  closeMenu()
}

const openHelp = () => {
  window.open('https://icanvas.fengxiaozi.net/?shareId=6b10400d-51b9-46f7-8b6c-97975ed90966', '_blank')
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown, { capture: true })
  window.addEventListener('keyup', onKeyUp, { capture: true })
  checkAuth()

  const urlParams = new URLSearchParams(window.location.search)
  const sharedCanvasId = urlParams.get('canvasId')
  const shareId = urlParams.get('shareId')

  if (shareId) {
    loadSharedContent(shareId)
  } else if (sharedCanvasId) {
    currentCanvasId.value = sharedCanvasId
    loadCanvas(sharedCanvasId).then(() => {
      initSocket()
    })
    if (user.value) startAutoSave()
  } else if (user.value) {
    loadFromServer().then(() => {
      initSocket()
    })
    startAutoSave()
  } else {
    // Offline / Guest Startup
    const lastId = localStorage.getItem('lastCanvasId')
    if (lastId) {
       currentCanvasId.value = lastId
       loadCanvas(lastId)
    } else {
       // New Local Canvas
       const newId = uuidv4()
       currentCanvasId.value = newId
       localStorage.setItem('lastCanvasId', newId)
       
       saveToLocalCache(newId, {
         content: { nodes: nodes.value, edges: edges.value, viewport: viewport.value },
         title: '未命名画布'
       })
       isOfflineMode.value = true
       addToast('离线模式：数据仅保存在本地', 'info')
    }
    initSocket()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown, { capture: true })
  window.removeEventListener('keyup', onKeyUp, { capture: true })
  stopAutoSave()
  if (socket.value) socket.value.disconnect()
})

const openMediaModal = (type: 'image' | 'video' | 'audio' | 'file', callback: (url: string, name?: string) => void) => {
  currentMediaType.value = type
  mediaCallback.value = callback
  showMediaModal.value = true
}

const handleDrawingSave = (dataUrl: string) => {
  if (activeEditorCallback.value) {
    activeEditorCallback.value(dataUrl)
  }
  showDrawingModal.value = false
}

const handleMediaSave = (data: string | { url: string, name?: string }) => {
  if (mediaCallback.value) {
    const url = typeof data === 'string' ? data : data.url
    const name = typeof data === 'string' ? undefined : data.name
    mediaCallback.value(url, name)
  }
  showMediaModal.value = false
}

const openLinkModal = (callback: (data: { url: string, text: string }) => void) => {
  activeEditorCallback.value = callback
  showLinkModal.value = true
}

const openWebsiteCardModal = (callback: (url: string) => void) => {
  activeEditorCallback.value = callback
  showCardModal.value = true
}

const handleLinkSave = (data: { url: string, text: string }) => {
  if (activeEditorCallback.value) {
    activeEditorCallback.value(data)
  }
  showLinkModal.value = false
}

const handleCardSave = (data: string | any) => {
  if (activeEditorCallback.value) {
    activeEditorCallback.value(data)
  }
  showCardModal.value = false
  activeEditorCallback.value = null
  logAndCommit()
}

const handleEChartsSave = (data: any) => {
  if (echartsCallback.value) {
    echartsCallback.value(data)
  }
  showEChartsModal.value = false
  echartsCallback.value = null
  echartsInitialData.value = undefined
  logAndCommit()
}

const handleSearchResult = (item: any) => {
  if (vueFlowInstance.value) {
    vueFlowInstance.value.fitView({ nodes: [item.id], duration: 800, padding: 0.2 })
  }
  
  // Update selection
  nodes.value = nodes.value.map(n => ({
    ...n,
    selected: n.id === item.id
  }))
}

const openEChartsModal = (callback: (data: any) => void, initialData?: any, type?: string) => {
  echartsCallback.value = callback
  echartsInitialData.value = initialData
  echartsInitialType.value = type
  echartsReadonly.value = false
  showEChartsModal.value = true
}

const maximizeChart = (option: any) => {
  echartsInitialData.value = { option, dataSourceType: 'static', dataUrl: '' } // Assuming option contains data
  echartsReadonly.value = true
  showEChartsModal.value = true
}

provide('openDrawingModal', openDrawingModal)
provide('openMediaModal', openMediaModal)
provide('openLinkModal', openLinkModal)
provide('openWebsiteCardModal', openWebsiteCardModal)
provide('openEChartsModal', openEChartsModal)
provide('maximizeChart', maximizeChart)

const openPreview = (id: string) => {
  previewNodeId.value = id
  isPreviewFullscreen.value = false
}

const closePreview = () => {
  previewNodeId.value = null
  isPreviewFullscreen.value = false
  logAndCommit()
}

provide('openPreview', openPreview)

const nodeTypes = {
  note: markRaw(NoteNode),
  group: markRaw(GroupNode),
}

const { project, getSelectedNodes, getSelectedEdges, onNodeDragStop, onConnect: onVueFlowConnect, getNodes } = useVueFlow()

const menu = reactive({
  visible: false,
  x: 0,
  y: 0,
  type: 'pane' as 'pane' | 'node' | 'selection',
  contextNodeId: null as string | null
})

const colors = ['#ffffff', '#ffedd5', '#dcfce7', '#dbeafe', '#f3e8ff', '#fee2e2']
const currentFontSize = ref(16)
const currentFontColor = ref('#000000')

const selectedNodes = computed(() => getSelectedNodes.value)

// 监听选中节点变化，高亮相关连线
// 优化：仅在选中状态真正改变时才触发样式更新，避免不必要的遍历
// Vue Flow 已经处理了选择逻辑，我们只需要响应选择集的变化
watch(selectedNodes, (newSelected, oldSelected) => {
  // 如果选中集合没有变化（例如只是内部属性变化），则跳过
  // 注意：selectedNodes 是 computed，每次依赖变化都会重新计算
  // 这里我们假设 getSelectedNodes 返回的是新的数组引用
  
  // 快速检查：如果新旧都为空，无需操作
  if (newSelected.length === 0 && (!oldSelected || oldSelected.length === 0)) return

  const selectedIds = new Set(newSelected.map(n => n.id))
  
  // 只有当边的状态需要改变时才更新 edges
  let hasChanges = false
  
  const newEdges = edges.value.map(edge => {
    const isConnected = selectedIds.has(edge.source) || selectedIds.has(edge.target)
    const isHighlighted = edge.data?.isHighlighted
    
    if (selectedIds.size > 0 && isConnected) {
      if (isHighlighted) return edge // 已经是高亮状态，无需更新
      
      hasChanges = true
      // 保存原始样式
      const originalStyle = edge.style || {}
      const originalAnimated = edge.animated || false
      const originalLabelStyle = edge.labelStyle || {}
      const originalZIndex = edge.zIndex
      
      return {
        ...edge,
        animated: true,
        style: { 
          ...(typeof originalStyle === 'object' ? originalStyle : {}), 
          stroke: '#3b82f6', // blue-500
          strokeWidth: 2,
          opacity: 1
        },
        labelStyle: {
          ...(typeof originalLabelStyle === 'object' ? originalLabelStyle : {}),
          fill: '#3b82f6',
          fontWeight: 700
        },
        zIndex: 10, // 提升层级
        data: {
          ...edge.data,
          isHighlighted: true,
          originalStyle,
          originalAnimated,
          originalLabelStyle,
          originalZIndex
        }
      }
    } else {
      if (!isHighlighted) return edge // 已经是普通状态，无需更新
      
      hasChanges = true
      // 恢复原始样式
      const { originalStyle, originalAnimated, originalLabelStyle, originalZIndex, ...restData } = edge.data || {}
      
      return {
        ...edge,
        animated: originalAnimated,
        style: originalStyle,
        labelStyle: originalLabelStyle,
        zIndex: originalZIndex,
        data: {
          ...restData,
          isHighlighted: false
        }
      }
    }
  })
  
  if (hasChanges) {
     edges.value = newEdges
  }
}, { deep: false }) // 关闭 deep watch，只监听数组引用变化

const closeMenu = () => {
  menu.visible = false
}

const onPaneDblClick = (event: any) => {
  if (isReadOnly.value) return
  const e = event.event
  let clientX = 0
  let clientY = 0
  
  if ('clientX' in e) {
    const mouseEvent = e as MouseEvent
    clientX = mouseEvent.clientX
    clientY = mouseEvent.clientY
  } else {
    const touchEvent = e as TouchEvent
    clientX = touchEvent.touches?.[0]?.clientX || 0
    clientY = touchEvent.touches?.[0]?.clientY || 0
  }
  
  createNoteAt(clientX, clientY)
}

const onConnect = (params: Connection) => {
  edges.value = addEdge(params, edges.value) as Edge[]
  logAndCommit()
}

// Hook into Vue Flow events
onNodeDragStop(({ nodes: draggedNodes }) => {
  const allNodes = getNodes.value
  const groups = allNodes.filter(n => n.type === 'group')
  let hasChanges = false
  const newNodes = [...nodes.value] // Create a copy for batch update

  draggedNodes.forEach(draggedNode => {
    // Find the reactive node in our state
    const stateNodeIndex = newNodes.findIndex(n => n.id === draggedNode.id)
    if (stateNodeIndex === -1) return
    
    const stateNode = newNodes[stateNodeIndex]
    const nowIso = new Date().toISOString()
    
    // Get absolute position and dimensions
    // Note: GraphNode has positionAbsolute, dimensions
    const nodeAny = draggedNode as any
    const absPos = nodeAny.positionAbsolute || nodeAny.computedPosition || draggedNode.position
    const width = draggedNode.dimensions?.width || 0
    const height = draggedNode.dimensions?.height || 0
    
    // Calculate center point of the dragged node
    const centerX = absPos.x + width / 2
    const centerY = absPos.y + height / 2
    
    let targetGroup = null
    
    // Find a group that contains the node center
    // We iterate all groups to find the best match (e.g. smallest one or top one)
    // For simplicity, we use the last one found in the list (usually rendered on top)
    for (const group of groups) {
      if (group.id === draggedNode.id) continue // Cannot group into itself
      
      const groupAny = group as any
      const gAbsPos = groupAny.positionAbsolute || groupAny.computedPosition || group.position
      const gW = group.dimensions?.width || 0
      const gH = group.dimensions?.height || 0
      
      if (
        centerX >= gAbsPos.x &&
        centerX <= gAbsPos.x + gW &&
        centerY >= gAbsPos.y &&
        centerY <= gAbsPos.y + gH
      ) {
        targetGroup = group
      }
    }
    
    if (targetGroup) {
      // Enter group
      if (stateNode.parentNode !== targetGroup.id) {
        const targetGroupAny = targetGroup as any
        const gAbsPos = targetGroupAny.positionAbsolute || targetGroupAny.computedPosition || targetGroup.position
        
        // Update state
        newNodes[stateNodeIndex] = {
          ...stateNode,
          parentNode: targetGroup.id,
          // Convert absolute position to relative position
          position: {
            x: absPos.x - gAbsPos.x,
            y: absPos.y - gAbsPos.y
          },
          data: {
            ...(stateNode as any).data,
            createdAt: (stateNode as any).data?.createdAt || nowIso,
            updatedAt: nowIso,
          },
        }
        hasChanges = true
      }
    } else {
      // Leave group
      if (stateNode.parentNode) {
        // Update state
        newNodes[stateNodeIndex] = {
          ...stateNode,
          parentNode: undefined,
          // Convert to absolute position (which is just global position now)
          position: {
            x: absPos.x,
            y: absPos.y
          },
          data: {
            ...(stateNode as any).data,
            createdAt: (stateNode as any).data?.createdAt || nowIso,
            updatedAt: nowIso,
          },
        }
        hasChanges = true
      }
    }
  })
  
  if (hasChanges) {
    nodes.value = newNodes // Trigger reactivity
    logAndCommit()
  } else {
    // Even if no parent change, position might have changed, so we should log
    logAndCommit()
  }
})

onVueFlowConnect(() => {
  // onConnect is already handling logic, but Vue Flow might emit its own event too.
  // We use our @connect handler in template which calls onConnect above.
  // So this might be redundant if we only rely on @connect.
  // But dragging edge to connect emits connect event.
})

const duplicateNodes = () => {
  if (isReadOnly.value) return
  
  const selected = getSelectedNodes.value
  if (selected.length === 0) return

  // 1. Identify all nodes to clone (selected + descendants)
  const nodesToClone = new Map<string, Node>()
  const allNodesValue = getNodes.value
  
  const addNodeAndDescendants = (node: Node) => {
    if (nodesToClone.has(node.id)) return
    nodesToClone.set(node.id, node)
    
    if (node.type === 'group') {
      const children = allNodesValue.filter(n => n.parentNode === node.id)
      children.forEach(addNodeAndDescendants)
    }
  }
  
  selected.forEach(addNodeAndDescendants)
  
  // 2. Prepare for cloning
  const idMap = new Map<string, string>()
  const newNodes: Node[] = []
  
  // Generate IDs first to ensure parent mapping works
  nodesToClone.forEach((node) => {
    idMap.set(node.id, uuidv4())
  })
  
  // 3. Create clones
  nodesToClone.forEach((node) => {
    const nowIso = new Date().toISOString()
    const newId = idMap.get(node.id)!
    const isParentCloned = node.parentNode && idMap.has(node.parentNode)
    
    const newPosition = isParentCloned 
      ? { ...node.position } // Keep relative pos
      : { x: node.position.x + 20, y: node.position.y + 20 } // Offset root
      
    const newParentId = isParentCloned ? idMap.get(node.parentNode!) : node.parentNode
    
    // Deep clone data
    const newData = JSON.parse(JSON.stringify(node.data))
    newData.createdAt = nowIso
    newData.updatedAt = nowIso
    
    newNodes.push({
      ...node,
      id: newId,
      position: newPosition,
      parentNode: newParentId,
      data: newData,
      selected: true // Select new nodes
    } as any)
  })
  
  // Deselect old nodes
  selected.forEach(n => (n as any).selected = false)
  
  // Add new nodes
  nodes.value = [...nodes.value, ...newNodes]
  closeMenu()
  logAndCommit()
}

const onPaneContextMenu = (event: MouseEvent) => {
  if (isReadOnly.value) return
  event.preventDefault()
  menu.visible = true
  menu.x = event.clientX
  menu.y = event.clientY
  menu.type = 'pane'
  menu.contextNodeId = null
}

const onSelectionContextMenu = (selectionEvent: { event: MouseEvent, nodes: any[] }) => {
  if (isReadOnly.value) return
  selectionEvent.event.preventDefault()
  menu.visible = true
  menu.x = selectionEvent.event.clientX
  menu.y = selectionEvent.event.clientY
  menu.type = 'selection'
  menu.contextNodeId = selectionEvent.nodes?.[0]?.id || null
}

const onNodeContextMenu = (event: NodeMouseEvent) => {
  if (isReadOnly.value) return
  event.event.preventDefault()
  menu.visible = true
  
  // Handle MouseEvent or TouchEvent
  const e = event.event
  let clientX = 0
  let clientY = 0
  
  if ('clientX' in e) {
    const mouseEvent = e as MouseEvent
    clientX = mouseEvent.clientX
    clientY = mouseEvent.clientY
  } else {
    const touchEvent = e as TouchEvent
    clientX = touchEvent.touches?.[0]?.clientX || 0
    clientY = touchEvent.touches?.[0]?.clientY || 0
  }

  menu.x = clientX
  menu.y = clientY
  
  // Check if we are right clicking on a selection or a single node
  if (selectedNodes.value.length > 1 && selectedNodes.value.find(n => n.id === event.node.id)) {
     menu.type = 'selection'
  } else {
     menu.type = 'node'
     // Initialize controls from node data
     currentFontSize.value = event.node.data.fontSize || 16
     currentFontColor.value = event.node.data.fontColor || '#000000'
  }
  menu.contextNodeId = event.node.id
}

const connectSelectedNodes = () => {
  if (isReadOnly.value) return
  const selected = getSelectedNodes.value
  if (selected.length < 2) return

  const sorted = [...selected].sort((a: any, b: any) => {
    const ay = a.position?.y ?? 0
    const by = b.position?.y ?? 0
    if (ay !== by) return ay - by
    const ax = a.position?.x ?? 0
    const bx = b.position?.x ?? 0
    return ax - bx
  })

  const existing = new Set<string>()
  edges.value.forEach((e: any) => {
    if (!e?.source || !e?.target) return
    existing.add(`${e.source}→${e.target}`)
  })

  const newEdges: Edge[] = []
  for (let i = 0; i < sorted.length - 1; i++) {
    const source = sorted[i].id
    const target = sorted[i + 1].id
    if (!source || !target) continue
    const key = `${source}→${target}`
    if (existing.has(key)) continue
    existing.add(key)
    newEdges.push({ id: uuidv4(), source, target } as any)
  }

  if (newEdges.length === 0) return
  edges.value = [...edges.value, ...newEdges]
  logAndCommit()
}

const handleNodeLinkConfirm = (targetNodeIds: string[]) => {
  const sourceId = linkSourceNodeId.value
  if (!sourceId) {
    showNodeLinkModal.value = false
    return
  }

  const existing = new Set<string>()
  edges.value.forEach((e: any) => {
    if (!e?.source || !e?.target) return
    existing.add(`${e.source}→${e.target}`)
  })

  const newEdges: Edge[] = []
  targetNodeIds.forEach(targetId => {
    if (!targetId) return
    if (targetId === sourceId) return
    const key = `${sourceId}→${targetId}`
    if (existing.has(key)) return
    existing.add(key)
    newEdges.push({ id: uuidv4(), source: sourceId, target: targetId } as any)
  })

  if (newEdges.length > 0) {
    edges.value = [...edges.value, ...newEdges]
    logAndCommit()
  }

  showNodeLinkModal.value = false
}

// Actions
const setNodeColor = (color: string) => {
  if (menu.contextNodeId) {
    const nowIso = new Date().toISOString()
    if (menu.type === 'selection') {
      selectedNodes.value.forEach(node => {
        node.data.backgroundColor = color
        if (!node.data.createdAt) node.data.createdAt = nowIso
        node.data.updatedAt = nowIso
      })
    } else {
      const node = nodes.value.find(n => n.id === menu.contextNodeId)
      if (node) {
        node.data.backgroundColor = color
        if (!node.data.createdAt) node.data.createdAt = nowIso
        node.data.updatedAt = nowIso
      }
    }
    logAndCommit()
  }
  menu.visible = false
}

const updateFontStyle = () => {
  if (menu.contextNodeId) {
    const nowIso = new Date().toISOString()
    const applyStyle = (node: Node) => {
      node.data.fontSize = currentFontSize.value
      node.data.fontColor = currentFontColor.value
      if (!node.data.createdAt) node.data.createdAt = nowIso
      node.data.updatedAt = nowIso
    }

    if (menu.type === 'selection') {
      selectedNodes.value.forEach(applyStyle)
    } else {
      const node = nodes.value.find(n => n.id === menu.contextNodeId)
      if (node) applyStyle(node)
    }
    logAndCommit()
  }
}

const addNote = () => {
  createNoteAt(menu.x, menu.y)
  closeMenu()
}

const createGroupAt = (clientX?: number, clientY?: number) => {
  let x, y

  if (clientX !== undefined && clientY !== undefined) {
    const p = project({ x: clientX, y: clientY })
    x = p.x
    y = p.y
  } else {
    if (vueFlowInstance.value) {
      const p = project({ x: window.innerWidth / 2, y: window.innerHeight / 2 })
      x = p.x
      y = p.y
    } else {
      x = 250
      y = 100
    }
  }

  const nowIso = new Date().toISOString()
  const groupNode: Node = {
    id: uuidv4(),
    type: 'group',
    position: { x, y },
    style: { width: '400px', height: '260px', zIndex: 0 },
    data: { label: '新建分组', createdAt: nowIso, updatedAt: nowIso },
  }
  nodes.value.push(groupNode)
  logAndCommit()
}

const addGroup = () => {
  createGroupAt(menu.x, menu.y)
  closeMenu()
}

const performDelete = (nodesToDelete: Set<string>, edgesToDelete: Set<string>) => {
  nodesToDelete.forEach(id => cancelTimersForNode(id))
  nodes.value = nodes.value.filter(n => !nodesToDelete.has(n.id))
  edges.value = edges.value.filter(e => !edgesToDelete.has(e.id) && !nodesToDelete.has(e.source) && !nodesToDelete.has(e.target))
  
  logAndCommit()
  menu.visible = false
}

const deleteNode = () => {
  const nodesToDelete = new Set<string>()
  const edgesToDelete = new Set<string>()

  // 1. Determine targets from Context Menu or Selection
  if (menu.visible && menu.contextNodeId) {
    if (menu.type === 'selection') {
      selectedNodes.value.forEach(n => nodesToDelete.add(n.id))
    } else {
      nodesToDelete.add(menu.contextNodeId)
    }
  } else {
    // Keyboard delete
    const selectedN = getSelectedNodes.value
    const selectedE = getSelectedEdges.value
    selectedN.forEach(n => nodesToDelete.add(n.id))
    selectedE.forEach(e => edgesToDelete.add(e.id))
  }

  if (nodesToDelete.size === 0 && edgesToDelete.size === 0) return

  // 2. Check for Groups
  const groupsToDelete = nodes.value.filter(n => nodesToDelete.has(n.id) && n.type === 'group')
  
  if (groupsToDelete.length > 0) {
    confirmModalMessage.value = '是否删除分组？默认仅删除分组本身'
    confirmModalCheckboxLabel.value = '同时删除分组内所有元素'
    confirmModalCheckboxDefaultChecked.value = false
    confirmCallback.value = (deleteChildren?: boolean) => {
      const nodeMap = new Map<string, any>()
      nodes.value.forEach(n => nodeMap.set(n.id, n))

      const getAbs = (id: string) => {
        let x = 0
        let y = 0
        const visited = new Set<string>()
        let curId: string | undefined = id
        while (curId) {
          if (visited.has(curId)) break
          visited.add(curId)
          const n = nodeMap.get(curId)
          if (!n) break
          x += n.position?.x || 0
          y += n.position?.y || 0
          const p = n.parentNode
          if (p && nodeMap.get(p)?.type === 'group') curId = p
          else break
        }
        return { x, y }
      }

      const groupIds = new Set(groupsToDelete.map(g => g.id))

      if (deleteChildren) {
        const stack = [...groupIds]
        while (stack.length) {
          const gid = stack.pop()!
          nodes.value.forEach(n => {
            if (n.parentNode === gid) {
              if (!nodesToDelete.has(n.id)) nodesToDelete.add(n.id)
              if (n.type === 'group') stack.push(n.id)
            }
          })
        }
        performDelete(nodesToDelete, edgesToDelete)
        return
      }

      const resolveParent = (node: any) => {
        let pid: string | undefined = node.parentNode
        while (pid && nodesToDelete.has(pid) && nodeMap.get(pid)?.type === 'group') {
          pid = nodeMap.get(pid)?.parentNode
        }
        return pid
      }

      const updatedNodes = nodes.value.map(n => {
        if (nodesToDelete.has(n.id)) return n
        if (!n.parentNode) return n
        if (!nodesToDelete.has(n.parentNode)) return n
        if (nodeMap.get(n.parentNode)?.type !== 'group') return n

        const abs = getAbs(n.id)
        const newParent = resolveParent(n)
        if (newParent && nodeMap.get(newParent)?.type === 'group') {
          const pAbs = getAbs(newParent)
          return {
            ...n,
            parentNode: newParent,
            position: { x: abs.x - pAbs.x, y: abs.y - pAbs.y },
            extent: undefined,
          }
        }
        return { ...n, parentNode: undefined, position: abs, extent: undefined }
      })

      nodes.value = updatedNodes
      performDelete(nodesToDelete, edgesToDelete)
    }
    showConfirmModal.value = true
    return
  }

  // 3. Execute Deletion
  performDelete(nodesToDelete, edgesToDelete)
}

// Removed duplicate listeners

const groupNodes = () => {
  if (selectedNodes.value.length > 1) {
    // Calculate bounding box
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    
    selectedNodes.value.forEach(node => {
      // Use dimensions if available, otherwise fallback to style
      // Note: node.dimensions is reliable if the node has been rendered
      const nodeStyle = node.style as any
      const width = node.dimensions?.width || (typeof nodeStyle?.width === 'number' ? nodeStyle.width : parseInt(nodeStyle?.width as string || '300'))
      const height = node.dimensions?.height || (typeof nodeStyle?.height === 'number' ? nodeStyle.height : parseInt(nodeStyle?.height as string || '200'))
      
      const x = node.position.x
      const y = node.position.y
      
      minX = Math.min(minX, x)
      minY = Math.min(minY, y)
      
      maxX = Math.max(maxX, x + width)
      maxY = Math.max(maxY, y + height)
    })
    
    // Add padding
    const padding = 40
    minX -= padding
    minY -= padding
    maxX += padding
    maxY += padding
    
    const groupId = uuidv4()
    const nowIso = new Date().toISOString()
    const groupNode: Node = {
      id: groupId,
      type: 'group',
      position: { x: minX, y: minY },
      style: { width: `${maxX - minX}px`, height: `${maxY - minY}px`, zIndex: 0 },
      data: { label: '新建分组', createdAt: nowIso, updatedAt: nowIso },
    }
    
    // Create new node objects for children with updated position and parent
    // IMPORTANT: We must create new objects to ensure Vue Flow detects the coordinate system change
    // from absolute to relative immediately.
    const childNodes = selectedNodes.value.map(node => ({
      ...node,
      parentNode: groupId,
      position: {
        x: node.position.x - minX,
        y: node.position.y - minY
      },
      data: {
        ...(node.data || {}),
        createdAt: (node as any).data?.createdAt || nowIso,
        updatedAt: nowIso,
      },
      extent: undefined // Ensure extent is reset if needed
    }))
    
    // Filter out old selected nodes and add new group + updated children
    const selectedIds = new Set(selectedNodes.value.map(n => n.id))
    const otherNodes = nodes.value.filter(n => !selectedIds.has(n.id))
    
    nodes.value = [...otherNodes, groupNode, ...childNodes]
    
    logAndCommit()
  }
  menu.visible = false
}

const alignNodes = (type: 'left' | 'top') => {
  if (selectedNodes.value.length > 1) {
    const nowIso = new Date().toISOString()
    if (type === 'left') {
      const minX = Math.min(...selectedNodes.value.map(n => n.position.x))
      selectedNodes.value.forEach(n => {
        n.position.x = minX
        if (!n.data.createdAt) n.data.createdAt = nowIso
        n.data.updatedAt = nowIso
      })
    } else if (type === 'top') {
      const minY = Math.min(...selectedNodes.value.map(n => n.position.y))
      selectedNodes.value.forEach(n => {
        n.position.y = minY
        if (!n.data.createdAt) n.data.createdAt = nowIso
        n.data.updatedAt = nowIso
      })
    }
    logAndCommit()
  }
  menu.visible = false
}

const autoLayoutNodes = () => {
  if (selectedNodes.value.length <= 1) {
    menu.visible = false
    return
  }

  const parsePx = (v: any) => {
    if (typeof v === 'number') return v
    if (typeof v !== 'string') return null
    const m = v.match(/^(\d+(\.\d+)?)px$/)
    if (!m) return null
    return parseFloat(m[1])
  }

  const getSize = (n: any) => {
    const style = (n.style || {}) as any
    const w = parsePx(style.width) ?? 300
    const h = (style.height && style.height !== 'auto') ? (parsePx(style.height) ?? 200) : 200
    return { w, h }
  }

  const byParent = new Map<string, any[]>()
  selectedNodes.value.forEach(n => {
    const key = (n as any).parentNode || '__root__'
    if (!byParent.has(key)) byParent.set(key, [])
    byParent.get(key)!.push(n)
  })

  const gap = 40

  const nowIso = new Date().toISOString()
  byParent.forEach(list => {
    const sorted = [...list].sort((a, b) => (a.position.y - b.position.y) || (a.position.x - b.position.x))
    const minX = Math.min(...sorted.map(n => n.position.x))
    const minY = Math.min(...sorted.map(n => n.position.y))

    const sizes = sorted.map(getSize)
    const maxW = Math.max(...sizes.map(s => s.w))
    const maxH = Math.max(...sizes.map(s => s.h))

    const cols = Math.max(1, Math.ceil(Math.sqrt(sorted.length)))
    const cellW = maxW + gap
    const cellH = maxH + gap

    sorted.forEach((n, idx) => {
      const col = idx % cols
      const row = Math.floor(idx / cols)
      n.position.x = minX + col * cellW
      n.position.y = minY + row * cellH
      if (!n.data.createdAt) n.data.createdAt = nowIso
      n.data.updatedAt = nowIso
    })
  })

  logAndCommit()
  menu.visible = false
}

const isContextGroupNode = computed(() => {
  if (!menu.contextNodeId) return false
  const node = nodes.value.find(n => n.id === menu.contextNodeId)
  return !!node && node.type === 'group'
})

const autoLayoutGroupChildren = () => {
  if (!menu.contextNodeId) {
    menu.visible = false
    return
  }

  const groupId = menu.contextNodeId
  const group = nodes.value.find(n => n.id === groupId && n.type === 'group') as any
  if (!group) {
    menu.visible = false
    return
  }

  const children = nodes.value.filter(n => (n as any).parentNode === groupId) as any[]
  if (children.length === 0) {
    menu.visible = false
    return
  }

  const parsePx = (v: any) => {
    if (typeof v === 'number') return v
    if (typeof v !== 'string') return null
    const m = v.match(/^(\d+(\.\d+)?)px$/)
    if (!m) return null
    return parseFloat(m[1])
  }

  const getSize = (n: any) => {
    const style = (n.style || {}) as any
    const w = parsePx(style.width) ?? 300
    const h = (style.height && style.height !== 'auto') ? (parsePx(style.height) ?? 200) : 200
    return { w, h }
  }

  const gap = 32
  const paddingX = 20
  const paddingTop = 40
  const paddingBottom = 20

  const sizes = children.map(getSize)
  const maxW = Math.max(...sizes.map(s => s.w))
  const maxH = Math.max(...sizes.map(s => s.h))
  const cols = Math.max(1, Math.ceil(Math.sqrt(children.length)))
  const rows = Math.ceil(children.length / cols)

  children
    .sort((a, b) => (a.position.y - b.position.y) || (a.position.x - b.position.x))
    .forEach((n, idx) => {
      const col = idx % cols
      const row = Math.floor(idx / cols)
      n.position.x = paddingX + col * (maxW + gap)
      n.position.y = paddingTop + row * (maxH + gap)
    })

  const neededW = paddingX * 2 + cols * maxW + (cols - 1) * gap
  const neededH = paddingTop + paddingBottom + rows * maxH + (rows - 1) * gap

  const groupStyle = (group.style || {}) as any
  const curW = parsePx(groupStyle.width) ?? 200
  const curH = parsePx(groupStyle.height) ?? 200

  group.style = {
    ...groupStyle,
    width: `${Math.max(curW, neededW)}px`,
    height: `${Math.max(curH, neededH)}px`,
  }

  logAndCommit()
  menu.visible = false
}

const exportData = () => {
  if (user.value) {
    saveToServer()
  } else {
    if (confirm('是否登录以保存到云端？')) {
      showAuthModal.value = true
    }
  }
}

const onKeyUp = (e: KeyboardEvent) => {
  if (e.code === 'Space' && isTemporaryLock.value) {
    isReadOnly.value = false
    isTemporaryLock.value = false
  }
}

const onKeyDown = (e: KeyboardEvent) => {
  const target = e.target as HTMLElement
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable) return

  // Spacebar Temporary Lock
  if (e.code === 'Space' && !e.repeat && !isReadOnly.value) {
     isTemporaryLock.value = true
     isReadOnly.value = true
  }

  // Toggle Lock
  if (matchShortcut(e, 'toggleLock')) {
    e.preventDefault()
    isReadOnly.value = !isReadOnly.value
    addToast(isReadOnly.value ? '画布已锁定' : '画布已解锁', 'info')
  }

  // Save
  if (matchShortcut(e, 'save')) {
    e.preventDefault()
    exportData()
  }
  
  // Search
  if (matchShortcut(e, 'search')) {
    e.preventDefault()
    showSearch.value = !showSearch.value
  }

  // Help
  if (e.key === '?' && (e.metaKey || e.ctrlKey)) {
    e.preventDefault()
    openHelp()
  }

  // Delete
  if (matchShortcut(e, 'delete')) {
    e.preventDefault()
    e.stopPropagation()
    deleteNode()
  }

  // Group
  if (matchShortcut(e, 'group')) {
    e.preventDefault()
    groupNodes()
  }

  // New Node
  if (matchShortcut(e, 'newNode')) {
    // Only if not in input
    createNoteAt(undefined, undefined) // Need to handle default position
  }

  // Undo
  if (matchShortcut(e, 'undo')) {
    e.preventDefault()
    if (canUndo.value) undo()
  }

  // Redo
  if (matchShortcut(e, 'redo')) {
    e.preventDefault()
    if (canRedo.value) redo()
  }
}

// Modify createNoteAt to handle undefined args (center of viewport)
const createNoteAt = (clientX?: number, clientY?: number) => {
  let x, y
  
  if (clientX !== undefined && clientY !== undefined) {
    const p = project({ x: clientX, y: clientY })
    x = p.x
    y = p.y
  } else {
    // Center of viewport
    // viewport.value.x/y is the transform, not the center.
    // We want the center of the visible area.
    // Viewport center = (-viewport.x + containerWidth/2) / zoom, (-viewport.y + containerHeight/2) / zoom
    // We can just use a safe default or try to get center.
    // For simplicity, let's use viewport center if available, else 0,0
    // Actually, VueFlow exposes `getNodes` etc but not container dimensions directly without refs.
    // Let's just put it at a slight offset from current viewport center logic or just 100,100 corrected by viewport.
    
    // Easier: project window.innerWidth/2, window.innerHeight/2
    if (vueFlowInstance.value) {
       const p = project({ x: window.innerWidth / 2, y: window.innerHeight / 2 })
       x = p.x
       y = p.y
    } else {
       x = 250
       y = 100
    }
  }

  const nowIso = new Date().toISOString()
  const newNode: Node = {
    id: uuidv4(),
    type: 'note',
    position: { x, y },
    data: { label: 'New Note', initialFocus: true, borderWidth: 1, createdAt: nowIso, updatedAt: nowIso },
    style: { width: '300px', height: 'auto', minHeight: '200px' },
  }
  nodes.value.push(newNode)
  logAndCommit()
}

import TurndownService from 'turndown'
import { gfm } from 'turndown-plugin-gfm'

const handleCopyMarkdown = () => {
  const turndownService = new TurndownService()
  turndownService.use(gfm)

  let markdown = ''
  
  if (selectedNodes.value.length > 0) {
    selectedNodes.value.forEach(node => {
      if (node.data.content) {
        markdown += turndownService.turndown(node.data.content) + '\n\n---\n\n'
      }
    })
  } else if (menu.contextNodeId) {
    const node = nodes.value.find(n => n.id === menu.contextNodeId)
    if (node && node.data.content) {
      markdown = turndownService.turndown(node.data.content)
    }
  }
  
  if (markdown) {
    navigator.clipboard.writeText(markdown.trim())
    addToast('已复制为 Markdown', 'success')
    closeMenu()
  } else {
    addToast('无内容可复制', 'info')
  }
}

provide('handleCopyMarkdown', handleCopyMarkdown)
</script>

<style>
/* Vue Flow styles are imported in main.ts */
.locked-canvas .vue-flow__node {
  pointer-events: none !important;
}
</style>
