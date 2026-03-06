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
        @click="runCode"
        title="运行代码"
        :disabled="isRunning"
      >
        <Loader2 v-if="isRunning" class="w-3.5 h-3.5 animate-spin" />
        <Play v-else class="w-3.5 h-3.5" />
      </button>

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
    <div v-if="output || outputError" 
      class="mt-2 rounded text-xs font-mono border max-h-48 overflow-y-auto select-text group/output relative" 
      :class="{
        'bg-red-950/30 border-red-900/50 text-red-200': outputError, 
        'bg-gray-900/50 border-gray-700 text-gray-300': !outputError
      }"
    >
      <div class="flex justify-between items-start p-2">
         <span class="flex-1 whitespace-pre-wrap break-all">{{ output }}</span>
         <div class="flex gap-1 shrink-0 ml-2 sticky top-0">
            <button 
              @click="output = ''; outputError = false" 
              class="p-1 hover:bg-white/10 rounded transition-colors"
              :class="outputError ? 'text-red-300 hover:text-red-100' : 'text-gray-400 hover:text-gray-200'"
              title="清除结果"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
            <button 
              @click="copyOutput"  
              class="p-1 hover:bg-white/10 rounded transition-colors"
              :class="outputError ? 'text-red-300 hover:text-red-100' : 'text-gray-400 hover:text-gray-200'"
              title="复制结果"
            >
              <Check v-if="outputCopied" class="w-3.5 h-3.5" />
              <Copy v-else class="w-3.5 h-3.5" />
            </button>
            <button 
                v-if="outputError" 
                @click="analyzeError" 
                class="p-1 text-purple-400 hover:text-purple-300 hover:bg-purple-900/30 rounded transition-colors flex items-center gap-1"
                title="AI 分析错误"
            >
                <Bot class="w-3.5 h-3.5" />
                <span class="text-[10px]">AI 分析</span>
            </button>
         </div>
      </div>
    </div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { NodeViewContent, nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { computed, ref } from 'vue'
import { Copy, Check, Wand2, Play, Loader2, Bot, Trash2 } from 'lucide-vue-next'
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
  'sql', 'bash', 'json', 'markdown', 'yaml', 'lua'
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
const isRunning = ref(false)
const output = ref('')
const outputError = ref(false)
const outputCopied = ref(false)

const runCode = async () => {
  if (isRunning.value) return
  
  const code = props.node.textContent
  if (!code.trim()) return
  
  isRunning.value = true
  output.value = 'Running...'
  outputError.value = false
  
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        code,
        language: props.node.attrs.language || 'python'
      })
    })
    
    const data = await res.json()
    
    if (!res.ok) {
        output.value = data.message || data.error || 'Execution failed'
        outputError.value = true
    } else {
        if (data.exit_code !== 0) {
             output.value = data.result || data.error
             outputError.value = true
        } else {
             output.value = data.result
        }
    }
  } catch (e: any) {
    output.value = 'Network error: ' + e.message
    outputError.value = true
  } finally {
    isRunning.value = false
  }
}

const analyzeError = () => {
  const analysisPayload = {
    code: props.node.textContent,
    language: props.node.attrs.language,
    error: output.value
  }
  console.log('AI Analysis Request:', JSON.stringify(analysisPayload, null, 2))
  // Here you would typically call an AI service
}

const copyCode = () => {
  const code = props.node.textContent
  navigator.clipboard.writeText(code)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

const copyOutput = () => {
  if (!output.value) return
  navigator.clipboard.writeText(output.value)
  outputCopied.value = true
  setTimeout(() => {
    outputCopied.value = false
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