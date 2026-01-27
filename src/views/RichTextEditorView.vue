<template>
  <div class="editor-page-container">
    <!-- 使用 Element Plus Container 构建左右布局，左侧为导航，右侧为富文本编辑器区域 -->
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
          <!-- 富文本编辑器菜单项 -->
          <el-menu-item index="/editor">
            <el-icon><Edit /></el-icon>
            <span>富文本编辑器</span>
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

          <!-- 编辑器和预览区使用上下结构：上方为编辑器，下方为预览 -->
          <div class="editor-content">
            <!-- 富文本编辑器区域 -->
            <div class="editor-wrapper">
              <!-- 富文本编辑器标题输入框 -->
              <el-input
                v-model="title"
                placeholder="请输入文档标题"
                size="large"
                class="title-input"
                clearable
              />

              <!-- 富文本编辑器组件 -->
              <!-- 使用 QuillEditor 作为富文本编辑器核心 -->
              <QuillEditor
                v-model:content="content"
                content-type="html"
                theme="snow"
                class="rich-text-editor"
                :toolbar="toolbarOptions"
              />
            </div>

            <!-- 右侧或下方预览区域，这里采用下方预览，方便在较窄屏幕上浏览 -->
            <div class="preview-wrapper">
              <div class="preview-header">
                <span class="preview-title">实时预览</span>
                <el-tag type="info" size="small">只读</el-tag>
              </div>
              <!-- 预览标题 -->
              <h3 class="preview-document-title">
                {{ title || '（未命名文档）' }}
              </h3>
              <!-- 预览内容区域，使用 v-html 渲染编辑器生成的 HTML -->
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
import { Document, Edit, Refresh, User } from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

/**
 * 富文本编辑器页面组件
 *
 * 提供一个可视化的富文本编辑界面，支持标题输入、富文本内容编辑、实时 HTML 预览，
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
 * 富文本内容
 *
 * @input 用户在 Quill 富文本编辑器中输入或编辑的内容
 * @process 使用 v-model:content 与 QuillEditor 双向绑定，类型为 HTML 字符串
 * @output 1. 在预览区域中以 HTML 形式展示
 *         2. 可在保存时提交给后端 API
 */
const content = ref<string>('')

/**
 * 预览区为空时的占位 HTML 内容
 *
 * @input 当 content 为空字符串时使用
 * @process 使用 v-html 渲染一段简单提示文本
 * @output 提示用户当前还没有输入内容
 */
const emptyContentPlaceholder =
  '<p style="color:#909399;">在上方编辑器中输入内容，这里将实时展示预览效果...</p>'

/**
 * 富文本编辑器工具栏配置
 *
 * @input QuillEditor 的 toolbar 属性
 * @process 配置常见的文本样式、标题、列表、对齐方式、链接和图片等工具
 * @output 控制编辑器顶部工具栏显示的按钮集合
 */
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
 * @input 用户点击“保存内容”按钮
 * @process 1. 校验标题和内容是否为空
 *          2. 如果为空给出友好提示
 *          3. 如果不为空，模拟保存成功（实际项目中可调用后端 API）
 * @output 显示保存成功或提示消息
 */
const handleSave = () => {
  if (!title.value.trim() && !content.value.trim()) {
    ElMessage.warning('请输入标题或内容后再保存')
    return
  }

  // 这里为模拟保存逻辑，实际项目中可以调用后端接口
  // 示例：await saveDocument({ title: title.value, content: content.value })
  ElMessage.success('内容已模拟保存（后续可接入真实接口）')
}

/**
 * 处理清空内容操作
 *
 * @input 用户点击“清空内容”按钮
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
 * @process 将 activeMenu 设置为当前路由路径，确保刷新页面后菜单高亮正确
 * @output 左侧导航栏显示正确的激活项
 */
onMounted(() => {
  activeMenu.value = route.path || '/editor'
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

/* 编辑器和预览整体容器：上下布局（在桌面端看起来为上下结构，在移动端也更自然） */
.editor-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 标题输入框样式 */
.title-input {
  margin-bottom: 12px;
}

/* 富文本编辑器容器 */
.editor-wrapper {
  background-color: #ffffff;
}

/* Quill 编辑器本身的高度和边框 */
.rich-text-editor {
  height: 320px;
}

.rich-text-editor :deep(.ql-container) {
  height: calc(100% - 42px);
}

/* 预览区域样式 */
.preview-wrapper {
  margin-top: 10px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
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

  .rich-text-editor {
    height: 260px;
  }
}
</style>

