<template>
  <div class="friend-container">
    <!-- 使用 Element Plus Container 构建左右布局，左侧为导航，右侧为好友管理区域 -->
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
          <!-- 好友管理菜单项 -->
          <el-menu-item index="/friends">
            <el-icon><User /></el-icon>
            <span>好友管理</span>
          </el-menu-item>
          <!-- 个人信息菜单项 -->
          <el-menu-item index="/profile">
            <el-icon><UserFilled /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主内容区域 -->
      <el-main class="main-container">
        <!-- 标签页切换不同功能 -->
        <el-tabs v-model="activeTab" type="border-card" class="friend-tabs">
          <!-- 好友列表 -->
          <el-tab-pane label="好友列表" name="friends">
            <div class="tab-content">
              <div class="section-header">
                <h3>我的好友</h3>
                <el-button type="primary" @click="showAddFriendDialog = true">
                  添加好友
                </el-button>
              </div>

              <el-empty v-if="friends.length === 0" description="暂无好友" />

              <el-table v-else :data="friends" stripe style="width: 100%">
                <el-table-column prop="friend_username" label="用户名" width="180" />
                <el-table-column prop="friend_email" label="邮箱" />
                <el-table-column label="添加时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      type="danger"
                      size="small"
                      @click="handleRemoveFriend(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- 收到的好友请求 -->
          <el-tab-pane label="好友请求" name="requests">
            <div class="tab-content">
              <div class="section-header">
                <h3>收到的好友请求</h3>
                <el-badge :value="receivedRequests.length" :hidden="receivedRequests.length === 0">
                  <el-button>新请求</el-button>
                </el-badge>
              </div>

              <el-empty v-if="receivedRequests.length === 0" description="暂无好友请求" />

              <el-table v-else :data="receivedRequests" stripe style="width: 100%">
                <el-table-column prop="from_username" label="用户名" width="180" />
                <el-table-column label="请求时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="250" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      size="small"
                      @click="handleAcceptRequest(row)"
                    >
                      接受
                    </el-button>
                    <el-button
                      size="small"
                      @click="handleRejectRequest(row)"
                    >
                      拒绝
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- 发送的好友请求 -->
          <el-tab-pane label="发送请求" name="sent">
            <div class="tab-content">
              <h3>发送的好友请求</h3>

              <el-empty v-if="sentRequests.length === 0" description="暂无发送的请求" />

              <el-table v-else :data="sentRequests" stripe style="width: 100%">
                <el-table-column prop="to_username" label="发送给" width="180" />
                <el-table-column label="请求时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag type="warning">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      size="small"
                      @click="handleCancelRequest(row)"
                    >
                      取消
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>

    <!-- 添加好友对话框 -->
    <el-dialog
      v-model="showAddFriendDialog"
      title="添加好友"
      width="500px"
      @close="resetAddFriendForm"
    >
      <el-form ref="addFriendFormRef" :model="addFriendForm" :rules="addFriendRules" label-width="80px">
        <el-form-item label="搜索用户" prop="username">
          <el-input
            v-model="addFriendForm.username"
            placeholder="输入用户名或邮箱搜索"
            clearable
            @input="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>

        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <p class="search-hint">搜索结果：</p>
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="search-result-item"
          >
            <div class="user-info">
              <span class="username">{{ user.username }}</span>
              <span class="email">{{ user.email }}</span>
            </div>
            <el-button
              type="primary"
              size="small"
              @click="handleSendRequest(user)"
            >
              发送请求
            </el-button>
          </div>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showAddFriendDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Document, Search, User, UserFilled } from '@element-plus/icons-vue'
import { type FormInstance, type FormRules, ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { friendApi } from '../services/api'

/**
 * 好友管理页面组件
 *
 * 提供好友管理功能，包括查看好友列表、处理好友请求、搜索添加好友等
 * 使用 Element Plus 组件库构建的好友管理界面
 *
 * @component
 */

/**
 * 好友信息接口
 */
interface Friend {
  id: number
  friend_id: number
  friend_username: string
  friend_email: string
  created_at: string
}

/**
 * 好友请求信息接口
 */
interface FriendRequest {
  id: number
  from_user_id: number
  from_username: string
  to_user_id: number
  to_username: string
  status: string
  created_at: string
}

/**
 * 搜索用户信息接口
 */
interface SearchUser {
  id: number
  username: string
  email: string
}

/**
 * 路由实例，用于导航跳转
 */
const router = useRouter()

/**
 * 当前路由信息
 */
const route = useRoute()

/**
 * 表单引用对象
 */
const addFriendFormRef = ref<FormInstance>()

/**
 * 当前激活的菜单路径
 */
const activeMenu = ref<string>('/friends')

/**
 * 当前激活的标签页
 */
const activeTab = ref('friends')

/**
 * 是否显示添加好友对话框
 */
const showAddFriendDialog = ref(false)

/**
 * 好友列表
 */
const friends = ref<Friend[]>([])

/**
 * 收到的好友请求列表
 */
const receivedRequests = ref<FriendRequest[]>([])

/**
 * 发送的好友请求列表
 */
const sentRequests = ref<FriendRequest[]>([])

/**
 * 搜索结果
 */
const searchResults = ref<SearchUser[]>([])

/**
 * 搜索防抖定时器
 */
let searchTimer: ReturnType<typeof setTimeout> | null = null

/**
 * 添加好友表单数据
 */
const addFriendForm = reactive({
  username: '',
})

/**
 * 添加好友表单验证规则
 */
const addFriendRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
}

