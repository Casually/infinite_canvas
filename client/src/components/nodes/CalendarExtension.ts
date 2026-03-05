import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import CalendarNode from './CalendarNode.vue'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    calendar: {
      setCalendar: () => ReturnType
    }
  }
}

export default Node.create({
  name: 'calendar',

  group: 'block',

  atom: true,

  draggable: true,

  addAttributes() {
    return {
      events: {
        default: {},
        parseHTML: element => {
          const events = element.getAttribute('data-events')
          try {
            return events ? JSON.parse(events) : {}
          } catch (e) {
            return {}
          }
        },
        renderHTML: attributes => {
          return {
            'data-events': JSON.stringify(attributes.events),
          }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="calendar"]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'calendar' })]
  },

  addNodeView() {
    return VueNodeViewRenderer(CalendarNode)
  },

  addCommands() {
    return {
      setCalendar:
        () =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
          })
        },
    }
  },
})
