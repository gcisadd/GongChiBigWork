<template>
  <div class="collab-editor-page-container">
    <!-- 使用 Element Plus Container 构建左右布局 -->
    <el-container class="layout-container">
      <!-- 左侧导航栏区域 -->
      <el-aside width="200px" class="aside-container">
        <el-menu
          :default-active="activeMenu"
          class="aside-menu"
          router
          @select="handleMenuSelect"
        >
          <el-menu-item index="/table">
            <el-icon><Document /></el-icon>
            <span>文档列表</span>
          </el-menu-item>
          <el-menu-item index="/collab-editor">
            <el-icon><Connection /></el-icon>
            <span>协作编辑</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>关于</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主内容区域 -->
      <el-main class="main-container">
        <el-card class="collab-editor-card" shadow="always">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <h2>协作编辑</h2>
                <el-tag v-if="documentId" type="success" size="small">
                  文档ID: {{ documentId }}
                </el-tag>
              </div>
              <div class="header-actions">
                <!-- 在线用户列表 -->
                <div class="online-users">
                  <el-tooltip
                    v-for="user in displayUsers"
                    :key="user"
                    :content="user"
                    placement="top"
                  >
                    <el-avatar :size="32" :style="{ backgroundColor: getUserColor(user) }">
                      {{ user.charAt(0).toUpperCase() }}
                    </el-avatar>
                  </el-tooltip>
                  <el-tag v-if="onlineUsers.length > 0" type="info" size="small" class="user-count">
                    {{ onlineUsers.length }} 人在线
                  </el-tag>
                </div>

                <el-button
                  type="primary"
                  :icon="Document"
                  :loading="saving"
                  @click="() => { console.log('[按钮] 点击了保存按钮'); handleSave() }"
                >
                  保存内容
                </el-button>

                <el-button
                  type="warning"
                  :icon="MagicStick"
                  @click="handleAISummary"
                  :loading="aiSummarizing"
                  :disabled="!content || !content.trim()"
                >
                  AI 概括
                </el-button>

                <el-button
                  type="success"
                  :icon="Download"
                  :loading="exportingPdf"
                  @click="handleExportPdf"
                >
                  导出PDF
                </el-button>

              </div>
            </div>
          </template>

          <!-- 协作状态显示 -->
          <div class="collaboration-status">
            <el-tag v-if="isConnected" type="success" size="small" class="status-tag">
              <el-icon><CircleCheck /></el-icon> 已连接
            </el-tag>
            <el-tag v-else type="danger" size="small" class="status-tag">
              <el-icon><CircleClose /></el-icon> 未连接
            </el-tag>

            <!-- 连接错误信息 -->
            <el-tag
              v-if="connectionError"
              type="warning"
              size="small"
              class="error-tag"
            >
              {{ connectionError }}
            </el-tag>
          </div>

          <!-- 协作提示 -->
          <el-alert
            v-if="!isConnected && !connectionError"
            title="未连接到协作服务器"
            type="warning"
            description="请确保后端服务已启动，才能进行多人协作编辑"
            show-icon
            class="collaboration-alert"
          />

          <!-- 编辑器区域 -->
          <div class="editor-content">
            <div class="editor-wrapper">
              <!-- 文档标题输入框 -->
              <el-input
                v-model="title"
                placeholder="请输入文档标题"
                size="large"
                class="title-input"
                clearable
              />

              <!-- 富文本编辑器 -->
              <div class="editor-container" style="position: relative;" ref="editorContainerRef">
                <QuillEditor
                  ref="editorRef"
                  v-model:content="content"
                  content-type="html"
                  theme="snow"
                  class="rich-text-editor"
                  :toolbar="toolbarOptions"
                  @text-change="onTextChange"
                  @selection-change="onSelectionChange"
                  @editor-ready="onEditorReady"
                />
                <!-- 其他用户光标显示 -->
                <div
                  v-for="(cursor, username) in displayedCursors"
                  :key="username"
                  class="remote-cursor"
                  :style="getCursorStyle(cursor, username)"
                >
                  <span class="cursor-label" :style="{ backgroundColor: cursor.color || getUserColor(username) }">
                    {{ username }}
                  </span>
                </div>
              </div>

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
              <h3 class="preview-document-title">
                {{ title || '（未命名文档）' }}
              </h3>
              <div
                class="preview-content"
                v-html="content || emptyContentPlaceholder"
              />
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { CircleCheck, CircleClose, Connection, Document, Download, MagicStick, User } from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentApi } from '../services/api'
import collaborationService from '../services/collaboration'

