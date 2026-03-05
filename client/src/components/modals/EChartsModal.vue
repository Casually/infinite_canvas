<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[800px] h-[600px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h2 class="text-lg font-bold text-gray-800">{{ readonly ? '图表展示' : '图表配置' }}</h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      
      <div class="flex-1 flex overflow-hidden">
        <!-- Sidebar: Configuration -->
        <div v-if="!readonly" class="w-1/2 border-r p-6 overflow-y-auto bg-gray-50">
          <!-- Chart Type Selection -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">图表类型</label>
            <div class="grid grid-cols-3 gap-2">
              <button 
                v-for="type in ['bar', 'line', 'pie', 'scatter', 'gantt']" 
                :key="type"
                type="button"
                class="px-3 py-2 border rounded text-sm capitalize hover:bg-blue-50 hover:border-blue-300"
                :class="{'bg-blue-100 border-blue-500 text-blue-700': currentType === type}"
                @click="applyTemplate(type)"
              >
                {{ type }}
              </button>
            </div>
          </div>

          <!-- Data Source Type -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">数据源</label>
            <div class="flex gap-4 mb-3">
              <label class="flex items-center">
                <input type="radio" v-model="dataSourceType" value="static" class="mr-2">
                静态数据 (JSON)
              </label>
              <label class="flex items-center">
                <input type="radio" v-model="dataSourceType" value="api" class="mr-2">
                API 请求
              </label>
            </div>
            
            <div v-if="dataSourceType === 'api'">
              <input 
                v-model="dataUrl" 
                type="text" 
                placeholder="https://api.example.com/data"
                class="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500"
              >
              <p class="text-xs text-gray-500 mt-1">API 需返回 ECharts 兼容的 Option 对象或数据片段</p>
            </div>
          </div>

          <!-- JSON Editor -->
          <div class="mb-4 flex-1 flex flex-col">
            <label class="block text-sm font-medium text-gray-700 mb-2">配置代码 (Option)</label>
            <textarea 
              v-model="optionCode" 
              class="w-full h-64 font-mono text-xs p-3 border rounded-md focus:ring-2 focus:ring-blue-500 resize-none bg-white"
              spellcheck="false"
              placeholder="{ title: { text: 'ECharts' }, ... }"
            ></textarea>
            <div v-if="jsonError" class="text-xs text-red-500 mt-1">{{ jsonError }}</div>
          </div>
          
          <button 
            type="button" 
            class="w-full py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
            @click="preview"
          >
            更新预览
          </button>
        </div>

        <!-- Preview Area -->
        <div :class="readonly ? 'w-full' : 'w-1/2'" class="p-6 flex flex-col items-center justify-center bg-white relative">
          <div v-if="!readonly" class="absolute top-2 left-4 text-xs font-bold text-gray-400 uppercase tracking-wide">Preview</div>
          <div ref="previewChartRef" class="w-full h-full min-h-[300px]"></div>
        </div>
      </div>
      
      <div v-if="!readonly" class="p-4 border-t bg-gray-50 flex justify-end gap-3">
        <button 
          @click="$emit('close')" 
          class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-200 rounded-md"
        >
          取消
        </button>
        <button 
          @click="handleSave" 
          class="px-6 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm"
        >
          完成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { processOption } from '../nodes/chartRenderers'

const props = defineProps<{
  initialData?: {
    option: any
    dataSourceType: 'static' | 'api'
    dataUrl: string
  }
  initialType?: string
  readonly?: boolean
}>()

const emit = defineEmits(['close', 'save'])

const dataSourceType = ref<'static' | 'api'>('static')
const dataUrl = ref('')
const optionCode = ref('')
const currentType = ref('bar')
const jsonError = ref('')

const previewChartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// Initialize with props
if (props.initialData) {
  dataSourceType.value = props.initialData.dataSourceType || 'static'
  dataUrl.value = props.initialData.dataUrl || ''
  if (props.initialData.option) {
    optionCode.value = JSON.stringify(props.initialData.option, null, 2)
  } else {
    // Default template will be set below
  }
} 

if (!optionCode.value) {
  // Use initialType if provided, otherwise default to bar
  const type = props.initialType || 'bar'
  
  // Define templates first so we can use them
  const templates: Record<string, any> = {
    bar: {
      title: { text: '柱状图示例' },
      tooltip: {},
      xAxis: { data: ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子'] },
      yAxis: {},
      series: [{ name: '销量', type: 'bar', data: [5, 20, 36, 10, 10, 20] }]
    },
    line: {
      title: { text: '折线图示例' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value' },
      series: [{ data: [150, 230, 224, 218, 135, 147, 260], type: 'line' }]
    },
    pie: {
      title: { text: '饼图示例', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: 'Access From',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: 'Search Engine' },
            { value: 735, name: 'Direct' },
            { value: 580, name: 'Email' },
            { value: 484, name: 'Union Ads' },
            { value: 300, name: 'Video Ads' }
          ]
        }
      ]
    },
    scatter: {
      xAxis: {},
      yAxis: {},
      series: [
        {
          symbolSize: 20,
          data: [
            [10.0, 8.04],
            [8.0, 6.95],
            [13.0, 7.58],
            [9.0, 8.81],
            [11.0, 8.33],
            [14.0, 9.96],
            [6.0, 7.24],
            [4.0, 4.26],
            [12.0, 10.84],
            [7.0, 4.82],
            [5.0, 5.68]
          ],
          type: 'scatter'
        }
      ]
    },
    gantt: {
      title: { text: '项目进度甘特图', left: 'center' },
      tooltip: {
        formatter: (params: any) => {
          return params.marker + params.name + ': ' + params.value[1] + ' ~ ' + params.value[2]
        }
      },
      grid: {
        height: 300,
        containLabel: true
      },
      xAxis: {
        type: 'time',
        position: 'top',
        axisLabel: {
          formatter: '{yyyy}-{MM}-{dd}'
        }
      },
      yAxis: {
        type: 'category',
        data: ['任务A', '任务B', '任务C', '任务D']
      },
      series: [
        {
          type: 'custom',
          renderItem: 'ganttRender',
          itemStyle: {
            opacity: 0.8
          },
          encode: {
            x: [1, 2],
            y: 0
          },
          data: [
            {
              value: [0, '2025-01-01', '2025-01-15'],
              itemStyle: { color: '#5470c6' },
              name: '计划阶段'
            },
            {
              value: [1, '2025-01-10', '2025-02-10'],
              itemStyle: { color: '#91cc75' },
              name: '开发阶段'
            },
            {
              value: [2, '2025-02-05', '2025-02-20'],
              itemStyle: { color: '#fac858' },
              name: '测试阶段'
            },
            {
              value: [3, '2025-02-18', '2025-03-01'],
              itemStyle: { color: '#ee6666' },
              name: '上线阶段'
            }
          ]
        }
      ]
    }
  }

  // Remove functions from templates before stringifying (specifically tooltip formatter)
  // For gantt, renderItem is already a string 'ganttRender', so it's safe.
  // But tooltip formatter is a function in my code above.
  // I need to handle tooltip formatter if I want it to work.
  // JSON.stringify will strip it.
  // For now, let's remove the tooltip formatter from the default template or make it simple string if possible.
  // ECharts tooltip formatter can be string.
  
  if (type === 'gantt') {
     // Remove function formatter for initial stringify to avoid confusion/loss
     // Or I can leave it out and let default tooltip work
     delete templates.gantt.tooltip.formatter
  }

  currentType.value = type
  optionCode.value = JSON.stringify(templates[type] || templates['bar'], null, 2)
}

