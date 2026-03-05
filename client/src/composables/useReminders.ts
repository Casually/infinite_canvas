import { ref, watch } from 'vue'
import { useToast } from './useToast'

export interface Reminder {
  id: string
  type: 'once' | 'periodic'
  content: string
  notifyMode: 'browser' | 'page'
  enabled: boolean
  
  // For one-time
  targetTime?: number // timestamp
  executed?: boolean
  
  // For periodic
  interval?: number // milliseconds
  lastRun?: number // timestamp
  
  createdAt: number
}

const STORAGE_KEY = 'canvas_reminders'
const reminders = ref<Reminder[]>([])
const { addToast } = useToast()

// Load from storage
try {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    reminders.value = JSON.parse(stored)
  }
} catch (e) {
  console.error('Failed to load reminders', e)
}

// Watch and save
watch(reminders, (newVal) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
}, { deep: true })

let timer: number | null = null

export function useReminders() {
  
  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      addToast('当前浏览器不支持桌面通知', 'error')
      return false
    }
    
    if (Notification.permission === 'granted') {
      return true
    }
    
    const permission = await Notification.requestPermission()
    return permission === 'granted'
  }

  const checkReminders = () => {
    const now = Date.now()
    
    reminders.value.forEach(reminder => {
      if (!reminder.enabled) return
      
      let shouldTrigger = false
      
      if (reminder.type === 'once') {
        if (reminder.targetTime && now >= reminder.targetTime && !reminder.executed) {
          shouldTrigger = true
          reminder.executed = true
          reminder.enabled = false // Disable after running once
        }
      } else if (reminder.type === 'periodic') {
        if (reminder.interval) {
          const lastRun = reminder.lastRun || reminder.createdAt
          if (now - lastRun >= reminder.interval) {
            shouldTrigger = true
            reminder.lastRun = now
          }
        }
      }
      
      if (shouldTrigger) {
        triggerNotification(reminder)
      }
    })
  }
  
  const triggerNotification = (reminder: Reminder) => {
    if (reminder.notifyMode === 'page') {
      addToast(`🔔 ${reminder.content}`, 'info', 10000) // Longer duration for reminders
    } else if (reminder.notifyMode === 'browser') {
      if (Notification.permission === 'granted') {
        new Notification('无限画布提醒', {
          body: reminder.content,
          icon: '/favicon.ico' // Assuming favicon exists
        })
      } else {
        // Fallback to page toast if permission denied
        addToast(`🔔 ${reminder.content} (桌面通知未授权)`, 'info', 10000)
      }
    }
  }

  const startTimer = () => {
    if (timer) return
    // Check every second for precision
    timer = window.setInterval(checkReminders, 1000)
  }

  const stopTimer = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }
  
  const addReminder = (reminder: Omit<Reminder, 'id' | 'createdAt' | 'executed' | 'lastRun'>) => {
    const newReminder: Reminder = {
      ...reminder,
      id: crypto.randomUUID(),
      createdAt: Date.now(),
      executed: false,
      lastRun: Date.now() // Start periodic interval from now
    }
    reminders.value.push(newReminder)
  }
  
  const removeReminder = (id: string) => {
    const index = reminders.value.findIndex(r => r.id === id)
    if (index !== -1) {
      reminders.value.splice(index, 1)
    }
  }
  
  const updateReminder = (id: string, updates: Partial<Reminder>) => {
    const reminder = reminders.value.find(r => r.id === id)
    if (reminder) {
      Object.assign(reminder, updates)
      // Reset periodic timer if interval changed
      if (updates.interval || updates.enabled === true) {
        reminder.lastRun = Date.now()
      }
    }
  }

  return {
    reminders,
    addReminder,
    removeReminder,
    updateReminder,
    startTimer,
    stopTimer,
    requestNotificationPermission
  }
}