/**
 * 协作编辑页面组件
 *
 * 提供多人实时协作编辑功能
 * 使用 WebSocket 实现实时同步
 *
 * @component
 */

interface CollaboratorInfo {
  username: string
  cursor?: {
    index: number
    length: number
  }
  color?: string
}

// 路由实例
const route = useRoute()
const router = useRouter()

// 当前激活的菜单路径
const activeMenu = ref('/collab-editor')

// 编辑器引用
const editorRef = ref()

// 编辑器容器引用（用于直接访问 Quill 实例）
const editorContainerRef = ref()

// Quill 实例引用（通过 onEditorReady 回调获取）
let quillInstance: any = null

/**
 * Quill 编辑器就绪回调
 * 注意：@vueup/vue-quill 的 @editor-ready 事件会传递 Quill 实例
 */
const onEditorReady = (quill: any) => {
  if (quill && typeof quill.getSelection === 'function') {
    quillInstance = quill

    // Quill 初始化完成，可以正常处理 text-change 事件
    // 但仍需等待内容加载完成才允许发送
  }
}

// 在 onMounted 中使用 setTimeout 确保 Quill 已初始化
onMounted(() => {
  // 延迟检查 Quill 实例
  const checkQuill = () => {
    if (quillInstance) return

    // 方式1: 通过 VueQuill 组件的 quill 属性
    if (editorRef.value && (editorRef.value as any).quill) {
      const quill = (editorRef.value as any).quill
      if (typeof quill.getSelection === 'function') {
        quillInstance = quill
        return
      }
    }

    // 方式2: 通过 DOM 查询 .ql-container
    const container = document.querySelector('.ql-container')
    if (container) {
      const quill = (container as any).__quill
      if (quill && typeof quill.getSelection === 'function') {
        quillInstance = quill
        return
      }
    }

    // 方式3: 通过 DOM 查询 .ql-editor
    const editorEl = document.querySelector('.ql-editor')
    if (editorEl) {
      const quill = (editorEl as any).__quill
      if (quill && typeof quill.getSelection === 'function') {
        quillInstance = quill
        return
      }
    }

    // 如果还没获取到，100ms 后继续检查
    if (!quillInstance) {
      setTimeout(checkQuill, 100)
    }
  }

  // 开始检查
  checkQuill()
})

// 文档ID
const documentId = ref<number>(0)

// 文档标题
const title = ref<string>('')

// 文档内容
const content = ref<string>('')

// 保存按钮加载状态
const saving = ref(false)

// 导出 PDF 加载状态
const exportingPdf = ref(false)

// AI 概括内容
const summary = ref<string>('')

// AI 概括加载状态
const aiSummarizing = ref<boolean>(false)

// 空内容占位符
const emptyContentPlaceholder =
  '<p style="color:#909399;">在上方编辑器中输入内容，这里将实时展示预览效果...</p>'

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

// 是否正在处理远程更新（避免循环）
const isProcessingRemote = ref(false)

// 自动保存定时器
let autoSaveTimer: ReturnType<typeof setInterval> | null = null

// 是否正在自动保存
const isAutoSaving = ref(false)

// 上次保存时间
const lastSaveTime = ref<Date | null>(null)

// 在线用户列表
const onlineUsers = computed(() => collaborationService.onlineUsers.value)

