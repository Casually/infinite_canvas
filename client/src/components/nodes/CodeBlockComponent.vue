<template>
  <node-view-wrapper class="code-block relative group">
    <div class="absolute right-2 top-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
      <select 
        contenteditable="false" 
        v-model="selectedLanguage" 
        class="text-xs bg-gray-800 text-gray-300 border border-gray-600 rounded px-1 py-0.5 outline-none cursor-pointer"
      >
        <option :value="null">auto</option>
        <option disabled>---</option>
        <option v-for="lang in languages" :key="lang" :value="lang">
          {{ lang }}
        </option>
      </select>
      
      <button 
        class="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        @click="formatCode"
        title="格式化代码"
      >
        <Check v-if="formatted" class="w-3.5 h-3.5 text-green-400" />
        <Wand2 v-else class="w-3.5 h-3.5" />
      </button>

      <button 
        class="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        @click="copyCode"
        title="复制代码"
      >
        <Check v-if="copied" class="w-3.5 h-3.5 text-green-400" />
        <Copy v-else class="w-3.5 h-3.5" />
      </button>
    </div>
    <pre><node-view-content as="code" /></pre>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { NodeViewContent, nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { computed, ref } from 'vue'
import { Copy, Check, Wand2 } from 'lucide-vue-next'
import * as prettier from 'prettier/standalone'
import * as prettierPluginBabel from 'prettier/plugins/babel'
import * as prettierPluginEstree from 'prettier/plugins/estree'
import * as prettierPluginHtml from 'prettier/plugins/html'
import * as prettierPluginMarkdown from 'prettier/plugins/markdown'
import * as prettierPluginPostcss from 'prettier/plugins/postcss'
import * as prettierPluginYaml from 'prettier/plugins/yaml'

const props = defineProps(nodeViewProps)

const languages = [
  'css', 'javascript', 'typescript', 'html', 'python', 
  'java', 'c', 'cpp', 'csharp', 'go', 'rust', 'php', 
  'sql', 'bash', 'json', 'markdown', 'yaml'
]

const selectedLanguage = computed({
  get() {
    return props.node.attrs.language
  },
  set(language: string | null) {
    props.updateAttributes({ language })
  }
})

const copied = ref(false)
const formatted = ref(false)

const copyCode = () => {
  const code = props.node.textContent
  navigator.clipboard.writeText(code)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

const formatCode = async () => {
  const code = props.node.textContent
  const language = props.node.attrs.language || 'javascript'
  
  let parser = 'babel'
  let plugins: any[] = [prettierPluginBabel, prettierPluginEstree]

  switch (language) {
    case 'javascript':
    case 'js':
    case 'typescript':
    case 'ts':
      parser = 'babel'
      break
    case 'css':
      parser = 'css'
      plugins = [prettierPluginPostcss]
      break
    case 'json':
      parser = 'json'
      plugins = [prettierPluginBabel, prettierPluginEstree]
      break
    case 'html':
      parser = 'html'
      plugins = [prettierPluginHtml]
      break
    case 'markdown':
      parser = 'markdown'
      plugins = [prettierPluginMarkdown]
      break
    case 'yaml':
      parser = 'yaml'
      plugins = [prettierPluginYaml]
      break
    default:
      // Try babel as fallback or skip
      if (['java', 'c', 'cpp', 'python', 'go', 'rust', 'php', 'sql', 'bash'].includes(language)) {
         // Prettier standalone doesn't support these by default without huge plugins
         // We skip formatting for now
         return
      }
  }

  try {
    const formattedCode = await prettier.format(code, {
      parser,
      plugins,
      useTabs: false,
      tabWidth: 2,
      printWidth: 80,
      semi: false,
      singleQuote: true,
    })
    
    // Update content
    // Tiptap way to update node content is tricky from NodeView.
    // We can't just set textContent.
    // We need to use updateAttributes? No, content is not an attribute.
    // We need to dispatch a transaction.
    if (props.updateAttributes && props.deleteNode) {
       const pos = props.getPos()
       if (typeof pos === 'number') {
          // Use chain command to safely update content
          // First clear the content, then insert new content
          // Or just replace the whole node? No, keep attributes.
          
          // Correct way to replace text content in a node:
          const tr = props.editor.state.tr
          const start = pos + 1
          const end = pos + props.node.nodeSize - 1
          
          // Check if range is valid
          if (start < end) {
             tr.delete(start, end)
          }
          // Insert the formatted code
          tr.insertText(formattedCode, start)
          
          props.editor.view.dispatch(tr)
       }
    }
    
    formatted.value = true
    setTimeout(() => {
      formatted.value = false
    }, 2000)
  } catch (e) {
    console.error('Format failed', e)
  }
}
</script>

<style scoped>
.code-block {
  position: relative;
}

.code-block pre {
  background: #0d0d0d;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin: 0;
}

.code-block code {
  color: inherit;
  padding: 0;
  background: none;
  font-size: 0.8rem;
}
</style>