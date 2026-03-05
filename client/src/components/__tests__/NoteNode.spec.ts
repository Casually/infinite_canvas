/**
 * @vitest-environment happy-dom
 */
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import NoteNode from '../nodes/NoteNode.vue'

const focusSpy = vi.fn()
const MockEditor = {
  template: '<div></div>',
  methods: {
    focus: focusSpy
  }
}

vi.mock('@vue-flow/node-resizer', () => ({
  NodeResizer: { template: '<div><slot /></div>' },
  NodeResizeControl: { template: '<div></div>' }
}))

describe('NoteNode Interactions', () => {
  // Fix 1 & 5: Styles (Color, Border)
  it('applies border width and background color from data', () => {
    const wrapper = mount(NoteNode, {
      props: {
        id: '1',
        type: 'note',
        position: { x: 0, y: 0 },
        data: { label: 'Test', borderWidth: 5, backgroundColor: '#ff0000' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Test',
        dimensions: { width: 100, height: 100 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          TiptapEditor: MockEditor,
          Handle: true,
          NodeResizer: true,
          NodeResizeControl: true,
          Minimize2: true,
          Maximize2: true,
          ChevronUp: true,
          ChevronDown: true
        }
      }
    })
    
    const node = wrapper.find('.note-node')
    const style = node.attributes('style')
    expect(style).toContain('border-width: 5px')
    expect(style).toMatch(/background-color:\s*(#ff0000|rgb\(255,\s*0,\s*0\))/)
  })

  it('applies font styles from data', () => {
    const wrapper = mount(NoteNode, {
      props: {
        id: '1',
        type: 'note',
        position: { x: 0, y: 0 },
        data: { label: 'Test', fontSize: 20, fontColor: '#00ff00' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Test',
        dimensions: { width: 100, height: 100 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          TiptapEditor: MockEditor,
          Handle: true,
          NodeResizer: true,
          NodeResizeControl: true,
          Minimize2: true,
          Maximize2: true,
          ChevronUp: true,
          ChevronDown: true
        }
      }
    })
    
    const node = wrapper.find('.note-node')
    const style = node.attributes('style')
    expect(style).toContain('font-size: 20px')
    expect(style).toMatch(/color:\s*(#00ff00|rgb\(0,\s*255,\s*0\))/)
  })

  // Fix 2: Double Click
  it('enters edit mode on double click', async () => {
    const wrapper = mount(NoteNode, {
      props: {
        id: '1',
        type: 'note',
        position: { x: 0, y: 0 },
        data: { label: 'Test' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Test',
        dimensions: { width: 100, height: 100 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          TiptapEditor: MockEditor,
          Handle: true,
          NodeResizer: true,
          NodeResizeControl: true,
          Minimize2: true,
          Maximize2: true,
          ChevronUp: true,
          ChevronDown: true
        }
      }
    })
    
    await wrapper.find('.note-node').trigger('dblclick')
    
    expect(focusSpy).toHaveBeenCalled()
  })

  // Fix 3: Connections
  it('renders handles on all 4 sides', () => {
    const wrapper = mount(NoteNode, {
      props: {
        id: '1',
        type: 'note',
        position: { x: 0, y: 0 },
        data: { label: 'Test' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Test',
        dimensions: { width: 100, height: 100 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          TiptapEditor: MockEditor,
          Handle: {
            template: '<div class="vue-flow__handle"></div>'
          },
          NodeResizer: true,
          NodeResizeControl: true,
          Minimize2: true,
          Maximize2: true,
          ChevronUp: true,
          ChevronDown: true
        }
      }
    })
    
    const handles = wrapper.findAll('.vue-flow__handle')
    // Dynamic handles: 4 positions, each has source and target
    // They are hidden by default (opacity: 0)
    expect(handles.length).toBe(8)
  })
})
