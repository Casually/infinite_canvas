<template>
  <div 
    class="fixed inset-0 z-[9999] bg-black bg-opacity-90 flex items-center justify-center overflow-hidden"
    @click="handleBackgroundClick"
    @wheel.prevent="handleWheel"
  >
    <div 
      ref="containerRef"
      class="relative w-full h-full flex items-center justify-center cursor-move"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
    >
      <img 
        :src="src" 
        class="max-w-none transition-transform duration-75 ease-linear select-none"
        :style="{
          transform: `translate(${translateX}px, ${translateY}px) scale(${scale}) rotate(${rotation}deg)`,
          maxWidth: '90vw',
          maxHeight: '90vh'
        }"
        @click.stop
        draggable="false"
      />
    </div>
    
    <!-- Controls -->
    <div class="absolute bottom-10 left-1/2 transform -translate-x-1/2 flex gap-4 bg-gray-800 bg-opacity-75 rounded-full px-6 py-2 items-center">
      <!-- Rotation Controls -->
      <button class="text-white hover:text-blue-400" @click.stop="rotateLeft" title="向左旋转">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      </button>
      <button class="text-white hover:text-blue-400 mr-4 border-r border-gray-600 pr-4" @click.stop="rotateRight" title="向右旋转">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6" />
        </svg>
      </button>

      <!-- Zoom Controls -->
      <button class="text-white hover:text-blue-400" @click.stop="zoomOut">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
        </svg>
      </button>
      <span class="text-white min-w-[3rem] text-center">{{ Math.round(scale * 100) }}%</span>
      <button class="text-white hover:text-blue-400" @click.stop="zoomIn">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
      <button class="text-white hover:text-red-400 ml-4 border-l border-gray-600 pl-4" @click.stop="reset">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <button 
      class="absolute top-4 right-4 text-white hover:text-gray-300 p-2 bg-gray-800 bg-opacity-50 rounded-full"
      @click="$emit('close')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  src: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const scale = ref(1)
const rotation = ref(0)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)
const containerRef = ref<HTMLElement | null>(null)

// Zoom limits
const MIN_SCALE = 0.1
const MAX_SCALE = 5

const handleWheel = (e: WheelEvent) => {
  const delta = -e.deltaY
  const zoomFactor = 0.1
  const newScale = delta > 0 ? scale.value + zoomFactor : scale.value - zoomFactor
  
  if (newScale >= MIN_SCALE && newScale <= MAX_SCALE) {
    // Zoom towards cursor would require more complex calculation involving rect
    // For simplicity, we just zoom center for now, or improve it:
    
    // Improved zoom: keep relative position
    // This is simplified. True cursor-zoom requires tracking offset relative to image center.
    scale.value = newScale
  }
}

const zoomIn = () => {
  if (scale.value < MAX_SCALE) scale.value += 0.2
}

const zoomOut = () => {
  if (scale.value > MIN_SCALE) scale.value -= 0.2
}

const rotateLeft = () => {
  rotation.value -= 90
}

const rotateRight = () => {
  rotation.value += 90
}

const reset = () => {
  scale.value = 1
  rotation.value = 0
  translateX.value = 0
  translateY.value = 0
}

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  startX.value = e.clientX - translateX.value
  startY.value = e.clientY - translateY.value
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  translateX.value = e.clientX - startX.value
  translateY.value = e.clientY - startY.value
}

const stopDrag = () => {
  isDragging.value = false
}

const handleBackgroundClick = () => {
  // Only close if not dragged significantly (to avoid closing after a drag release)
  // Since we have specific close button, maybe we can be stricter or just allow it.
  // With the current logic, clicking background calls this.
  // If user was dragging, stopDrag happens on mouseup. 
  // We can just emit close.
  if (!isDragging.value) {
    emit('close')
  }
}
</script>
