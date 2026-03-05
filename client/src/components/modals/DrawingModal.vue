<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[800px] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">画板</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <X class="w-6 h-6" />
        </button>
      </div>
      
      <div class="flex-1 bg-gray-50 p-4 flex justify-center items-center relative overflow-hidden">
        <canvas 
          ref="canvasRef" 
          class="bg-white shadow-sm border cursor-crosshair"
          :width="700"
          :height="500"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
        ></canvas>
        
        <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-white rounded-full shadow-lg border px-4 py-2 flex gap-4 items-center">
           <button @click="clearCanvas" class="text-sm text-red-500 hover:text-red-700 font-medium">清空</button>
           <div class="w-px h-4 bg-gray-300"></div>
           <div class="flex items-center gap-2">
             <span class="text-xs text-gray-500">颜色</span>
             <input type="color" v-model="color" class="w-6 h-6 rounded-full cursor-pointer border-0 p-0" />
           </div>
           <div class="flex items-center gap-2">
             <span class="text-xs text-gray-500">粗细</span>
             <input type="range" v-model.number="lineWidth" min="1" max="20" class="w-24 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
           </div>
        </div>
      </div>

      <div class="p-4 border-t flex justify-end gap-2">
        <button @click="$emit('close')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">取消</button>
        <button @click="save" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">保存到节点</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X } from 'lucide-vue-next'

const emit = defineEmits(['close', 'save'])

const canvasRef = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const color = ref('#000000')
const lineWidth = ref(3)
let ctx: CanvasRenderingContext2D | null = null

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    if (ctx) {
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      // Fill white background
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    }
  }
})

const startDrawing = (e: MouseEvent) => {
  isDrawing.value = true
  if (ctx) {
    ctx.beginPath()
    ctx.moveTo(e.offsetX, e.offsetY)
    ctx.strokeStyle = color.value
    ctx.lineWidth = lineWidth.value
  }
}

const draw = (e: MouseEvent) => {
  if (!isDrawing.value || !ctx) return
  ctx.lineTo(e.offsetX, e.offsetY)
  ctx.stroke()
}

const stopDrawing = () => {
  if (isDrawing.value && ctx) {
    ctx.closePath()
    isDrawing.value = false
  }
}

const clearCanvas = () => {
  if (ctx && canvasRef.value) {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  }
}

const save = () => {
  if (canvasRef.value) {
    const dataUrl = canvasRef.value.toDataURL('image/png')
    emit('save', dataUrl)
  }
}
</script>