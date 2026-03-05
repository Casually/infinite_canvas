import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import CalloutNode from './CalloutNode.vue'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    callout: {
      setCallout: (attributes?: { type: 'info' | 'warning' | 'error' | 'success' | 'tip' | 'question' | 'important' | 'bug' }) => ReturnType
      toggleCallout: (attributes?: { type: 'info' | 'warning' | 'error' | 'success' | 'tip' | 'question' | 'important' | 'bug' }) => ReturnType
    }
  }
}

export default Node.create({
  name: 'callout',

  group: 'block',

  content: 'block+',

  draggable: true,

  addAttributes() {
    return {
      type: {
        default: 'info',
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="callout"]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'callout' }), 0]
  },

  addNodeView() {
    return VueNodeViewRenderer(CalloutNode)
  },

  addCommands() {
    return {
      setCallout: (attributes) => ({ commands }) => {
        return commands.wrapIn(this.name, attributes)
      },
      toggleCallout: (attributes) => ({ commands }) => {
        return commands.toggleWrap(this.name, attributes)
      },
    }
  },
})
