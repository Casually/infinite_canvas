<template>
  <node-view-wrapper class="calendar-node select-none">
    <BaseBlockWrapper :editor="props.editor" :node="props.node" :get-pos="props.getPos">
      <div class="bg-white border rounded-lg shadow-sm overflow-hidden relative" contenteditable="false">
      <!-- Event Edit Modal -->
      <Teleport to="body">
        <EventEditorModal
          v-if="showEventModal"
          :initial-content="newEventText"
          :title="editingEventIndex !== null ? '编辑事项' : '添加事项'"
          @close="closeEventModal"
          @save="saveEvent"
        />
      </Teleport>
      
      <!-- Delete Confirm Modal (Keep centralized or make popover? Centralized is fine for delete) -->
      <div v-if="showDeleteModal" class="absolute inset-0 z-10 bg-white/90 flex items-center justify-center p-4">
        <div class="bg-white border shadow-lg rounded-lg p-4 w-full max-w-sm" @click.stop>
          <h3 class="font-medium text-gray-900 mb-2">确认删除</h3>
          <p class="text-sm text-gray-600 mb-4">确定要删除该事项吗？</p>
          <div class="flex justify-end gap-2">
            <button 
              @click="closeDeleteModal"
              class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded"
            >
              取消
            </button>
            <button 
              @click="confirmDelete"
              class="px-3 py-1.5 text-sm bg-red-500 text-white hover:bg-red-600 rounded"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- Header -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-b">
        <div class="flex items-center gap-2">
          <button @click="prevMonth" class="p-1 hover:bg-gray-200 rounded">
            <ChevronLeft class="w-4 h-4 text-gray-600" />
          </button>
          <span class="font-medium text-gray-700">{{ currentMonthLabel }}</span>
          <button @click="nextMonth" class="p-1 hover:bg-gray-200 rounded">
            <ChevronRight class="w-4 h-4 text-gray-600" />
          </button>
          <button @click="jumpToToday" class="ml-2 text-xs text-blue-500 hover:text-blue-700 font-medium">
            今天
          </button>
        </div>
        <div class="text-xs text-gray-500">
          {{ props.editor.isEditable ? '点击日期添加内容' : '只读模式' }}
        </div>
      </div>

      <!-- Days Header -->
      <div class="grid grid-cols-7 border-b bg-gray-50 text-xs font-medium text-gray-500 text-center py-2">
        <div v-for="day in weekDays" :key="day">{{ day }}</div>
      </div>

      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 bg-white">
        <div 
          v-for="(day, index) in calendarDays" 
          :key="index"
          class="min-h-[100px] border-b border-r p-2 relative group transition-colors"
          :class="{
            'bg-gray-50/50 text-gray-400': !day.isCurrentMonth,
            'bg-blue-50/30': day.isToday,
            'cursor-pointer hover:bg-blue-50': props.editor.isEditable
          }"
          @click="handleDayClick(day, $event)"
        >
          <!-- Date Number -->
          <div class="flex justify-between items-start mb-1">
            <span 
              class="text-xs font-medium w-6 h-6 flex items-center justify-center rounded-full"
              :class="{ 'bg-blue-500 text-white': day.isToday }"
            >
              {{ day.date.getDate() }}
            </span>
            <button 
              v-if="props.editor.isEditable && day.isCurrentMonth" 
              class="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-gray-200 rounded text-gray-400"
              @click.stop="addEvent(day, $event)"
            >
              <Plus class="w-3 h-3" />
            </button>
          </div>

          <!-- Events -->
          <div class="flex flex-wrap gap-1 mt-1 px-1">
            <div 
              v-for="(_event, idx) in getEvents(day.dateStr)" 
              :key="idx"
              class="group/event relative"
              @click.stop="viewEvent(day, idx, $event)"
            >
              <div class="p-1 hover:bg-gray-100 rounded cursor-pointer text-blue-500 transition-colors" title="点击查看详情">
                 <FileText class="w-4 h-4" />
              </div>
              <!-- Delete button (small overlay) -->
              <button 
                v-if="props.editor.isEditable"
                @click.stop="removeEvent(day.dateStr, idx)"
                class="absolute -top-1 -right-1 bg-white rounded-full border shadow-sm opacity-0 group-hover/event:opacity-100 hover:text-red-600 p-0.5 z-10"
              >
                <X class="w-2 h-2" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </BaseBlockWrapper>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NodeViewWrapper, nodeViewProps } from '@tiptap/vue-3'
