<template>
  <div class="relative" ref="menuContainer">
    <!-- Menu Button -->
    <button 
      @click="toggleMenu"
      class="flex items-center gap-2 bg-white px-3 py-2 rounded-md shadow border hover:bg-gray-50 transition-colors"
    >
      <div v-if="user" class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-full overflow-hidden border border-gray-200 bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
          <img v-if="user.avatar" :src="fullAvatarUrl(user.avatar)" class="w-full h-full object-cover" />
          <span v-else>{{ (user.nickname || user.email || '?')[0].toUpperCase() }}</span>
        </div>
        <span class="text-sm font-medium text-gray-700 hidden sm:inline-block max-w-[100px] truncate">
          {{ user.nickname || user.email }}
        </span>
      </div>
      <div v-else class="text-sm font-medium text-gray-700">菜单</div>
      <Menu class="w-4 h-4 text-gray-500" />
    </button>

    <!-- Dropdown -->
    <div 
      v-if="isOpen" 
      class="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden transform origin-top-right transition-all flex flex-col max-h-[85vh]"
    >
      <div class="overflow-y-auto flex-1">
      <!-- User Info Section -->
      <div class="p-4 bg-gray-50 border-b border-gray-100">
        <div v-if="user">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
               <div class="w-8 h-8 rounded-full overflow-hidden border border-gray-200 bg-white flex items-center justify-center text-gray-400 font-bold text-sm">
                  <img v-if="user.avatar" :src="fullAvatarUrl(user.avatar)" class="w-full h-full object-cover" />
                  <span v-else>{{ (user.nickname || user.email || '?')[0].toUpperCase() }}</span>
               </div>
               <div class="flex flex-col">
                 <span class="font-medium text-gray-900 text-sm">{{ user.nickname || '未设置昵称' }}</span>
                 <span class="text-xs text-gray-500">{{ user.email }}</span>
               </div>
            </div>
          </div>
          
          <div class="flex gap-2 mb-4">
             <button @click="isProfileOpen = true; isOpen = false" class="flex-1 py-1 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50">
               个人信息
             </button>
             <button @click="$emit('changePassword')" class="flex-1 py-1 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50">
               修改密码
             </button>
          </div>
          
          <div class="mb-4 space-y-2">
            <button 
              @click="$emit('openCanvasManager'); isOpen = false"
              class="w-full py-2 bg-white border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              画布管理
            </button>
            <button 
              @click="$emit('openShareManager'); isOpen = false"
              class="w-full py-2 bg-white border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <span class="w-4 h-4 flex items-center justify-center">🔗</span>
              我的分享
            </button>
          </div>

          <div class="space-y-3">
            <!-- Storage -->
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2 text-gray-600">
                <Database class="w-4 h-4" />
                <span>存储空间</span>
              </div>
              <BatteryGauge :value="350" :total="1024" unit="MB" />
            </div>

            <!-- Balance -->
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2 text-gray-600">
                <CreditCard class="w-4 h-4" />
                <span>余额</span>
              </div>
              <span class="font-mono font-medium text-gray-700">¥ 128.50</span>
            </div>

            <!-- Token Usage -->
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2 text-gray-600">
                <Cpu class="w-4 h-4" />
                <span>Token 使用</span>
              </div>
              <BatteryGauge :value="12500" :total="50000" :warning-threshold="80" :danger-threshold="95" />
            </div>
          </div>
        </div>
        <div v-else class="text-center py-2">
          <p class="text-sm text-gray-500 mb-3">登录以同步数据和使用高级功能</p>
          <button 
            @click="$emit('login')"
            class="w-full py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            登录 / 注册
          </button>
        </div>
      </div>

      <!-- Data Management Section -->
      <div class="p-4 border-b border-gray-100">
        <div class="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">数据管理</div>
        <div class="grid grid-cols-2 gap-2">
            <button 
              @click="$emit('exportData'); isOpen = false"
              class="flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Download class="w-4 h-4" />
              导出
            </button>
            <button 
              @click="$emit('importData'); isOpen = false"
              class="flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Upload class="w-4 h-4" />
              导入
            </button>
        </div>
      </div>

      <!-- Tools Section -->
      <div class="p-4 border-b border-gray-100">
        <div class="text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">常用工具</div>
        <div class="grid grid-cols-2 gap-2">
            <button 
              @click="$emit('openReminderManager'); isOpen = false"
              class="flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Clock class="w-4 h-4" />
              定时提醒
            </button>
        </div>
      </div>

      <!-- Shortcuts Section -->
      <div class="p-4">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2 text-gray-900 font-medium text-sm">
            <Key class="w-4 h-4" />
            <span>快捷键设置</span>
          </div>
          <button 
            @click="$emit('openShortcuts'); isOpen = false" 
            class="text-xs text-blue-600 hover:text-blue-800 hover:underline"
          >
            修改
          </button>
        </div>
        
        <div class="space-y-2 max-h-60 overflow-y-auto">
          <div v-for="sc in shortcuts" :key="sc.id" class="flex items-center justify-between text-sm group">
            <span class="text-gray-600">{{ sc.label }}</span>
            <div class="flex gap-1">
              <span v-if="sc.isCtrlOrMeta" class="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs text-gray-500 font-mono">
                Ctrl/Cmd
              </span>
              <kbd v-for="(k, i) in sc.keys" :key="i" class="px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs text-gray-500 font-mono min-w-[20px] text-center uppercase">
                {{ k }}
              </kbd>
            </div>
          </div>
        </div>
      </div>
      </div>

      <!-- Footer Actions -->
      <div class="p-4 border-t border-gray-100">
        <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">视图导航模式</span>
        </div>
        <div class="flex bg-gray-100 p-1 rounded-lg">
            <button 
                class="flex-1 py-1.5 px-3 rounded-md text-xs font-medium transition-all"
                :class="interactionMode === 'mouse' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'"
                @click="$emit('update:interactionMode', 'mouse')"
            >
                鼠标模式
            </button>
            <button 
                class="flex-1 py-1.5 px-3 rounded-md text-xs font-medium transition-all"
                :class="interactionMode === 'trackpad' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'"
                @click="$emit('update:interactionMode', 'trackpad')"
            >
                触控板模式
            </button>
        </div>
      </div>

      <div v-if="user" class="p-2 bg-gray-50 border-t border-gray-100">
        <button 
          @click="$emit('logout')"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-md text-sm transition-colors"
        >
          <LogOut class="w-4 h-4" />
          <span>退出登录</span>
        </button>
      </div>
    </div>
    
    <!-- Click Outside Overlay -->
    <div v-if="isOpen" class="fixed inset-0 z-40 bg-transparent" @click="isOpen = false"></div>

    <UserProfileModal 
      v-if="isProfileOpen" 
      :user="user" 
      @close="isProfileOpen = false" 
      @update="(u) => $emit('updateUser', u)" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Menu, Database, CreditCard, Cpu, Key, LogOut, Download, Upload, Clock } from 'lucide-vue-next'
import BatteryGauge from './BatteryGauge.vue'
import UserProfileModal from '../modals/UserProfileModal.vue'
import { useShortcuts } from '../../composables/useShortcuts'

defineProps<{
  user: { email: string, token: string, nickname?: string, avatar?: string } | null
  interactionMode: 'mouse' | 'trackpad'
}>()

defineEmits(['login', 'logout', 'changePassword', 'openShortcuts', 'update:interactionMode', 'openCanvasManager', 'openShareManager', 'updateUser', 'exportData', 'importData', 'openReminderManager'])

const isOpen = ref(false)
const isProfileOpen = ref(false)
const menuContainer = ref<HTMLElement | null>(null)
const { shortcuts } = useShortcuts()

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const fullAvatarUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
}
</script>