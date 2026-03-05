<template>
  <div class="items bg-white border rounded shadow-lg overflow-hidden py-1 min-w-[150px]">
    <button
      class="item w-full text-left px-3 py-1.5 hover:bg-gray-100 text-sm flex items-center space-x-2"
      :class="{ 'bg-gray-100': index === selectedIndex }"
      v-for="(item, index) in items"
      :key="index"
      @click="selectItem(index)"
    >
      <component :is="item.icon" v-if="item.icon" class="w-4 h-4 text-gray-500" />
      <span>{{ item.title }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  items: any[]
  command: any
}>()

const selectedIndex = ref(0)

watch(() => props.items, () => {
  selectedIndex.value = 0
})

const onKeyDown = ({ event }: { event: KeyboardEvent }) => {
  if (event.key === 'ArrowUp') {
    if (props.items.length === 0) return false
    upHandler()
    return true
  }

  if (event.key === 'ArrowDown') {
    if (props.items.length === 0) return false
    downHandler()
    return true
  }

  if (event.key === 'Enter') {
    if (props.items.length === 0) {
      return false
    }
    enterHandler()
    return true
  }

  return false
}

const upHandler = () => {
  selectedIndex.value = ((selectedIndex.value + props.items.length) - 1) % props.items.length
}

const downHandler = () => {
  selectedIndex.value = (selectedIndex.value + 1) % props.items.length
}

const enterHandler = () => {
  selectItem(selectedIndex.value)
}

const selectItem = (index: number) => {
  const item = props.items[index]
  if (item) {
    props.command(item)
  }
}

defineExpose({
  onKeyDown,
})
</script>
