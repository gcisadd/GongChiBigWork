<template>
  <div class="table-container">
    <!-- 表格页面标题 -->
    <el-card class="table-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>数据表格</h2>
        </div>
      </template>

      <!-- 表格操作栏 -->
      <div class="table-toolbar">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增</el-button>
        <el-button type="danger" :icon="Delete" :disabled="selectedRows.length === 0" @click="handleDelete">
          删除
        </el-button>
        <el-button type="success" :icon="Refresh" @click="handleRefresh">刷新</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" :icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" :icon="Delete" @click="handleDeleteRow(scope.row)">删除</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { Delete, Edit, Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'

/**
 * 表格页面组件
 *
 * 提供数据表格展示功能，包含数据列表、分页、新增、编辑、删除等操作
 * 使用 Element Plus 表格组件构建功能完善的数据管理界面
 *
 * @component
 */

/**
 * 表格数据接口
 *
 * @interface TableRow
 * @property {number} id - 数据ID
 * @property {string} name - 姓名
 * @property {number} age - 年龄
 * @property {string} email - 邮箱
 * @property {string} address - 地址
 */
interface TableRow {
  id: number
  name: string
  age: number
  email: string
  address: string
}

// 表格数据
const tableData = ref<TableRow[]>([])

// 选中的行数据
const selectedRows = ref<TableRow[]>([])

// 当前页码
const currentPage = ref(1)

// 每页显示数量
const pageSize = ref(10)

// 数据总数
const total = ref(0)

/**
 * 初始化表格数据
 *
 * @input 组件挂载时触发
 * @process 1. 生成模拟数据
 *          2. 设置数据总数
 *          3. 更新表格显示
 * @output 填充表格数据
 */
const initTableData = () => {
  // 模拟数据生成
  const mockData: TableRow[] = []
  for (let i = 1; i <= 50; i++) {
    mockData.push({
      id: i,
      name: `用户${i}`,
      age: 20 + Math.floor(Math.random() * 40),
      email: `user${i}@example.com`,
      address: `地址${i}号`,
    })
  }
  tableData.value = mockData
  total.value = mockData.length
}

/**
 * 处理选择变化
 *
 * @input 用户选择表格行
 * @process 1. 获取选中的行数据
 *          2. 更新选中行数组
 * @output 更新 selectedRows 数组
 */
const handleSelectionChange = (selection: TableRow[]) => {
  selectedRows.value = selection
}

/**
 * 处理新增操作
 *
 * @input 用户点击新增按钮
 * @process 1. 显示提示信息
 *          2. 后续可打开新增对话框
 * @output 显示提示消息
 */
const handleAdd = () => {
  ElMessage.info('新增功能待实现')
  // 后续可以打开新增对话框
  // dialogVisible.value = true
}

/**
 * 处理编辑操作
 *
 * @input 用户点击编辑按钮
 * @process 1. 获取当前行数据
 *          2. 显示提示信息
 *          3. 后续可打开编辑对话框
 * @output 显示提示消息
 */
const handleEdit = (row: TableRow) => {
  ElMessage.info(`编辑用户：${row.name}`)
  // 后续可以打开编辑对话框
  // editDialogVisible.value = true
  // editForm.value = { ...row }
}

/**
 * 处理删除单行操作
 *
 * @input 用户点击删除按钮
 * @process 1. 确认删除操作
 *          2. 从表格数据中移除该行
 *          3. 更新数据总数
 * @output 更新表格数据，显示成功消息
 */
const handleDeleteRow = async (row: TableRow) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const index = tableData.value.findIndex((item) => item.id === row.id)
    if (index > -1) {
      tableData.value.splice(index, 1)
      total.value--
      ElMessage.success('删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

/**
 * 处理批量删除操作
 *
 * @input 用户点击批量删除按钮
 * @process 1. 确认删除操作
 *          2. 从表格数据中移除选中的行
 *          3. 更新数据总数
 * @output 更新表格数据，显示成功消息
 */
const handleDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的数据')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条数据吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const ids = selectedRows.value.map((row) => row.id)
    tableData.value = tableData.value.filter((item) => !ids.includes(item.id))
    total.value = tableData.value.length
    selectedRows.value = []
    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
  }
}

/**
 * 处理刷新操作
 *
 * @input 用户点击刷新按钮
 * @process 1. 重新初始化表格数据
 *          2. 重置分页信息
 * @output 刷新表格数据
 */
const handleRefresh = () => {
  initTableData()
  currentPage.value = 1
  ElMessage.success('刷新成功')
}

/**
 * 处理每页显示数量变化
 *
 * @input 用户改变每页显示数量
 * @process 1. 更新每页显示数量
 *          2. 重新加载数据（实际项目中应调用 API）
 * @output 更新表格显示
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  // 实际项目中应调用 API 重新加载数据
  ElMessage.info(`每页显示 ${size} 条`)
}

/**
 * 处理页码变化
 *
 * @input 用户切换页码
 * @process 1. 更新当前页码
 *          2. 重新加载数据（实际项目中应调用 API）
 * @output 更新表格显示
 */
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  // 实际项目中应调用 API 重新加载数据
  ElMessage.info(`当前第 ${page} 页`)
}

/**
 * 组件挂载时初始化数据
 *
 * @input 组件挂载完成
 * @process 调用初始化表格数据函数
 * @output 填充表格数据
 */
onMounted(() => {
  initTableData()
})
</script>

<style scoped>
/* 表格容器样式 - 全屏显示 */
.table-container {
  width: 100vw;
  height: 100%;
  background-color: #f5f5f5;
  box-sizing: border-box;
  margin: 0;
  overflow: auto;
}

/* 表格卡片样式 */
.table-card {
  border-radius: 8px;
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

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .table-container {
    padding: 10px;
  }

  .table-toolbar {
    flex-wrap: wrap;
  }

  .pagination-container {
    justify-content: center;
  }
}
</style>
