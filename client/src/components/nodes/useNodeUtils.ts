import type { NodeViewProps } from '@tiptap/vue-3'

export function useNodeUtils(props: NodeViewProps) {
  const addParagraphAfter = (e: MouseEvent) => {
    e.stopPropagation()
    
    if (!props.editor.isEditable) return

    const { state, dispatch } = props.editor.view
    const pos = props.getPos()
    
    if (typeof pos !== 'number') return

    // Calculate the position after the node
    const afterPos = pos + props.node.nodeSize
    
    // Ensure we don't exceed document size
    const targetPos = Math.min(afterPos, state.doc.content.size)
    
    // Create a transaction to insert a paragraph
    const tr = state.tr.insert(targetPos, state.schema.nodes.paragraph.create())
    
    // Apply transaction
    dispatch(tr)
    
    // Set focus to the new paragraph (targetPos + 1 is inside the new paragraph)
    props.editor.commands.setTextSelection(targetPos + 1)
    props.editor.commands.focus()
  }

  return {
    addParagraphAfter
  }
}