// 其他用户光标位置（排除自己）
const displayedCursors = computed(() => {
  const cursors = collaborationService.cursors.value
  const result: Record<string, CollaboratorInfo> = {}
  cursors.forEach((cursor, username) => {
    if (username !== currentUsername.value) {
      result[username] = cursor
    }
  })
  return result
})

// 连接错误信息
const connectionError = computed(() => collaborationService.connectionError.value)

// 连接状态
const isConnected = computed(() => collaborationService.isConnected.value)

// 显示的用户列表（排除自己）
const displayUsers = computed(() =>
  onlineUsers.value.filter((u) => u !== currentUsername.value)
)

// 当前用户名
const currentUsername = ref('')

// Quill编辑器初始化状态（防止初始化时重复发送内容）
const isQuillInitializing = ref(true)

/**
 * 获取用户颜色
 */
const getUserColor = (username: string): string => {
  const colors = [
    '#FF6B6B',
    '#4ECDC4',
    '#45B7D1',
    '#96CEB4',
    '#FFEAA7',
    '#DDA0DD',
    '#98D8C8',
    '#F7DC6F',
    '#BB8FCE',
    '#85C1E9',
  ]

  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }

  return colors[Math.abs(hash) % colors.length] ?? '#85C1E9'
}

/**
 * 获取光标样式
 */
const getCursorStyle = (cursor: CollaboratorInfo, username: string) => {
  if (!cursor.cursor) {
    return {}
  }

  const quill = getQuillInstance()
  if (!quill || typeof quill.getBounds !== 'function') {
    return {}
  }

  try {
    // 获取光标位置的坐标（相对于 .ql-editor）
    const bounds = quill.getBounds(cursor.cursor.index)
    const color = cursor.color || getUserColor(username)

    // 查找 .ql-editor 元素作为参照
    const editorEl = document.querySelector('.ql-editor') as HTMLElement | null
    if (!editorEl) {
      return { left: `${bounds.left}px`, top: `${bounds.top}px`, '--cursor-color': color }
    }

    // 计算相对于 .editor-container 的坐标
    const containerEl = editorContainerRef.value as HTMLElement | null
    if (containerEl) {
      const containerRect = containerEl.getBoundingClientRect()
      const editorRect = editorEl.getBoundingClientRect()

      const relativeLeft = bounds.left + editorRect.left - containerRect.left
      const relativeTop = bounds.top + editorRect.top - containerRect.top

      return {
        left: `${relativeLeft}px`,
        top: `${relativeTop}px`,
        '--cursor-color': color,
      }
    }

    return {
      left: `${bounds.left}px`,
      top: `${bounds.top}px`,
      '--cursor-color': color,
    }
  } catch (error) {
    return {}
  }
}

/**
 * 自动保存文档
 */
const autoSave = async () => {
  if (!title.value.trim() || !documentId.value) {
    return
  }

  isAutoSaving.value = true

  try {
    await documentApi.updateDocument(documentId.value, {
      title: title.value,
      content: content.value,
    })
    lastSaveTime.value = new Date()
  } catch (error) {
  } finally {
    isAutoSaving.value = false
  }
}

/**
 * 启动自动保存定时器
 */
const startAutoSave = () => {
  // 每 5 秒自动保存
  autoSaveTimer = setInterval(() => {
    if (documentId.value && isConnected.value) {
      autoSave()
    }
  }, 1000)
}

/**
 * 处理文本变更
 */
const onTextChange = (delta: Record<string, unknown>) => {
  // 如果正在处理远程更新，忽略
  if (isProcessingRemote.value) return

  // 如果 Quill 正在初始化，忽略（这可能是 v-model 绑定导致的虚假事件）
  if (isQuillInitializing.value) {
    return
  }

  // 检查 delta 是否有效（忽略空的 delta）
  if (!delta || Object.keys(delta).length === 0) {
    return
  }

  // 检查 delta 是否只包含 retain（这是选区变化，不需要同步）
  if (delta.ops && Array.isArray(delta.ops) && delta.ops.every((op: any) => op.retain !== undefined)) {
    return
  }

  // 发送内容变更到协作服务器
  collaborationService.sendContentChange(delta, 'user')
}

