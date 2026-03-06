import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'

export const CustomTableCell = TableCell.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      colwidth: {
        default: null,
        parseHTML: element => {
          const colwidth = element.getAttribute('data-colwidth')
          return colwidth ? colwidth.split(',').map(w => parseInt(w, 10)) : null
        },
        renderHTML: attributes => {
          if (!attributes.colwidth) {
            return {}
          }
          const width = attributes.colwidth.reduce((a: number, b: number) => a + b, 0)
          return {
            'data-colwidth': attributes.colwidth,
            style: `width: ${width}px`,
          }
        },
      },
      backgroundColor: {
        default: null,
        parseHTML: element => element.getAttribute('data-background-color'),
        renderHTML: attributes => {
          if (!attributes.backgroundColor) {
            return {}
          }
          return {
            'data-background-color': attributes.backgroundColor,
            style: `background-color: ${attributes.backgroundColor}`,
          }
        },
      },
    }
  },
})

export { Table, TableRow, TableHeader }
