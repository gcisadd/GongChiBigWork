<template>
  <div class="editor-page-container">
    <!-- 使用 Element Plus Container 构建左右布局，左侧为导航，右侧为 Markdown 编辑器区域 -->
    <el-container class="layout-container">
      <!-- 左侧导航栏区域 -->
      <el-aside width="200px" class="aside-container">
        <el-menu
          :default-active="activeMenu"
          class="aside-menu"
          router
          @select="handleMenuSelect"
        >
          <!-- 文档列表菜单项 -->
          <el-menu-item index="/table">
            <el-icon><Document /></el-icon>
            <span>文档列表</span>
          </el-menu-item>
          <!-- Markdown 编辑器菜单项 -->
          <el-menu-item index="/editor">
            <el-icon><Edit /></el-icon>
            <span>编辑文档</span>
          </el-menu-item>
          <!-- 个人信息菜单项 -->
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>关于</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主内容区域 -->
      <el-main class="main-container">
        <el-card class="editor-card" shadow="always">
          <template #header>
            <div class="card-header">
              <h2>富文本编辑器</h2>
              <div class="header-actions">
                <!-- AI 概括按钮 -->
                <el-button
                  type="warning"
                  :icon="MagicStick"
                  @click="handleAISummary"
                  :loading="aiSummarizing"
                  :disabled="!content || !content.trim()"
                >
                  AI 概括
                </el-button>
                <!-- 顶部工具按钮区 -->
                <el-button type="primary" :icon="Document" @click="handleSave">
                  保存内容
                </el-button>
                <el-button type="success" :icon="Download" @click="handleExportPdf" :loading="exportingPdf">
                  导出PDF
                </el-button>
              </div>
            </div>
          </template>

          <!-- 编辑器和预览区使用左右分栏结构 -->
          <div class="editor-content">
            <!-- Markdown 编辑器区域 -->
            <div class="editor-wrapper">
              <!-- 文档标题输入框 -->
              <el-input
                v-model="title"
                placeholder="请输入文档标题"
                size="large"
                class="title-input"
                clearable
              />

              <!-- Markdown 编辑器 -->
              <!-- 富文本编辑器 -->
              <QuillEditor
                ref="editorRef"
                v-model:content="content"
                content-type="html"
                theme="snow"
                class="rich-text-editor"
                :toolbar="toolbarOptions"
              />

              <!-- AI 概括显示区域 - 放在编辑器下方 -->
              <div v-if="summary" class="ai-summary-section">
                <div class="summary-header">
                  <el-tag type="warning" size="small">
                    <el-icon><MagicStick /></el-icon> AI 概括
                  </el-tag>
                  <el-button
                    type="primary"
                    size="small"
                    text
                    @click="copySummary"
                  >
                    复制
                  </el-button>
                </div>
                <div class="summary-content">
                  {{ summary }}
                </div>
              </div>
            </div>

            <!-- 右侧预览区域 -->
            <div class="preview-wrapper">
              <div class="preview-header">
                <span class="preview-title">实时预览</span>
                <el-tag type="info" size="small">只读</el-tag>
              </div>
              <!-- 预览标题 -->
              <h3 class="preview-document-title">
                {{ title || '（未命名文档）' }}
              </h3>
              <!-- 预览内容区域 -->
              <div
                class="preview-content markdown-body"
                v-html="renderedContent"
              />
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>
<>
<script setup lang="ts">
import { Document, Download, Edit, MagicStick, User } from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentApi } from '../services/api'

/**
 * Markdown 编辑器页面组件
 *
 * 提供一个 Markdown 编辑界面，支持标题输入、Markdown 内容编辑、实时预览，
 * 并集成 Element Plus 的布局和按钮组件，保证与项目整体风格一致。
 *
 * @component
 */

/**
 * 路由实例，用于导航跳转
 */
const router = useRouter()

/**
 * 当前路由信息，用于确定左侧菜单高亮项
 */
const route = useRoute()

/**
 * 当前激活的菜单路径
 *
 * @input 由当前路由变化触发
 * @process 当页面加载或路由变化时更新为当前路径
 * @output 控制左侧导航菜单的高亮状态
 */
const activeMenu = ref<string>('/editor')

/**
 * 文档标题
 *
 * @input 用户在标题输入框中输入的文本
 * @process 双向绑定到 `el-input` 组件
 * @output 提供给预览区域显示文档标题，也可以在保存时提交给后端
 */
const title = ref<string>('')