/**
 * 获取 Quill 实例的辅助函数
 */
const getQuillInstance = () => {
  // 优先使用已存储的实例
  if (quillInstance) return quillInstance

  // 方式1: 通过 VueQuill 组件的 quill 属性
  if (editorRef.value && (editorRef.value as any).quill) {
    const quill = (editorRef.value as any).quill
    if (typeof quill.getSelection === 'function') {
      return quill
    }
  }

  // 方式2: 通过 DOM 查询 .ql-container
  const container = document.querySelector('.ql-container')
  if (container) {
    const quill = (container as any).__quill
    if (quill) return quill
  }

  // 方式3: 通过 DOM 查询 .ql-editor
  const editorEl = document.querySelector('.ql-editor')
  if (editorEl) {
    const quill = (editorEl as any).__quill
    if (quill) return quill
  }

  return null
}

/**
 * 处理选中文本变更
 */
const onSelectionChange = () => {
  const quill = getQuillInstance()
  if (quill) {
    const selection = quill.getSelection()
    if (selection) {
      collaborationService.sendCursorPosition(selection.index, selection.length)
    }
  }
}

/**
 * 处理菜单选择
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  router.push(index)
}

/**
 * 保存文档
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

  saving.value = true

  try {
    if (documentId.value) {
      // 更新现有文档
      console.log('[保存] 更新文档, id:', documentId.value)
      await documentApi.updateDocument(documentId.value, {
        title: title.value,
        content: content.value,
      })
      console.log('[保存] 文档更新成功')
    } else {
      // 创建新文档
      console.log('[保存] 创建新文档')
      const result = await documentApi.createDocument({
        title: title.value,
        content: content.value,
      })
      documentId.value = result.id
      console.log('[保存] 文档创建成功, id:', result.id)
    }

    ElMessage.success('文档保存成功')
  } catch (error) {
    console.error('[保存] 保存文档失败:', error)
    ElMessage.error('保存文档失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

/**
 * 导出 PDF
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
    contentElement.innerHTML = content.value || ''
    contentElement.style.color = '#303133'
    contentElement.style.lineHeight = '1.6'

    // 添加富文本编辑器样式
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
 * 处理 AI 概括操作
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
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

/**
 * 清空内容
 */
const handleReset = () => {
  title.value = ''
  content.value = ''

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
 * 初始化协作连接
 */
const initCollaboration = async () => {
  // 获取当前用户名
  currentUsername.value = localStorage.getItem('username') || '匿名用户'

  // 如果有文档ID，连接协作房间
  if (documentId.value) {
    const connected = await collaborationService.connect(documentId.value, currentUsername.value)

    if (connected) {
      ElMessage.success('已连接到协作房间')
      // 连接成功后启动自动保存定时器
      startAutoSave()
    } else {
      ElMessage.warning('连接协作房间失败')
    }
  }
}

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

      // 文档加载完成后，Quill 初始化完成，允许发送变更
      // 延迟一下确保 Quill 已处理完 v-model 绑定
      setTimeout(() => {
        isQuillInitializing.value = false
      }, 100)
    } catch (error) {
      // 即使加载失败，也要重置初始化状态
      isQuillInitializing.value = false
    }
  } else {
    isQuillInitializing.value = false
  }
}

/**
 * 设置协作回调
 */
