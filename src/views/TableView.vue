<template>
  <div class="table-container">
    <!-- 使用 Element Plus Container 布局组件 -->
    <el-container class="layout-container">
      <!-- 左侧导航栏区域 -->
      <el-aside width="200px" class="aside-container">
        <el-menu
          :default-active="activeMenu"
          class="aside-menu"
          router
          @select="handleMenuSelect"
        >
          <!-- 导航菜单项 -->
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
    <!-- 表格页面标题 -->
    <el-card class="table-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>文档列表</h2>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新建文档</el-button>
        </div>
      </template>

      <!-- 表格操作栏 -->
      <div class="table-toolbar">
        <el-button type="danger" :icon="Delete" :disabled="selectedRows.length === 0" @click="handleDelete">
          批量删除
        </el-button>
        <el-button type="success" :icon="Refresh" @click="handleRefresh">刷新</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        class="document-table"
        style="width: 100%"
        border
        stripe
        size="large"
        @selection-change="handleSelectionChange"
      >
        <!-- 选择列：适当减小固定宽度，避免占用过多空间 -->
        <el-table-column type="selection" width="60" />
        <!-- 其余列使用 min-width，由表格自动按剩余空间等比拉伸，铺满整行 -->
        <el-table-column prop="id" label="文档ID" min-width="100" />
        <el-table-column prop="title" label="文档名" min-width="200" />
        <el-table-column prop="creator_name" label="创建者" min-width="150" />
        <el-table-column prop="modified_time" label="修改时间" min-width="200" />
        <el-table-column label="操作" min-width="280" fixed="right">
          <template #default="scope">
            <el-button
              type="success"
              size="large"
              :icon="Connection"
              class="action-button"
              @click="handleCollabEdit(scope.row)"
            >
              协作
            </el-button>
            <el-button
              type="primary"
              size="large"
              :icon="Edit"
              class="action-button"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="large"
              :icon="Delete"
              class="action-button"
              @click="handleDeleteRow(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Connection, Delete, Document, Edit, Plus, Refresh, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentApi } from '../services/api'
/**
 * 文档列表页面组件
 *
 * 提供文档列表展示功能，包含文档列表、分页、新建、编辑、删除等操作
 * 使用 Element Plus Container 组件构建左右布局，左侧为导航栏，右侧为文档列表内容区域
 *
 * @component
 */

/**
 * 文档数据接口
 *
 * @interface DocumentRow
 * @property {number} id - 文档ID
 * @property {string} title - 文档名
 * @property {string} creator - 创建者
 * @property {string} modifiedTime - 修改时间
 */
interface DocumentRow {
  id: number
  title: string
  creator_name: string
  modified_time: string
}

// 路由实例，用于获取当前路由路径和执行页面跳转
const route = useRoute()
const router = useRouter()

// 当前激活的菜单项
const activeMenu = ref('/table')

// 文档列表数据
const tableData = ref<DocumentRow[]>([])

// 选中的行数据
const selectedRows = ref<DocumentRow[]>([])

// 当前页码
const currentPage = ref(1)

// 每页显示数量
const pageSize = ref(10)

// 数据总数
const total = ref(0)

/**
 * 格式化日期时间
 *
 * @input 日期对象
 * @process 1. 将日期对象格式化为 YYYY-MM-DD HH:mm:ss 格式
 * @output 格式化后的日期时间字符串
 */
const formatDateTime = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 加载文档列表数据
 *
 * @input 组件挂载时或用户触发刷新
 * @process 1. 调用后端 API 获取文档列表
 *          2. 设置数据总数
 *          3. 更新表格显示
 * @output 填充文档列表数据
 */
const loadTableData = async () => {
  try {
    // 调用后端 API 获取文档列表
    const response = await documentApi.getDocuments(currentPage.value, pageSize.value)

    // 更新表格数据
    tableData.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('加载文档列表失败:', error)
    ElMessage.error('加载文档列表失败')

    // 如果加载失败，使用空数组
    tableData.value = []
    total.value = 0
  }
}

/**
 * 初始化文档列表数据
 *
 * @input 组件挂载时触发
 * @process 1. 加载文档列表数据
 * @output 填充文档列表数据
 */
const initTableData = () => {
  loadTableData()
}

/**
 * 处理选择变化
 *
 * @input 用户选择表格行
 * @process 1. 获取选中的行数据
 *          2. 更新选中行数组
 * @output 更新 selectedRows 数组
 */
const handleSelectionChange = (selection: DocumentRow[]) => {
  selectedRows.value = selection
}