/**
 * Markdown 内容
 *
 * @input 用户在文本区域中输入的 Markdown 内容
 * @process 双向绑定到 `el-input(type="textarea")` 组件
 * @output 1. 在预览区域中以渲染后的 HTML 形式展示
 *         2. 可在保存时提交给后端 API
 */
const content = ref<string>('')

// AI 概括内容
const summary = ref<string>('')

// AI 概括加载状态
const aiSummarizing = ref<boolean>(false)

// 文档 ID（用于编辑已有文档）
const documentId = ref<number | null>(null)

// 编辑器引用
const editorRef = ref()

// 导出 PDF 加载状态
const exportingPdf = ref<boolean>(false)

// 工具栏配置
const toolbarOptions: any[] = [
  ['bold', 'italic', 'underline', 'strike'],
  [{ header: 1 }, { header: 2 }],
  [{ list: 'ordered' }, { list: 'bullet' }],
  [{ script: 'sub' }, { script: 'super' }],
  [{ indent: '-1' }, { indent: '+1' }],
  [{ direction: 'rtl' }],
  [{ size: ['small', false, 'large', 'huge'] }],
  [{ header: [1, 2, 3, 4, 5, 6, false] }],
  [{ color: [] }, { background: [] }],
  [{ font: [] }],
  [{ align: [] }],
  ['link', 'image', 'code-block'],
  ['clean'],
]

// 空内容占位符
const emptyContentPlaceholder =
  '<p style="color:#909399;">在上方编辑器中输入内容，这里将实时展示预览效果...</p>'

/**
 * 渲染内容为 HTML（富文本直接是 HTML）
 *
 * @input HTML 字符串或空内容
 * @process 如果为空则显示占位符，否则直接返回 HTML
 * @output 渲染后的 HTML 字符串
 */
const renderedContent = computed(() => {
  if (!content.value.trim()) {
    return emptyContentPlaceholder
  }
  return content.value
})

/**
 * 加载文档内容
 */
const loadDocument = async () => {
  const id = route.query.id as string

  if (id) {
    try {
      const doc = await documentApi.getDocument(parseInt(id))
      documentId.value = doc.id
      title.value = doc.title
      content.value = doc.content || ''
      summary.value = doc.summary || ''
    } catch (error) {
      // 加载失败时重置 documentId，确保不会尝试更新不存在的文档
      documentId.value = null
      ElMessage.error('文档加载失败，该文档可能不存在')
    }
  } else {
    // 没有 ID，表示新建文档
    documentId.value = null
  }
}

/**
 * 处理菜单选择
 *
 * @input 用户点击左侧导航菜单项
 * @process 1. 更新当前激活菜单路径
 *          2. 使用 router.push 进行路由跳转
 * @output 导航到对应页面，并更新菜单高亮状态
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  router.push(index)
}

/**
 * 处理保存操作
 *
 * @input 用户点击"保存内容"按钮
 * @process 1. 校验标题和内容是否为空
 *          2. 如果为空给出友好提示
 *          3. 调用后端 API 保存文档
 * @output 显示保存成功或错误消息
 */
const handleSave = async () => {
  console.log('[保存] 开始保存文档, documentId:', documentId.value, 'title:', title.value)

  if (!title.value.trim()) {
    ElMessage.warning('请输入文档标题')
    return
  }

  if (!content.value.trim()) {
    ElMessage.warning('请输入文档内容')
    return
  }

  try {
    // 如果有 documentId，说明是编辑已有文档，否则是新建文档
    if (documentId.value) {
      console.log('[保存] 更新文档, id:', documentId.value)
      await documentApi.updateDocument(documentId.value, {
        title: title.value,
        content: content.value,
      })
      console.log('[保存] 文档更新成功')
      ElMessage.success('文档更新成功')
    } else {
      console.log('[保存] 创建新文档')
      const result = await documentApi.createDocument({
        title: title.value,
        content: content.value,
      })
      console.log('[保存] 文档创建成功, result:', result)
      documentId.value = result.id
      ElMessage.success('文档保存成功')
    }
  } catch (error: any) {
    console.error('[保存] 保存文档失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error('保存文档失败: ' + error.response.data.detail)
    } else {
      ElMessage.error('保存文档失败，请稍后重试')
    }
  }
}

/**
 * 处理导出 PDF 操作
 *
 * @input 用户点击"导出PDF"按钮
 * @process 1. 创建一个包含标题和渲染后内容的 HTML 元素
 *          2. 使用 html2pdf.js 将 HTML 转换为 PDF 并下载
 * @output 触发浏览器下载 PDF 文件
 */
