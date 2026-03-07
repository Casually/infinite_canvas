import { VueRenderer } from '@tiptap/vue-3'
import tippy from 'tippy.js'
import CommandsList from './CommandsList.vue'
import { Heading1, Heading2, Heading3, List, CheckSquare, Table, Image as ImageIcon, PenTool, Link, Globe, BarChart, Video, Music, Code, Minus, Highlighter, Sigma, Info, Calendar, Paperclip, GitGraph, Workflow, BrainCircuit, Clock } from 'lucide-vue-next'

export const getSuggestion = (context: any) => {
  return {
    items: ({ query }: { query: string }) => {
      const items = [
        {
          title: '音乐播放器',
          icon: Music,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'musicPlayer',
              attrs: {
                playlist: [
                  {
                    id: '1',
                    name: '示例歌曲',
                    artist: 'Unknown',
                    url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
                    cover: ''
                  }
                ]
              }
            }).run()
          },
        },
        {
          title: '标题 1',
          icon: Heading1,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run()
          },
        },
        {
          title: '标题 2',
          icon: Heading2,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run()
          },
        },
        {
          title: '标题 3',
          icon: Heading3,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run()
          },
        },
        {
          title: '任务列表',
          icon: CheckSquare,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).toggleTaskList().run()
          },
        },
        {
          title: '无序列表',
          icon: List,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).toggleBulletList().run()
          },
        },
        {
          title: '代码块',
          icon: Code,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).toggleCodeBlock().run()
          },
        },
        {
          title: '分割线',
          icon: Minus,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setHorizontalRule().run()
          },
        },
        {
          title: '高亮文本',
          icon: Highlighter,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).toggleHighlight().run()
          },
        },
        {
          title: '高亮块',
          icon: Info,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).toggleCallout().run()
          },
        },
        {
          title: '公式',
          icon: Sigma,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setMath().run()
          },
        },
        {
          title: '流程图',
          icon: Workflow,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'mermaid',
              attrs: {
                content: 'graph TD\nA[Start] --> B{Is it?}\nB -- Yes --> C[OK]\nC --> D[Rethink]\nD --> B\nB -- No --> E[End]',
                type: 'flowchart'
              }
            }).run()
          },
        },
        {
          title: '思维导图',
          icon: BrainCircuit,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'mermaid',
              attrs: {
                content: 'mindmap\n  root((思维导图))\n    分支1\n    分支2\n      子分支2.1\n      子分支2.2',
                type: 'mindmap'
              }
            }).run()
          },
        },
        {
          title: '甘特图',
          icon: GitGraph,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'mermaid',
              attrs: {
                content: 'gantt\n    title A Gantt Diagram\n    dateFormat  YYYY-MM-DD\n    section Section\n    A task           :a1, 2014-01-01, 30d\n    Another task     :after a1  , 20d\n    section Another\n    Task in sec      :2014-01-12  , 12d\n    another task      : 24d',
                type: 'gantt'
              }
            }).run()
          },
        },
        {
          title: '时间线',
          icon: Clock,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'mermaid',
              attrs: {
                content: 'timeline\n    title History of Social Media Platform\n    2002 : LinkedIn\n    2004 : Facebook\n         : Google\n    2005 : Youtube\n    2006 : Twitter',
                type: 'timeline'
              }
            }).run()
          },
        },
        {
          title: 'Mermaid',
          icon: Workflow,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertContent({
              type: 'mermaid',
              attrs: {
                content: 'graph TD\nA[Start] --> B[End]',
                type: 'flowchart'
              }
            }).run()
          },
        },
        {
          title: '插入表格',
          icon: Table,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
          },
        },
        {
          title: '画板',
          icon: PenTool,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openDrawing()
          },
        },
        {
          title: '插入图片',
          icon: ImageIcon,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openImage()
          },
        },
        {
          title: '插入视频',
          icon: Video,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openVideo()
          },
        },
        {
          title: '插入音频',
          icon: Music,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openAudio()
          },
        },
        {
          title: '插入附件',
          icon: Paperclip,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openFile()
          },
        },
        {
          title: '插入链接',
          icon: Link,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openLink()
          },
        },
        {
          title: '网站卡片',
          icon: Globe,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openWebsiteCard()
          },
        },
        {
          title: '插入图表',
          icon: BarChart,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openECharts()
          },
        },
        {
          title: '甘特图',
          icon: BarChart,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).run()
            context.openECharts(undefined, 'gantt')
          },
        },
        {
          title: '日历',
          icon: Calendar,
          command: ({ editor, range }: any) => {
            editor.chain().focus().deleteRange(range).setCalendar().run()
          },
        },
      ]

      if (!query) return items.slice(0, 20)
      
      const lowerQuery = query.toLowerCase()
      // Fuzzy search: Check if characters of query appear in order in title
      return items.filter(item => {
        const title = item.title.toLowerCase()
        let i = 0, j = 0
        while (i < title.length && j < lowerQuery.length) {
          if (title[i] === lowerQuery[j]) {
            j++
          }
          i++
        }
        return j === lowerQuery.length
      }).slice(0, 20)
    },

    render: () => {
      let component: any
      let popup: any

      return {
        onStart: (props: any) => {
          component = new VueRenderer(CommandsList, {
            props,
            editor: props.editor,
          })

          if (!props.clientRect) {
            return
          }

          popup = tippy('body', {
            getReferenceClientRect: props.clientRect,
            appendTo: () => document.body,
            content: component.element,
            showOnCreate: true,
            interactive: true,
            trigger: 'manual',
            placement: 'bottom-start',
          })
        },

        onUpdate(props: any) {
          component.updateProps(props)

          if (!props.clientRect) {
            return
          }

          popup[0].setProps({
            getReferenceClientRect: props.clientRect,
          })
        },

        onKeyDown(props: any) {
          if (props.event.key === 'Escape') {
            popup[0].hide()
            return true
          }

          return component.ref?.onKeyDown(props)
        },

        onExit() {
          popup[0].destroy()
          component.destroy()
        },
      }
    },
  }
}
