<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-96 overflow-hidden transform transition-all">
      <div class="relative h-32 bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
        <button @click="$emit('close')" class="absolute top-2 right-2 text-white hover:text-gray-200 bg-black bg-opacity-20 rounded-full p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <div class="text-white text-center">
          <div class="text-3xl font-bold mb-1">丰小子科技</div>
          <div class="text-xs opacity-80">Fengxiaozi Tech</div>
        </div>
      </div>
      
      <div class="p-6">
        <div class="text-center mb-6">
          <p class="text-gray-600 text-sm leading-relaxed">
            专注于为您提供极致的无限画布体验。<br>
            激发创意，整理思绪，连接未来。
          </p>
        </div>
        
        <div class="space-y-3">
          <div class="flex items-center p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-3">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <div class="text-xs text-gray-500">联系邮箱</div>
              <div class="text-sm font-medium text-gray-800">support@fengxiaozi.net</div>
            </div>
          </div>
          
          <div class="flex items-center p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 mr-3">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            </div>
            <div>
              <div class="text-xs text-gray-500">官方网站</div>
              <div class="text-sm font-medium text-gray-800">www.fengxiaozi.net</div>
            </div>
          </div>
        </div>

        <div class="mt-6 text-center text-xs text-gray-400">
          <a href="https://beian.miit.gov.cn/" target="_blank">© {{ new Date().getFullYear() }} 丰小子科技 版权所有</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits(['close'])
</script>