const handleExportPdf = async () => {
  if (!title.value.trim() && !content.value.trim()) {
    ElMessage.warning('文档内容为空，无法导出PDF')
    return
  }

  exportingPdf.value = true

  try {
    // 创建临时的 HTML 容器用于生成 PDF
    const container = document.createElement('div')
    container.style.padding = '20px'
    container.style.fontFamily = 'Arial, sans-serif'

    // 添加标题
    const titleElement = document.createElement('h1')
    titleElement.textContent = title.value || '未命名文档'
    titleElement.style.color = '#303133'
    titleElement.style.marginBottom = '20px'
    titleElement.style.borderBottom = '2px solid #409eff'
    titleElement.style.paddingBottom = '10px'
    container.appendChild(titleElement)

    // 添加内容
    const contentElement = document.createElement('div')
    contentElement.innerHTML = renderedContent.value
    contentElement.style.color = '#303133'
    contentElement.style.lineHeight = '1.6'

    // 添加 Markdown 样式
    const style = document.createElement('style')
    style.textContent = `
      .pdf-content h1, .pdf-content h2, .pdf-content h3, .pdf-content h4, .pdf-content h5, .pdf-content h6 {
        color: #303133;
        margin-top: 16px;
        margin-bottom: 8px;
        font-weight: 600;
      }
      .pdf-content h1 { font-size: 24px; }
      .pdf-content h2 { font-size: 20px; }
      .pdf-content h3 { font-size: 18px; }
      .pdf-content p { margin: 8px 0; }
      .pdf-content ul, .pdf-content ol { padding-left: 20px; }
      .pdf-content li { margin: 4px 0; }
      .pdf-content code {
        background-color: #f5f5f5;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Consolas', monospace;
        font-size: 14px;
      }
      .pdf-content pre {
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 6px;
        overflow-x: auto;
      }
      .pdf-content pre code {
        background: none;
        padding: 0;
      }
      .pdf-content blockquote {
        border-left: 4px solid #409eff;
        margin: 8px 0;
        padding-left: 16px;
        color: #606266;
      }
      .pdf-content a {
        color: #409eff;
        text-decoration: none;
      }
      .pdf-content table {
        border-collapse: collapse;
        width: 100%;
        margin: 8px 0;
      }
      .pdf-content th, .pdf-content td {
        border: 1px solid #dcdfe6;
        padding: 8px;
        text-align: left;
      }
      .pdf-content th {
        background-color: #f5f7fa;
      }
      .pdf-content img {
        max-width: 100%;
        height: auto;
      }
    `
    contentElement.className = 'pdf-content'
    container.appendChild(style)
    container.appendChild(contentElement)

    // 配置 PDF 选项
    const opt: any = {
      margin: 10,
      filename: `${title.value || 'document'}.pdf`,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const }
    }

    // 生成并下载 PDF
    await html2pdf().set(opt).from(container).save()
    ElMessage.success('PDF 导出成功')
  } catch (error) {
    ElMessage.error('导出 PDF 失败，请稍后重试')
  } finally {
    exportingPdf.value = false
  }
}

/**
 * 处理清空内容操作
 *
 * @input 用户点击"清空内容"按钮
 * @process 1. 将标题和内容重置为空
 *          2. 使用 Quill API 清除编辑器内容
 *          3. 使用提示消息告知用户已清空
 * @output 重置页面状态并显示提示
 */
const handleReset = () => {
  title.value = ''
  content.value = ''
  summary.value = ''

  // 使用 Quill API 清除编辑器内容
  if (editorRef.value) {
    const quill = (editorRef.value as any).quill
    if (quill) {
      quill.setContents([])
      quill.setText('')
    }
  }

  ElMessage.info('已清空标题和内容')
}

/**
 * 处理 AI 概括操作
 *
 * @input 用户点击"AI 概括"按钮
 * @process 1. 校验文档内容是否为空
 *          2. 调用后端 API 生成概括
 *          3. 显示概括结果
 * @output 显示 AI 概括结果或错误提示
 */
const handleAISummary = async () => {
  if (!content.value.trim()) {
    ElMessage.warning('请先输入文档内容')
    return
  }

  aiSummarizing.value = true

  try {
    const result = await documentApi.generateAISummary(content.value)
    summary.value = result.summary

    // 如果文档已保存，同时更新数据库中的概括
    if (documentId.value) {
      await documentApi.updateDocumentSummary(documentId.value, result.summary)
    }

    ElMessage.success('AI 概括生成成功')
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('AI 概括失败，请稍后重试')
    }
  } finally {
    aiSummarizing.value = false
  }
}