const templates: Record<string, any> = {
  bar: {
    title: { text: '柱状图示例' },
    tooltip: {},
    xAxis: { data: ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子'] },
    yAxis: {},
    series: [{ name: '销量', type: 'bar', data: [5, 20, 36, 10, 10, 20] }]
  },
  line: {
    title: { text: '折线图示例' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value' },
    series: [{ data: [150, 230, 224, 218, 135, 147, 260], type: 'line' }]
  },
  pie: {
    title: { text: '饼图示例', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        name: 'Access From',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: 'Search Engine' },
          { value: 735, name: 'Direct' },
          { value: 580, name: 'Email' },
          { value: 484, name: 'Union Ads' },
          { value: 300, name: 'Video Ads' }
        ]
      }
    ]
  },
  scatter: {
    xAxis: {},
    yAxis: {},
    series: [
      {
        symbolSize: 20,
        data: [
          [10.0, 8.04],
          [8.0, 6.95],
          [13.0, 7.58],
          [9.0, 8.81],
          [11.0, 8.33],
          [14.0, 9.96],
          [6.0, 7.24],
          [4.0, 4.26],
          [12.0, 10.84],
          [7.0, 4.82],
          [5.0, 5.68]
        ],
        type: 'scatter'
      }
    ]
  },
  gantt: {
      title: { text: '项目进度甘特图', left: 'center' },
      tooltip: {
        // Formatter function removed for JSON compatibility
      },
      grid: {
        height: 300,
        containLabel: true
      },
      xAxis: {
        type: 'time',
        position: 'top',
        axisLabel: {
          formatter: '{yyyy}-{MM}-{dd}'
        }
      },
      yAxis: {
        type: 'category',
        data: ['任务A', '任务B', '任务C', '任务D']
      },
      series: [
        {
          type: 'custom',
          renderItem: 'ganttRender',
          itemStyle: {
            opacity: 0.8
          },
          encode: {
            x: [1, 2],
            y: 0
          },
          data: [
            {
              value: [0, '2025-01-01', '2025-01-15'],
              itemStyle: { color: '#5470c6' },
              name: '计划阶段'
            },
            {
              value: [1, '2025-01-10', '2025-02-10'],
              itemStyle: { color: '#91cc75' },
              name: '开发阶段'
            },
            {
              value: [2, '2025-02-05', '2025-02-20'],
              itemStyle: { color: '#fac858' },
              name: '测试阶段'
            },
            {
              value: [3, '2025-02-18', '2025-03-01'],
              itemStyle: { color: '#ee6666' },
              name: '上线阶段'
            }
          ]
        }
      ]
    }
}

