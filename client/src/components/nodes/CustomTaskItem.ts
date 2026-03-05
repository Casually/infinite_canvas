import TaskItem from '@tiptap/extension-task-item'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import TaskItemNode from './TaskItemNode.vue'

export default TaskItem.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      createdAt: {
        default: null,
        parseHTML: element => element.getAttribute('data-created-at'),
        renderHTML: attributes => {
          if (!attributes.createdAt) {
            return {}
          }
          return {
            'data-created-at': attributes.createdAt,
          }
        },
      },
      completedAt: {
        default: null,
        parseHTML: element => element.getAttribute('data-completed-at'),
        renderHTML: attributes => {
          if (!attributes.completedAt) {
            return {}
          }
          return {
            'data-completed-at': attributes.completedAt,
          }
        },
      },
    }
  },

  addNodeView() {
    return VueNodeViewRenderer(TaskItemNode)
  },
})