/**
 * 处理菜单选择
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  router.push(index)
}

/**
 * 加载好友列表
 */
const loadFriends = async () => {
  try {
    const res = await friendApi.getFriends()
    friends.value = res.items || []
  } catch (error) {
    console.error('获取好友列表失败:', error)
  }
}

/**
 * 加载收到的好友请求
 */
const loadReceivedRequests = async () => {
  try {
    const res = await friendApi.getReceivedRequests()
    receivedRequests.value = res.items || []
  } catch (error) {
    console.error('获取好友请求失败:', error)
  }
}

/**
 * 加载发送的好友请求
 */
const loadSentRequests = async () => {
  try {
    const res = await friendApi.getSentRequests()
    sentRequests.value = res.items || []
  } catch (error) {
    console.error('获取发送的请求失败:', error)
  }
}

/**
 * 处理搜索
 */
const handleSearch = async () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }

  if (!addFriendForm.username.trim()) {
    searchResults.value = []
    return
  }

  searchTimer = setTimeout(async () => {
    try {
      const res = await friendApi.searchUsers(addFriendForm.username)
      searchResults.value = res || []
    } catch (error) {
      console.error('搜索用户失败:', error)
    }
  }, 300)
}

/**
 * 发送好友请求
 */
const handleSendRequest = async (user: SearchUser) => {
  try {
    await friendApi.sendFriendRequest(user.username)
    ElMessage.success('好友请求已发送')
    loadSentRequests()
    // 从搜索结果中移除已发送请求的用户
    searchResults.value = searchResults.value.filter(u => u.id !== user.id)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '发送好友请求失败')
  }
}

/**
 * 接受好友请求
 */
const handleAcceptRequest = async (request: FriendRequest) => {
  try {
    await friendApi.acceptFriendRequest(request.id)
    ElMessage.success('已接受好友请求')
    loadReceivedRequests()
    loadFriends()
  } catch (error) {
    ElMessage.error('接受好友请求失败')
  }
}

/**
 * 拒绝好友请求
 */
const handleRejectRequest = async (request: FriendRequest) => {
  try {
    await friendApi.rejectFriendRequest(request.id)
    ElMessage.success('已拒绝好友请求')
    loadReceivedRequests()
  } catch (error) {
    ElMessage.error('拒绝好友请求失败')
  }
}

/**
 * 取消好友请求
 */
const handleCancelRequest = async (request: FriendRequest) => {
  try {
    await friendApi.cancelFriendRequest(request.id)
    ElMessage.success('已取消好友请求')
    loadSentRequests()
  } catch (error) {
    ElMessage.error('取消好友请求失败')
  }
}

/**
 * 删除好友
 */
const handleRemoveFriend = async (friend: Friend) => {
  try {
    await ElMessageBox.confirm('确定要删除该好友吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await friendApi.removeFriend(friend.friend_id)
    ElMessage.success('已删除好友')
    loadFriends()
  } catch {
    // 用户取消操作
  }
}

/**
 * 重置添加好友表单
 */
const resetAddFriendForm = () => {
  addFriendForm.username = ''
  searchResults.value = []
}

/**
 * 格式化日期
 */
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  activeMenu.value = route.path || '/friends'
  loadFriends()
  loadReceivedRequests()
  loadSentRequests()
})
</script>

<style scoped>
/* 页面根容器 */
.friend-container {
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

/* 标签页样式 */
.friend-tabs {
  height: calc(100% - 40px);
}

.friend-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow-y: auto;
}

.tab-content {
  padding: 10px;
}

/* 区块标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

/* 搜索结果区域 */
.search-results {
  margin-top: 20px;
}

.search-hint {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #fafafa;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: #303133;
}

.email {
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-container {
    padding: 10px;
  }
}
</style>
