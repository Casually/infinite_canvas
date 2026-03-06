import { mergeAttributes, Node } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import MermaidNode from './MermaidNode.vue'

export default Node.create({
  name: 'mermaid',

  group: 'block',

  atom: true,

  addAttributes() {
    return {
      content: {
        default: 'graph TD\nA[Start] --> B[End]',
      },
      type: {
        default: 'flowchart', // flowchart, mindmap, etc.
      }
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mermaid-diagram',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['mermaid-diagram', mergeAttributes(HTMLAttributes)]
  },

  addNodeView() {
    return VueNodeViewRenderer(MermaidNode)
  },
})