const setupCollaborationCallbacks = () => {
  // 内容变更回调
  collaborationService.onContentChangeCallback((delta, source) => {

    const quill = getQuillInstance()
    // 如果 Quill 正在初始化，则忽略
    if (isQuillInitializing.value) {
      return
    }

    // 即使正在处理远程变更，也要处理新的 delta
    // 开始处理远程变更
    isProcessingRemote.value = true

    // 应用 delta 到 Quill
    quill.updateContents(delta as any)


    // 延迟重置标志，确保 Quill 完全处理完 delta
    setTimeout(() => {
      isProcessingRemote.value = false
    }, 0)
  })

  // 光标位置回调
  collaborationService.onCursorPositionCallback((username, cursor) => {
  })

  // 用户加入回调
  collaborationService.onUserJoinedCallback((username, users) => {
    ElMessage.info(`${username} 加入了编辑`)
  })

  // 内容同步回调 - 当新用户加入时，后端发送当前文档内容
  collaborationService.onSyncContentCallback((syncContent) => {

    const quill = getQuillInstance()
    if (!quill) {
      return
    }

    // 使用 setContents 设置内容，这会替换整个编辑器内容
    // 同时设置 isQuillInitializing 防止触发本地 text-change 事件
    isQuillInitializing.value = true

    // 直接设置 HTML 内容
    if (syncContent) {
      quill.root.innerHTML = syncContent
    }

    // 同时更新 v-model
    content.value = syncContent || ''

    // 延迟重置初始化状态
    setTimeout(() => {
      isQuillInitializing.value = false
    }, 500)
  })

  // 用户离开回调
  collaborationService.onUserLeftCallback((username, users) => {
    ElMessage.info(`${username} 离开了编辑`)
  })

}

/**
 * 组件挂载
 */
onMounted(async () => {
  activeMenu.value = route.path || '/collab-editor'

  // 加载文档
  await loadDocument()

  // 设置协作回调
  setupCollaborationCallbacks()

  // 初始化协作连接
  await initCollaboration()

  // 启动自动保存定时器（连接成功后启动）
  if (isConnected.value) {
    startAutoSave()
  }
})

/**
 * 组件卸载
 */
onUnmounted(() => {
  // 清除自动保存定时器
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }

  // 断开协作连接
  collaborationService.disconnect()
})
</script>

<style scoped>
/* 页面容器 */
.collab-editor-page-container {
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

/* 布局容器 */
.layout-container {
  width: 100%;
  height: 100%;
}

/* 左侧导航栏 */
.aside-container {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.aside-menu {
  border-right: none;
  height: 100%;
}

/* 右侧主内容区域 */
.main-container {
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
  box-sizing: border-box;
}

/* 编辑器卡片 */
.collab-editor-card {
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
  flex-wrap: wrap;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 在线用户列表 */
.online-users {
  display: flex;
  align-items: center;
  gap: 4px;
}

.online-users .el-avatar {
  margin-left: -8px;
  border: 2px solid #fff;
}

.online-users .el-avatar:first-child {
  margin-left: 0;
}

.user-count {
  margin-left: 8px;
}

/* 协作提示 */
.collaboration-alert {
  margin-bottom: 16px;
}

/* 协作状态显示 */
.collaboration-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-tag {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 编辑器内容区域：左右布局 */
.editor-content {
  display: flex;
  flex-direction: row;
  gap: 20px;
  flex: 1;
}

.editor-wrapper {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* 标题输入框 */
.title-input {
  margin-bottom: 12px;
}

/* 富文本编辑器 */
.rich-text-editor {
  height: 350px;
  position: relative;
}

.rich-text-editor :deep(.ql-container) {
  height: calc(100% - 42px);
  position: relative;
}

/* 远程光标样式 - 相对于 Quill 编辑器容器定位 */
.remote-cursor {
  position: absolute;
  left: 0;
  top: 0;
  pointer-events: none;
  z-index: 100;
}

.remote-cursor::before {
  content: '';
  position: absolute;
  width: 2px;
  height: 20px;
  background-color: var(--cursor-color, #000);
  animation: cursor-blink 1s infinite;
}

.cursor-label {
  position: absolute;
  top: -20px;
  left: 0;
  padding: 2px 6px;
  font-size: 10px;
  color: #fff;
  border-radius: 3px;
  white-space: nowrap;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 预览区域 */
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
}

.preview-content img {
  max-width: 100%;
  height: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-container {
    padding: 10px;
  }

  .collab-editor-card {
    min-height: auto;
  }

  .rich-text-editor {
    height: 280px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .online-users {
    display: none;
  }
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
  overflow-y: auto;
}
</style>