/**
 * 复制 AI 概括内容到剪贴板
 *
 * @input 用户点击"复制"按钮
 * @process 使用 Clipboard API 复制内容
 * @output 显示复制成功或失败提示
 */
const copySummary = async () => {
  if (!summary.value) {
    ElMessage.warning('没有可复制的概括内容')
    return
  }

  try {
    await navigator.clipboard.writeText(summary.value)
    ElMessage.success('概括内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

/**
 * 组件挂载时初始化菜单高亮状态
 *
 * @input 组件首次挂载
 * @process 将 activeMenu 设置为当前路由路径，确保刷新页面后菜单高亮正确，然后加载文档内容
 * @output 左侧导航栏显示正确的激活项，并加载文档内容（如果有 ID）
 */
onMounted(async () => {
  activeMenu.value = route.path || '/editor'
  // 加载文档内容
  await loadDocument()
})
</script>

<style scoped>
/* 页面根容器：全屏布局，背景与表格页面保持一致 */
.editor-page-container {
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

/* 布局容器：占满整个视口 */
.layout-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

/* 左侧导航栏样式 */
.aside-container {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: hidden;
}

.aside-menu {
  border-right: none;
  height: 100%;
}

/* 右侧主内容区域样式 */
.main-container {
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: hidden;
  box-sizing: border-box;
}

/* 编辑器卡片样式：竖向布局，上方标题，下方内容区域 */
.editor-card {
  border-radius: 8px;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 编辑器和预览整体容器：左右布局 */
.editor-content {
  display: flex;
  flex-direction: row;
  gap: 20px;
  height: calc(100vh - 180px);
}

.editor-wrapper {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.preview-wrapper {
  flex: 1;
  margin-top: 0;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  height: 100%;
  overflow-y: hidden;
}

/* 标题输入框样式 */
.title-input {
  margin-bottom: 12px;
}

/* 富文本编辑器样式 */
.rich-text-editor {
  flex: 1;
  height: 350px;
}

.rich-text-editor :deep(.ql-container) {
  height: calc(100% - 42px);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.preview-title {
  font-size: 14px;
  color: #606266;
}

.preview-document-title {
  margin: 4px 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.preview-content {
  min-height: 120px;
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

/* Markdown 渲染样式 */
.markdown-body {
  color: #24292e;
}

.markdown-body :deep(h1) {
  font-size: 2em;
  font-weight: 600;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(h3) {
  font-size: 1.25em;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(code) {
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 85%;
  margin: 0;
  padding: 0.2em 0.4em;
}

.markdown-body :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  font-size: 85%;
  line-height: 1.45;
  overflow: auto;
  padding: 16px;
}

.markdown-body :deep(pre code) {
  background-color: transparent;
  border: 0;
  display: inline;
  line-height: inherit;
  margin: 0;
  overflow: visible;
  padding: 0;
  word-wrap: normal;
}

.markdown-body :deep(blockquote) {
  border-left: 0.25em solid #dfe2e5;
  color: #6a737d;
  margin: 0;
  padding: 0 1em;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 16px;
  padding-left: 2em;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  border-spacing: 0;
  display: block;
  margin-bottom: 16px;
  margin-top: 0;
  overflow: auto;
  width: 100%;
}

.markdown-body :deep(table th),
.markdown-body :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
}

.markdown-body :deep(table tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
  box-sizing: content-box;
}

.markdown-body :deep(hr) {
  background-color: #e1e4e8;
  border: 0;
  height: 0.25em;
  margin: 24px 0;
  padding: 0;
}

/* 让预览区内的图片自适应宽度，避免撑破布局 */
.preview-content img {
  max-width: 100%;
  height: auto;
}

/* AI 概括区域样式 */
.ai-summary-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #dcdfe6;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.summary-content {
  padding: 12px;
  background-color: #fdf6ec;
  border-radius: 6px;
  border-left: 4px solid #e6a23c;
  color: #303133;
  font-size: 14px;
  line-height: 1.6;
  max-height: 200px;
  overflow-y: hidden;
}

/* 响应式设计：在窄屏幕上调整内边距 */
@media (max-width: 768px) {
  .main-container {
    padding: 10px;
  }

  .editor-card {
    min-height: auto;
  }

  .editor-content {
    flex-direction: column;
  }

  .preview-wrapper {
    max-height: none;
  }
}
</style>
