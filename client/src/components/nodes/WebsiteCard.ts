import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import WebsiteCardNode from './WebsiteCardNode.vue'

export default Node.create({
  name: 'websiteCard',

  group: 'block',

  draggable: true,

  atom: true,

  addAttributes() {
    return {
      url: {
        default: null,
      },
      title: {
        default: null,
      },
      description: {
        default: null,
      },
      image: {
        default: null,
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'website-card',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['website-card', mergeAttributes(HTMLAttributes)]
  },

  addNodeView() {
    return VueNodeViewRenderer(WebsiteCardNode)
  },
})