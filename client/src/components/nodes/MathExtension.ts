import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import MathNode from './MathNode.vue'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    math: {
      setMath: (attributes?: { latex: string }) => ReturnType
    }
  }
}

export default Node.create({
  name: 'math',

  group: 'inline',

  inline: true,

  atom: true,

  addAttributes() {
    return {
      latex: {
        default: 'E=mc^2',
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-type="math"]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes(HTMLAttributes, { 'data-type': 'math' })]
  },

  addNodeView() {
    return VueNodeViewRenderer(MathNode)
  },

  addCommands() {
    return {
      setMath: (attributes) => ({ commands }) => {
        return commands.insertContent({
          type: this.name,
          attrs: attributes,
        })
      },
    }
  },
})
