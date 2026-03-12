/**
 * @vitest-environment happy-dom
 */
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import GroupNode from '../nodes/GroupNode.vue'

describe('GroupNode Interactions', () => {
  it('applies background color from data', () => {
    const wrapper = mount(GroupNode, {
      props: {
        id: '1',
        type: 'group',
        position: { x: 0, y: 0 },
        data: { label: 'Group 1', backgroundColor: '#ff0000' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Group 1',
        dimensions: { width: 300, height: 300 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          NodeResizer: true,
          Handle: true
        }
      }
    })
    
    const node = wrapper.find('.group-node')
    const style = node.attributes('style')
    expect(style).toMatch(/background-color:\s*(#ff0000|rgb\(255,\s*0,\s*0\))/)
  })

  it('applies font styles from data', () => {
    const wrapper = mount(GroupNode, {
      props: {
        id: '1',
        type: 'group',
        position: { x: 0, y: 0 },
        data: { label: 'Group 1', fontSize: 18, fontColor: '#0000ff' },
        selected: false,
        connectable: true,
        draggable: true,
        events: {},
        label: 'Group 1',
        dimensions: { width: 300, height: 300 },
        dragging: false,
        resizing: false,
        zIndex: 1,
      } as any,
      global: {
        provide: {
          saveHistory: vi.fn()
        },
        stubs: {
          NodeResizer: true,
          Handle: true
        }
      }
    })
    
    const node = wrapper.find('.group-node')
    const style = node.attributes('style')
    expect(style).toContain('font-size: 18px')
    expect(style).toMatch(/color:\s*(#0000ff|rgb\(0,\s*0,\s*255\))/)
    
    // Check title color
    const title = wrapper.find('.absolute')
    const titleStyle = title.attributes('style')
    expect(titleStyle).toMatch(/color:\s*(#0000ff|rgb\(0,\s*0,\s*255\))/)
  })
})