/**
 * 处理新建文档操作
 *
 * @input 用户点击新建文档按钮
 * @process 1. 直接通过路由跳转到富文本编辑器页面 `/editor`
 *          2. 后续可在跳转时携带文档 ID 或其他参数用于初始化编辑内容
 * @output 跳转到富文本编辑器页面
 */
const handleAdd = () => {
  router.push('/editor')
}

/**
 * 处理编辑文档操作
 *
 * @input 用户点击编辑按钮
 * @process 1. 获取当前文档数据
 *          2. 通过路由跳转到富文本编辑器页面，并在查询参数中携带文档 ID
 *          3. 后续可在编辑器页面根据 ID 加载对应文档内容（目前仅跳转，不做数据加载）
 * @output 跳转到富文本编辑器页面
 */
const handleEdit = (row: DocumentRow) => {
  router.push({
    path: '/editor',
    query: {
      id: String(row.id),
    },
  })
}

/**
 * 处理协作编辑操作
 *
 * @input 用户点击协作编辑按钮
 * @process 跳转到协作编辑页面
 * @output 跳转到协作编辑页面
 */
const handleCollabEdit = (row: DocumentRow) => {
  router.push({
    path: '/collab-editor',
    query: {
      id: String(row.id),
    },
  })
}

/**
 * 处理删除单行操作
 *
 * @input 用户点击删除按钮
 * @process 1. 确认删除操作
 *          2. 调用后端 API 删除文档
 *          3. 重新加载文档列表
 * @output 更新文档列表数据，显示成功消息
 */
const handleDeleteRow = async (row: DocumentRow) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档 "${row.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 调用后端 API 删除文档
    await documentApi.deleteDocument(row.id)

    // 重新加载文档列表
    await loadTableData()

    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除文档失败')
    }
  }
}

/**
 * 处理批量删除操作
 *
 * @input 用户点击批量删除按钮
 * @process 1. 确认删除操作
 *          2. 逐个调用后端 API 删除文档
 *          3. 重新加载文档列表
 * @output 更新文档列表数据，显示成功消息
 */
const handleDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的文档')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个文档吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 逐个删除选中的文档
    for (const row of selectedRows.value) {
      await documentApi.deleteDocument(row.id)
    }

    // 重新加载文档列表
    await loadTableData()

    // 清空选中状态
    selectedRows.value = []
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败，请稍后重试')
    }
  }
}

/**
 * 处理刷新操作
 *
 * @input 用户点击刷新按钮
 * @process 1. 重新加载文档列表数据
 *          2. 重置分页信息
 * @output 刷新文档列表数据
 */
const handleRefresh = () => {
  currentPage.value = 1
  loadTableData()
  ElMessage.success('刷新成功')
}

/**
 * 处理每页显示数量变化
 *
 * @input 用户改变每页显示数量
 * @process 1. 更新每页显示数量
 *          2. 重新加载数据
 * @output 更新表格显示
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadTableData()
}

/**
 * 处理页码变化
 *
 * @input 用户切换页码
 * @process 1. 更新当前页码
 *          2. 重新加载数据
 * @output 更新表格显示
 */
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadTableData()
}

/**
 * 处理菜单选择
 *
 * @input 用户点击导航菜单项
 * @process 1. 更新当前激活的菜单项
 *          2. 菜单路由跳转由 el-menu 的 router 属性自动处理
 * @output 更新激活菜单状态
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}

/**
 * 组件挂载时初始化数据
 *
 * @input 组件挂载完成
 * @process 1. 设置当前激活的菜单项为当前路由路径
 *          2. 调用初始化表格数据函数
 * @output 填充表格数据，设置菜单激活状态
 */
onMounted(() => {
  // 根据当前路由设置激活的菜单项
  activeMenu.value = route.path
  initTableData()
})
</script>

<style scoped>
/* 表格容器样式 - 全屏显示 */
.table-container {
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* 布局容器样式 */
.layout-container {
  width: 100%;
  height: 100%;
}

/* 左侧导航栏容器样式 */
.aside-container {
  background-color: #ffffff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

/* 左侧导航菜单样式 */
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

/* 表格卡片样式 */
.table-card {
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 卡片头部样式 */
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

/* 表格工具栏样式 */
.table-toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

/* 分页容器样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 表格行高度与单元格内边距：让每一行看起来更高、更舒适 */
.document-table :deep(.el-table__cell) {
  padding-top: 16px;
  padding-bottom: 16px;
}

/* 操作列按钮样式：增大按钮之间间距，方便点击 */
.action-button + .action-button {
  margin-left: 8px;
}

</style>