import { ChevronLeft, ChevronRight, Plus, X, FileText } from 'lucide-vue-next'
import EventEditorModal from '../modals/EventEditorModal.vue'
import BaseBlockWrapper from './BaseBlockWrapper.vue'

const props = defineProps(nodeViewProps)

const currentDate = ref(new Date())
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

// Modal States
const showEventModal = ref(false)
const showDeleteModal = ref(false)
const selectedDay = ref<any>(null)
const newEventText = ref('')
const editingEventIndex = ref<number | null>(null)
const itemToDelete = ref<{ dateStr: string; index: number } | null>(null)

const currentMonthLabel = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth() + 1
  return `${year}年 ${month}月`
})

const getEvents = (dateStr: string) => {
  return props.node.attrs.events[dateStr] || []
}

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  
  const startDayOfWeek = firstDayOfMonth.getDay() // 0 (Sun) - 6 (Sat)
  const daysInMonth = lastDayOfMonth.getDate()
  
  const days = []
  
  // Previous month days
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const d = new Date(year, month - 1, prevMonthLastDay - i)
    days.push({
      date: d,
      dateStr: formatDate(d),
      isCurrentMonth: false,
      isToday: isSameDate(d, new Date())
    })
  }
  
  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const d = new Date(year, month, i)
    days.push({
      date: d,
      dateStr: formatDate(d),
      isCurrentMonth: true,
      isToday: isSameDate(d, new Date())
    })
  }
  
  // Next month days to fill grid (6 rows * 7 cols = 42)
  const remainingCells = 42 - days.length
  for (let i = 1; i <= remainingCells; i++) {
    const d = new Date(year, month + 1, i)
    days.push({
      date: d,
      dateStr: formatDate(d),
      isCurrentMonth: false,
      isToday: isSameDate(d, new Date())
    })
  }
  
  return days
})

const formatDate = (date: Date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const isSameDate = (d1: Date, d2: Date) => {
  return d1.getFullYear() === d2.getFullYear() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getDate() === d2.getDate()
}

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

const jumpToToday = () => {
  currentDate.value = new Date()
}

const handleDayClick = (day: any, event: MouseEvent) => {
  if (!props.editor.isEditable) return
  addEvent(day, event)
}

const addEvent = (day: any, _event?: MouseEvent) => {
  if (!props.editor.isEditable) return
  
  selectedDay.value = day
  newEventText.value = ''
  editingEventIndex.value = null
  
  showEventModal.value = true
}

const viewEvent = (day: any, index: any, _event?: MouseEvent) => {
  selectedDay.value = day
  const events = props.node.attrs.events[day.dateStr] || []
  newEventText.value = events[index] || ''
  editingEventIndex.value = index
  
  showEventModal.value = true
}

const closeEventModal = () => {
  showEventModal.value = false
  selectedDay.value = null
  newEventText.value = ''
  editingEventIndex.value = null
}

const saveEvent = (content: string) => {
  if (!content.trim() || !selectedDay.value) return
  if (!props.editor.isEditable) return 

  const dateStr = selectedDay.value.dateStr
  const currentEvents = [...(props.node.attrs.events[dateStr] || [])]
  
  if (editingEventIndex.value !== null) {
    currentEvents[editingEventIndex.value] = content.trim()
  } else {
    currentEvents.push(content.trim())
  }
  
  props.updateAttributes({
    events: {
      ...props.node.attrs.events,
      [dateStr]: currentEvents
    }
  })
  
  closeEventModal()
}

const removeEvent = (dateStr: string, index: any) => {
  if (!props.editor.isEditable) return
  
  itemToDelete.value = { dateStr, index }
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  itemToDelete.value = null
}

const confirmDelete = () => {
  if (!itemToDelete.value) return
  
  const { dateStr, index } = itemToDelete.value
  const currentEvents = [...(props.node.attrs.events[dateStr] || [])]
  currentEvents.splice(index, 1)
  
  const newEvents = { ...props.node.attrs.events }
  if (currentEvents.length === 0) {
    delete newEvents[dateStr]
  } else {
    newEvents[dateStr] = currentEvents
  }
  
  props.updateAttributes({
    events: newEvents
  })
  
  closeDeleteModal()
}
</script>

<style scoped>
.calendar-node {
  width: 100%;
}
</style>