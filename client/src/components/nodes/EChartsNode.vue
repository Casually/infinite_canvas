<template>
  <node-view-wrapper class="echarts-node-wrapper">
    <BaseBlockWrapper :editor="editor" :node="node" :get-pos="getPos">
      <div class="echarts-wrapper relative border rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow" :class="{ 'ring-2 ring-blue-500': selected && props.editor.isEditable }">
        <div 
          class="echarts-container" 
          ref="chartRef" 
          :style="{ width: '100%', height: height }"
          @dblclick="handleDblClick"
        ></div>
        
        <!-- Loading Overlay -->
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 z-10">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
        
        <!-- Error Overlay -->
        <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-red-50 bg-opacity-90 z-10 p-4 text-center">
          <div class="text-red-500 text-sm">{{ error }}</div>
        </div>

        <!-- Edit Overlay (only on hover in edit mode) -->
        <div 
          v-if="props.editor.isEditable" 
          class="absolute top-2 right-2 opacity-0 hover:opacity-100 transition-opacity bg-white rounded shadow px-2 py-1 text-xs text-gray-500 cursor-pointer border"
          @click="openEditModal"
        >
          双击编辑图表
        </div>
      </div>
    </BaseBlockWrapper>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { ref, onMounted, onUnmounted, watch, computed, inject } from 'vue'
import * as echarts from 'echarts'
import { processOption } from './chartRenderers'
import BaseBlockWrapper from './BaseBlockWrapper.vue'

const props = defineProps(nodeViewProps)
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
const loading = ref(false)
const error = ref('')

const openEChartsModal = inject('openEChartsModal') as (callback: (data: any) => void, initialData?: any) => void

const height = computed(() => props.node.attrs.height || '400px')
const option = computed(() => props.node.attrs.option)
const dataSourceType = computed(() => props.node.attrs.dataSourceType || 'static')
const dataUrl = computed(() => props.node.attrs.dataUrl)

const initChart = async () => {
  if (!chartRef.value) return
  
  // Dispose existing instance if any
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)
  
  await updateChartData()
}

const updateChartData = async () => {
  if (!chartInstance) return

  loading.value = true
  error.value = ''

  try {
    let finalOption = option.value

    if (dataSourceType.value === 'api' && dataUrl.value) {
      try {
        const res = await fetch(dataUrl.value)
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        const data = await res.json()
        
        // Assume API returns standard ECharts option or data to be merged
        // For simplicity, let's assume the user configures the static part and API returns the 'dataset' or 'series' data
        // Or strictly, if API is used, we might expect it to return the full option or specific data structure.
        // To make it flexible:
        // 1. If option is empty, assume API returns full option.
        // 2. If option exists, try to merge API data into it (requires knowing where to put it).
        // For this first version, let's assume if API is used, the 'option' prop acts as a template, 
        // and we might need a way to map API data. 
        // BUT, the simplest requirement is "Data Source (Static or GET request)".
        // Let's assume if GET request, the response IS the option object or part of it.
        
        // Simple strategy: Merge API result into options
        finalOption = { ...finalOption, ...data }
      } catch (e: any) {
        throw new Error(`Failed to fetch data: ${e.message}`)
      }
    }

    // Ensure finalOption is an object
    if (typeof finalOption === 'string') {
      try {
        finalOption = JSON.parse(finalOption)
      } catch (e) {
        console.error('Invalid JSON option', e)
        error.value = 'Invalid JSON configuration'
        return
      }
    }

    if (!finalOption || typeof finalOption !== 'object') {
      error.value = 'Invalid chart configuration'
      return
    }

    // Process renderItem strings to functions
    finalOption = processOption(finalOption)

    chartInstance.setOption(finalOption, true)
  } catch (e: any) {
    error.value = e.message
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleDblClick = (e: MouseEvent) => {
  e.stopPropagation() // Prevent NoteNode from entering edit mode if not desired, or interference
  if (props.editor.isEditable) {
    openEditModal()
  } else {
    // Expand/Maximize
    // We can use a modal to show the chart in large size
    // For now, let's just re-use the openEChartsModal in 'preview' mode or just a simple maximize
    // The requirement says: "Non-edit mode double click to expand display"
    // I can emit an event or call a global maximize function
    // Let's implement a "ChartPreviewModal" logic in InfiniteCanvas or reuse EChartsModal in readonly mode
    
    // Actually, I can use the same EChartsModal but with a readonly flag if I add it.
    // Or better, trigger a custom event that InfiniteCanvas listens to show a maximization modal.
    // Let's try to invoke a maximize function injected.
    const maximizeChart = inject('maximizeChart') as ((option: any) => void) | undefined
    if (maximizeChart) {
      maximizeChart(chartInstance?.getOption())
    }
  }
}

const openEditModal = () => {
  if (!props.editor.isEditable) return
  
  openEChartsModal((data: any) => {
    props.updateAttributes(data)
  }, {
    option: props.node.attrs.option,
    dataSourceType: props.node.attrs.dataSourceType,
    dataUrl: props.node.attrs.dataUrl
  })
}

watch([() => props.node.attrs.option, () => props.node.attrs.dataSourceType, () => props.node.attrs.dataUrl], () => {
  updateChartData()
}, { deep: true })

// Resize observer
let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  initChart()
  
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      chartInstance?.resize()
    })
    resizeObserver.observe(chartRef.value)
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.echarts-wrapper {
  max-width: 100%;
}
</style>
