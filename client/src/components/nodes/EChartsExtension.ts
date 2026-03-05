import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import EChartsNode from './EChartsNode.vue'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    echarts: {
      setECharts: (options: { option: any; width?: string; height?: string; dataSourceType?: 'static' | 'api'; dataUrl?: string }) => ReturnType
    }
  }
}

export default Node.create({
  name: 'echarts',

  group: 'block',

  draggable: true,

  atom: true,

  addAttributes() {
    return {
      option: {
        default: {},
        parseHTML: element => {
          const option = element.getAttribute('data-option')
          try {
            return option ? JSON.parse(option) : {}
          } catch (e) {
            return {}
          }
        },
        renderHTML: attributes => {
          return {
            'data-option': JSON.stringify(attributes.option),
          }
        },
      },
      width: {
        default: '100%',
      },
      height: {
        default: '400px',
      },
      dataSourceType: {
        default: 'static',
      },
      dataUrl: {
        default: '',
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="echarts"]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'echarts' })]
  },

  addNodeView() {
    return VueNodeViewRenderer(EChartsNode)
  },

  addCommands() {
    return {
      setECharts:
        (options) =>
        ({ commands }) => {
          return commands.insertContent({
            type: 'echarts',
            attrs: options,
          })
        },
    }
  },
})
