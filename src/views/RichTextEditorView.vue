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
            <span>Markdown 编辑器</span>
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
              <h2>Markdown 编辑器</h2>
              <div class="header-actions">
                <!-- 顶部工具按钮区 -->
                <el-button type="primary" :icon="Document" @click="handleSave">
                  保存内容
                </el-button>
                <el-button type="success" :icon="Refresh" @click="handleReset">
                  清空内容
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
              <el-input
                v-model="content"
                type="textarea"
                :rows="15"
                placeholder="请输入 Markdown 内容...
# 支持的语法
- 标题：# H1, ## H2, ### H3
- 加粗：**bold**
- 斜体：*italic*
- 链接：[text](url)
- 代码：`code` 或 ```code block```
- 列表：- item 或 1. item
- 引用：> quote"
                class="markdown-editor"
              />
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
              <!-- 预览内容区域，使用 marked 渲染 Markdown -->
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

<script setup lang="ts">
import { Document, Edit, Refresh, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
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

// 文档 ID（用于编辑已有文档）
const documentId = ref<number | null>(null)

/**
 * 配置 marked 选项
 */
marked.setOptions({
  breaks: true,
  gfm: true,
})

/**
 * 渲染 Markdown 内容为 HTML
 *
 * @input Markdown 字符串
 * @process 使用 marked 库将 Markdown 转换为 HTML
 * @output 渲染后的 HTML 字符串
 */
const renderedContent = computed(() => {
  if (!content.value.trim()) {
    return '<p style="color:#909399;">在上方编辑器中输入内容，这里将实时展示预览效果...</p>'
  }
  try {
    return marked(content.value) as string
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return content.value
  }
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
      console.log('[编辑器] 文档加载成功:', doc.title)
    } catch (error) {
      console.error('加载文档失败:', error)
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
      await documentApi.updateDocument(documentId.value, {
        title: title.value,
        content: content.value,
      })
      ElMessage.success('文档更新成功')
    } else {
      // 新建文档
      await documentApi.createDocument({
        title: title.value,
        content: content.value,
      })
      ElMessage.success('文档保存成功')
    }
  } catch (error) {
    console.error('保存文档失败:', error)
    ElMessage.error('保存文档失败，请稍后重试')
  }
}

/**
 * 处理清空内容操作
 *
 * @input 用户点击"清空内容"按钮
 * @process 1. 将标题和内容重置为空
 *          2. 使用提示消息告知用户已清空
 * @output 重置页面状态并显示提示
 */
const handleReset = () => {
  title.value = ''
  content.value = ''
  ElMessage.info('已清空标题和内容')
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
}

/* 左侧导航栏样式 */
.aside-container {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.aside-menu {
  border-right: none;
  height: 100%;
}

/* 右侧主内容区域样式 */
.main-container {
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
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
}

.editor-wrapper {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

.preview-wrapper {
  flex: 1;
  margin-top: 0;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  max-height: 500px;
  overflow-y: auto;
}

/* 标题输入框样式 */
.title-input {
  margin-bottom: 12px;
}

/* Markdown 编辑器样式 */
.markdown-editor {
  flex: 1;
}

.markdown-editor :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
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
