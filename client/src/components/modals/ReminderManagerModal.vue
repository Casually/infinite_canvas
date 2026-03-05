<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="font-bold text-lg">{{ isEditing ? (editingId ? '编辑提醒' : '新建提醒') : '定时提醒管理' }}</h3>
        <button @click="$emit('close')" class="p-1 hover:bg-gray-100 rounded text-gray-500">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- List View -->
      <div v-if="!isEditing" class="flex-1 overflow-y-auto p-4">
        <div v-if="reminders.length === 0" class="text-center text-gray-500 py-8">
          暂无提醒任务
        </div>
        <div v-else class="space-y-3">
          <div 
            v-for="reminder in reminders" 
            :key="reminder.id"
            class="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
            :class="{ 'opacity-60': !reminder.enabled }"
          >
            <div class="flex justify-between items-start mb-2">
              <div class="flex items-center gap-2">
                <span 
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :class="reminder.type === 'once' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
                >
                  {{ reminder.type === 'once' ? '单次' : '周期' }}
                </span>
                <span class="text-xs text-gray-500">
                   {{ formatTime(reminder) }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  @click="toggleEnable(reminder)"
                  class="p-1 rounded hover:bg-gray-100"
                  :title="reminder.enabled ? '暂停' : '启用'"
                >
                  <component :is="reminder.enabled ? Pause : Play" class="w-4 h-4 text-gray-600" />
                </button>
                <button @click="editReminder(reminder)" class="p-1 rounded hover:bg-gray-100">
                  <Edit2 class="w-4 h-4 text-gray-600" />
                </button>
                <button @click="removeReminder(reminder.id)" class="p-1 rounded hover:bg-red-50 text-red-600">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
            <p class="text-sm text-gray-800 line-clamp-2">{{ reminder.content }}</p>
            <div class="mt-2 flex items-center gap-2 text-xs text-gray-500">
              <component :is="reminder.notifyMode === 'browser' ? Bell : AppWindow" class="w-3 h-3" />
              {{ reminder.notifyMode === 'browser' ? '浏览器通知' : '页面弹窗' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Edit View -->
      <div v-else class="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">提醒内容</label>
          <textarea 
            v-model="form.content" 
            rows="3"
            class="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            placeholder="请输入提醒内容..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">提醒类型</label>
            <select v-model="form.type" class="w-full px-3 py-2 border rounded-md outline-none">
              <option value="once">单次提醒</option>
              <option value="periodic">周期提醒</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">通知方式</label>
            <select v-model="form.notifyMode" class="w-full px-3 py-2 border rounded-md outline-none">
              <option value="page">页面弹窗</option>
              <option value="browser">浏览器通知</option>
            </select>
          </div>
        </div>

        <div v-if="form.type === 'once'">
          <label class="block text-sm font-medium text-gray-700 mb-1">触发时间</label>
          <input 
            type="datetime-local" 
            v-model="form.datetime"
            class="w-full px-3 py-2 border rounded-md outline-none"
          />
        </div>

        <div v-if="form.type === 'periodic'">
          <label class="block text-sm font-medium text-gray-700 mb-1">循环间隔</label>
          <div class="flex gap-2">
            <input 
              type="number" 
              v-model.number="form.intervalValue"
              min="1"
              class="flex-1 px-3 py-2 border rounded-md outline-none"
            />
            <select v-model="form.intervalUnit" class="w-24 px-3 py-2 border rounded-md outline-none">
              <option value="seconds">秒</option>
              <option value="minutes">分钟</option>
              <option value="hours">小时</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t bg-gray-50 flex justify-end gap-3">
        <template v-if="!isEditing">
          <button 
            @click="startAdd"
            class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus class="w-4 h-4" />
            新建提醒
          </button>
        </template>
        <template v-else>
          <button 
            @click="isEditing = false"
            class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors"
          >
            取消
          </button>
          <button 
            @click="saveReminder"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            :disabled="!isValid"
            :class="{ 'opacity-50 cursor-not-allowed': !isValid }"
          >
            保存
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { X, Plus, Trash2, Edit2, Bell, AppWindow, Play, Pause } from 'lucide-vue-next'
import { useReminders, type Reminder } from '../../composables/useReminders'

defineEmits(['close'])

const { reminders, addReminder, removeReminder, updateReminder, requestNotificationPermission } = useReminders()

const isEditing = ref(false)
const editingId = ref<string | null>(null)

interface ReminderForm {
  content: string
  type: 'once' | 'periodic'
  notifyMode: 'browser' | 'page'
  datetime: string
  intervalValue: number
  intervalUnit: 'seconds' | 'minutes' | 'hours'
}

const form = reactive<ReminderForm>({
  content: '',
  type: 'once',
  notifyMode: 'page',
  datetime: '',
  intervalValue: 30,
  intervalUnit: 'minutes'
})

const isValid = computed(() => {
  if (!form.content.trim()) return false
  if (form.type === 'once' && !form.datetime) return false
  if (form.type === 'periodic' && form.intervalValue <= 0) return false
  return true
})

const formatTime = (reminder: Reminder) => {
  if (reminder.type === 'once') {
    return reminder.targetTime ? new Date(reminder.targetTime).toLocaleString() : 'Invalid Date'
  } else {
    const ms = reminder.interval || 0
    if (ms >= 3600000) return `每 ${ms / 3600000} 小时`
    if (ms >= 60000) return `每 ${ms / 60000} 分钟`
    return `每 ${ms / 1000} 秒`
  }
}

const toggleEnable = (reminder: Reminder) => {
  updateReminder(reminder.id, { enabled: !reminder.enabled })
}

const startAdd = () => {
  editingId.value = null
  form.content = ''
  form.type = 'once'
  form.notifyMode = 'page'
  
  // Default to 1 hour later
  const now = new Date()
  now.setHours(now.getHours() + 1)
  now.setMinutes(0)
  form.datetime = toDateTimeLocal(now)
  
  form.intervalValue = 30
  form.intervalUnit = 'minutes'
  
  isEditing.value = true
}

const editReminder = (reminder: Reminder) => {
  editingId.value = reminder.id
  form.content = reminder.content
  form.type = reminder.type
  form.notifyMode = reminder.notifyMode
  
  if (reminder.type === 'once' && reminder.targetTime) {
    form.datetime = toDateTimeLocal(new Date(reminder.targetTime))
  }
  
  if (reminder.type === 'periodic' && reminder.interval) {
    if (reminder.interval % 3600000 === 0) {
      form.intervalValue = reminder.interval / 3600000
      form.intervalUnit = 'hours'
    } else if (reminder.interval % 60000 === 0) {
      form.intervalValue = reminder.interval / 60000
      form.intervalUnit = 'minutes'
    } else {
      form.intervalValue = reminder.interval / 1000
      form.intervalUnit = 'seconds'
    }
  }
  
  isEditing.value = true
}

const saveReminder = async () => {
  if (!isValid.value) return
  
  if (form.notifyMode === 'browser') {
    const granted = await requestNotificationPermission()
    if (!granted) {
       // Proceed anyway, fallback logic handles it or user is aware
    }
  }
  
  const reminderData: any = {
    content: form.content,
    type: form.type,
    notifyMode: form.notifyMode,
    enabled: true
  }
  
  if (form.type === 'once') {
    reminderData.targetTime = new Date(form.datetime).getTime()
  } else {
    let multiplier = 1000
    if (form.intervalUnit === 'minutes') multiplier = 60000
    if (form.intervalUnit === 'hours') multiplier = 3600000
    reminderData.interval = form.intervalValue * multiplier
  }
  
  if (editingId.value) {
    updateReminder(editingId.value, reminderData)
  } else {
    addReminder(reminderData)
  }
  
  isEditing.value = false
}

// Helper to format Date to datetime-local string
const toDateTimeLocal = (date: Date) => {
  const pad = (n: number) => n < 10 ? '0' + n : n
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>