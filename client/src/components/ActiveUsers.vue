<template>
  <div class="flex -space-x-2 overflow-hidden pointer-events-none mr-4">
    <div 
      v-for="user in users" 
      :key="user.id"
      class="relative inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-200 flex items-center justify-center text-xs font-medium text-white shadow-sm pointer-events-auto cursor-pointer overflow-hidden"
      :style="{ backgroundColor: user.avatar ? 'transparent' : user.color }"
      @click="selectedUser = user"
      :title="user.username"
    >
       <img v-if="user.avatar" :src="fullAvatarUrl(user.avatar)" class="w-full h-full object-cover" />
       <span v-else>{{ user.username.charAt(0).toUpperCase() }}</span>
    </div>
    <div v-if="users.length === 0" class="h-8 flex items-center px-2 bg-white bg-opacity-80 rounded-full text-xs text-gray-500 backdrop-blur-sm shadow-sm">
      ...
    </div>

    <!-- User Info Popover -->
    <div v-if="selectedUser" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-20 pointer-events-auto" @click.self="selectedUser = null">
       <div class="bg-white rounded-lg shadow-xl p-6 min-w-[250px] flex flex-col items-center animate-fade-in-up">
          <div class="w-20 h-20 rounded-full overflow-hidden mb-4 border-2 border-gray-100">
             <img v-if="selectedUser.avatar" :src="fullAvatarUrl(selectedUser.avatar)" class="w-full h-full object-cover" />
             <div v-else class="w-full h-full flex items-center justify-center text-3xl text-white" :style="{ backgroundColor: selectedUser.color }">
                {{ selectedUser.username.charAt(0).toUpperCase() }}
             </div>
          </div>
          <h3 class="text-lg font-bold text-gray-900">{{ selectedUser.username }}</h3>
          <p class="text-sm text-gray-500 mt-1">正在浏览此画布</p>
          <button @click="selectedUser = null" class="mt-4 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm">关闭</button>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  users: Array<{
    id: string
    username: string
    color: string
    avatar?: string
  }>
}>()

const selectedUser = ref<any>(null)

const fullAvatarUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.2s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
