import { ref } from 'vue'

export interface Shortcut {
  id: string
  label: string
  keys: string[] // e.g., ['Meta', 's'] or ['Control', 's'] or ['n']
  isCtrlOrMeta?: boolean // If true, matches either Ctrl or Meta (for cross-platform Mod key)
}

const STORAGE_KEY = 'canvas_shortcuts'

const defaultShortcuts: Shortcut[] = [
  { id: 'save', label: '保存画布', keys: ['s'], isCtrlOrMeta: true },
  { id: 'group', label: '所选节点编组', keys: ['g'], isCtrlOrMeta: true },
  { id: 'search', label: '搜索节点', keys: ['f'], isCtrlOrMeta: true },
  { id: 'newNode', label: '新建节点', keys: ['n'], isCtrlOrMeta: false },
  { id: 'delete', label: '删除节点', keys: ['Delete'], isCtrlOrMeta: false },
  { id: 'undo', label: '撤销', keys: ['z'], isCtrlOrMeta: true },
  { id: 'redo', label: '重做', keys: ['y'], isCtrlOrMeta: true },
  { id: 'copy', label: '复制', keys: ['c'], isCtrlOrMeta: true },
  { id: 'paste', label: '粘贴', keys: ['v'], isCtrlOrMeta: true },
  { id: 'toggleLock', label: '锁定/解锁画布', keys: ['Shift', 'l'], isCtrlOrMeta: true },
]

const shortcuts = ref<Shortcut[]>(JSON.parse(JSON.stringify(defaultShortcuts)))

export function useShortcuts() {
  // Load from local storage
  const loadShortcuts = () => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        // Merge with defaults to ensure all keys exist (in case of updates)
        shortcuts.value = defaultShortcuts.map(def => {
          const found = parsed.find((p: Shortcut) => p.id === def.id)
          return found || def
        })
      } catch (e) {
        console.error('Failed to parse shortcuts', e)
      }
    }
  }

  // Save to local storage
  const saveShortcuts = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(shortcuts.value))
  }

  // Reset to defaults
  const resetShortcuts = () => {
    shortcuts.value = JSON.parse(JSON.stringify(defaultShortcuts))
    saveShortcuts()
  }

  // Check if an event matches a shortcut
  const matchShortcut = (e: KeyboardEvent, actionId: string): boolean => {
    const shortcut = shortcuts.value.find(s => s.id === actionId)
    if (!shortcut) return false

    const keys = shortcut.keys
    if (keys.length === 0) return false

    // Check modifiers
    const hasCtrl = e.ctrlKey
    const hasMeta = e.metaKey
    const hasShift = e.shiftKey
    const hasAlt = e.altKey

    // Helper to check main key (case insensitive)
    const mainKey = keys[keys.length - 1].toLowerCase()
    const eventKey = e.key.toLowerCase()

    // Special handling for 'Delete' and 'Backspace' which are often interchangeable for delete action
    if (actionId === 'delete') {
      // If the configured key is Delete, also allow Backspace if it's not explicitly used elsewhere?
      // Or just strictly follow configuration. 
      // Current default uses 'Delete'.
      // If the event key is Backspace, we might want to return true if the config is Delete?
      // Let's stick to strict config for now, but the default config can have multiple alternatives if we supported it.
      // For now, let's hardcode a small exception for delete: if config is Delete, allow Backspace too?
      // Or better: The config logic below will check exact match.
      // If we want to support multiple keys for one action, we'd need keys to be string[][].
      // For simplicity, let's keep it simple.
      // However, the original code allowed Backspace.
      if (shortcut.keys.includes('Delete') && e.key === 'Backspace') return true
    }

    // Check modifier requirements
    // If isCtrlOrMeta is true, we expect Ctrl OR Meta to be pressed
    if (shortcut.isCtrlOrMeta) {
      if (!(hasCtrl || hasMeta)) return false
    } else {
      // If not required, we generally expect them NOT to be pressed, 
      // unless they are part of the keys array (e.g. ['Shift', 'N'])
      // But for simple letters like 'n', usually means no modifiers.
      // Let's check if 'Ctrl' or 'Meta' or 'Shift' or 'Alt' is in the keys array
      const definedModifiers = keys.slice(0, -1).map(k => k.toLowerCase())
      
      // Check Ctrl/Meta
      if (hasCtrl && !definedModifiers.includes('control') && !definedModifiers.includes('ctrl')) return false
      if (hasMeta && !definedModifiers.includes('meta') && !definedModifiers.includes('cmd')) return false
      // Check Shift (allow shift for letters if they are uppercase? No, e.key is case sensitive usually)
      if (hasShift && !definedModifiers.includes('shift')) return false
      if (hasAlt && !definedModifiers.includes('alt')) return false
    }

    // Check the main key
    // For letters, e.key matches the case.
    // If we pressed 's' with Ctrl, e.key is 's'.
    return eventKey === mainKey
  }

  // Format shortcut for display
  const formatShortcut = (shortcut: Shortcut): string => {
    const parts = []
    if (shortcut.isCtrlOrMeta) {
      parts.push('Ctrl/Cmd')
    }
    // Add other modifiers if we support them explicitly in keys array (e.g. Shift)
    shortcut.keys.slice(0, -1).forEach(k => {
      if (['control', 'meta'].includes(k.toLowerCase())) return // handled by isCtrlOrMeta
      parts.push(k)
    })
    
    // Add main key
    const mainKey = shortcut.keys[shortcut.keys.length - 1]
    parts.push(mainKey.toUpperCase())
    
    return parts.join(' + ')
  }

  const updateShortcut = (id: string, newKeys: string[], isCtrlOrMeta: boolean) => {
    const index = shortcuts.value.findIndex(s => s.id === id)
    if (index !== -1) {
      shortcuts.value[index] = { ...shortcuts.value[index], keys: newKeys, isCtrlOrMeta }
      saveShortcuts()
    }
  }

  // Initialize
  loadShortcuts()

  return {
    shortcuts,
    matchShortcut,
    formatShortcut,
    updateShortcut,
    resetShortcuts
  }
}