const applyTemplate = (type: string) => {
  if (type === 'gantt') {
      // Remove function formatter for initial stringify to avoid confusion/loss
      delete templates.gantt.tooltip.formatter
   }

  currentType.value = type
  optionCode.value = JSON.stringify(templates[type], null, 2)
  preview()
}

const preview = () => {
  jsonError.value = ''
  try {
    let option = JSON.parse(optionCode.value)
    
    // Process option using chartRenderers (e.g. replace 'ganttRender' string with function)
    option = processOption(option)
    
    if (chartInstance) {
      chartInstance.setOption(option, true) // true = not merge, replace
    }
  } catch (e: any) {
    jsonError.value = 'JSON 格式错误: ' + e.message
  }
}

const handleSave = () => {
  jsonError.value = ''
  try {
    const option = JSON.parse(optionCode.value)
    emit('save', {
      option,
      dataSourceType: dataSourceType.value,
      dataUrl: dataUrl.value
    })
  } catch (e: any) {
    jsonError.value = 'JSON 格式错误: ' + e.message
  }
}

onMounted(() => {
  if (previewChartRef.value) {
    chartInstance = echarts.init(previewChartRef.value)
    preview()
    
    // Resize handling
    window.addEventListener('resize', () => chartInstance?.resize())
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  // Remove event listener if added... but for modal it's okay, maybe strictly remove
})

</script>
