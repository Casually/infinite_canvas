<template>
  <div class="flex items-center gap-2" :title="tooltip">
    <span class="text-xs font-medium text-gray-700">{{ value }}</span>
    
    <div class="relative w-8 h-4 border border-gray-400 rounded-sm p-0.5">
      <!-- Battery Terminal -->
      <div class="absolute -right-1 top-1 w-0.5 h-2 bg-gray-400 rounded-r-sm"></div>
      
      <!-- Fill -->
      <div 
        class="h-full rounded-sm transition-all duration-300"
        :class="fillColorClass"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
    
    <span class="text-xs text-gray-500">{{ total }} {{ unit }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  value: number
  total: number
  unit?: string
  warningThreshold?: number
  dangerThreshold?: number
}>()

const percentage = computed(() => {
  if (props.total === 0) return 0
  return Math.min(100, Math.max(0, (props.value / props.total) * 100))
})

const fillColorClass = computed(() => {
  if (percentage.value > (props.dangerThreshold || 90)) return 'bg-red-500'
  if (percentage.value > (props.warningThreshold || 70)) return 'bg-yellow-500'
  return 'bg-green-500'
})

const tooltip = computed(() => {
  return `${props.value} / ${props.total} ${props.unit || ''}`
})
</script>