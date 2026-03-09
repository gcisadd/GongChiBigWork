<template>
  <div class="profile-container">
    <!-- 使用 Element Plus Container 构建左右布局，左侧为导航，右侧为个人信息区域 -->
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
          <!-- 个人信息菜单项 -->
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>关于</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧主内容区域 -->
      <el-main class="main-container">
        <el-card class="profile-card" shadow="always">
          <template #header>
            <div class="card-header">
              <h2>个人信息</h2>
            </div>
          </template>

          <!-- 个人信息表单 -->
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            class="profile-form"
          >
            <!-- 用户名输入框 -->
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="profileForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                clearable
                size="large"
              />
            </el-form-item>

            <!-- 邮箱输入框 -->
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="profileForm.email"
                placeholder="请输入邮箱地址"
                :prefix-icon="Message"
                clearable
                size="large"
              />
            </el-form-item>

            <!-- 手机号输入框 -->
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="profileForm.phone"
                placeholder="请输入手机号"
                :prefix-icon="Phone"
                clearable
                size="large"
              />
            </el-form-item>

            <!-- 个人简介输入框 -->
            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="请输入个人简介"
                maxlength="200"
                show-word-limit
                size="large"
              />
            </el-form-item>

            <!-- 操作按钮区域 -->
            <el-form-item>
              <el-button type="primary" size="large" :loading="saving" @click="handleSave">
                保存修改
              </el-button>
              <el-button size="large" @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 退出登录按钮 -->
          <div class="logout-section">
            <el-divider />
            <el-button type="danger" size="large" :icon="SwitchButton" @click="handleLogout">
              退出登录
            </el-button>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Document, Message, Phone, SwitchButton, User } from '@element-plus/icons-vue'
import { type FormInstance, type FormRules, ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi, profileApi } from '../services/api'

/**
 * 个人信息页面组件
 *
 * 提供个人信息显示和编辑功能，包含用户名、邮箱、手机号、个人简介等字段的编辑，
 * 以及退出登录功能。使用 Element Plus 组件库构建美观的个人信息管理界面。
 *
 * @component
 */

/**
 * 个人信息表单数据接口
 *
 * @interface ProfileForm
 * @property {string} username - 用户名
 * @property {string} email - 邮箱地址
 * @property {string} phone - 手机号
 * @property {string} bio - 个人简介
 */
interface ProfileForm {
  username: string
  email: string
  phone: string
  bio: string
}

/**
 * 用户信息接口（后端返回的数据结构）
 *
 * @interface UserInfo
 * @property {number} id - 用户ID
 * @property {string} username - 用户名
 * @property {string} email - 邮箱
 * @property {string} [phone] - 手机号
 * @property {string} [bio] - 个人简介
 */
interface UserInfo {
  id: number
  username: string
  email: string
  phone?: string
  bio?: string
}

/**
 * 路由实例，用于导航跳转
 */
const router = useRouter()

/**
 * 当前路由信息，用于确定左侧菜单高亮项
 */
const route = useRoute()

/**
 * 表单引用对象，用于表单验证和重置
 */
const profileFormRef = ref<FormInstance>()

/**
 * 保存按钮加载状态
 */
const saving = ref(false)

/**
 * 当前激活的菜单路径
 *
 * @input 由当前路由变化触发
 * @process 当页面加载或路由变化时更新为当前路径
 * @output 控制左侧导航菜单的高亮状态
 */
const activeMenu = ref<string>('/profile')

/**
 * 个人信息表单数据
 *
 * @input 用户在表单中输入的数据
 * @process 双向绑定到表单组件
 * @output 提交给后端保存或显示在表单中
 */
const profileForm = reactive<ProfileForm>({
  username: '',
  email: '',
  phone: '',
  bio: '',
})

/**
 * 表单验证规则
 *
 * @input 表单字段值
 * @process 1. 检查用户名是否为空
 *          2. 检查邮箱格式是否正确
 *          3. 检查手机号格式是否正确
 * @output 返回验证错误信息或通过验证
 */
const profileRules: FormRules<ProfileForm> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' },
  ],
  bio: [
    { max: 200, message: '个人简介不能超过 200 个字符', trigger: 'blur' },
  ],
}

/**
 * 初始化个人信息数据
 *
 * @input 组件挂载时触发
 * @process 1. 从 localStorage 获取用户名
 *          2. 调用后端 API 获取用户信息
 *          3. 填充到表单中
 * @output 填充个人信息表单数据
 */
const initProfileData = async () => {
  try {
    // 调用后端 API 获取用户信息
    const userInfo: UserInfo = await authApi.getCurrentUser()

    // 填充表单数据
    profileForm.username = userInfo.username || ''
    profileForm.email = userInfo.email || ''
    profileForm.phone = userInfo.phone || ''
    profileForm.bio = userInfo.bio || ''
  } catch (error) {
    console.error('获取用户信息失败:', error)
    // 如果获取失败，使用本地存储的用户名
    const savedUsername = localStorage.getItem('username') || ''
    profileForm.username = savedUsername || '示例用户'
    profileForm.email = 'example@example.com'
    profileForm.phone = '13800138000'
    profileForm.bio = '这是一个示例的个人简介，您可以在这里编辑您自己的简介内容。'
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
 * 处理保存个人信息操作
 *
 * @input 用户点击"保存修改"按钮
 * @process 1. 验证表单字段是否符合规则
 *          2. 如果验证通过，设置加载状态为 true
 *          3. 调用后端 API 更新用户信息
 *          4. 显示保存成功消息
 * @output 显示保存成功或错误消息
 */
const handleSave = async () => {
  if (!profileFormRef.value) return

  // 验证表单
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true

      try {
        // 调用后端 API 更新用户信息
        await profileApi.updateProfile({
          phone: profileForm.phone,
          bio: profileForm.bio,
        })

        ElMessage.success('个人信息保存成功')
      } catch (error) {
        console.error('保存个人信息失败:', error)
        ElMessage.error('保存个人信息失败，请稍后重试')
      } finally {
        saving.value = false
      }
    }
  })
}

/**
 * 处理重置表单操作
 *
 * @input 用户点击"重置"按钮
 * @process 1. 重置表单到初始状态
 *          2. 重新加载用户信息
 * @output 表单恢复到初始状态
 */
const handleReset = () => {
  if (!profileFormRef.value) return
  profileFormRef.value.resetFields()
  initProfileData()
  ElMessage.info('表单已重置')
}

/**
 * 处理退出登录操作
 *
 * @input 用户点击"退出登录"按钮
 * @process 1. 确认退出操作
 *          2. 清除本地存储的用户信息
 *          3. 跳转到登录页面
 * @output 跳转到登录页面
 */
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 清除本地存储的用户信息
    localStorage.removeItem('token')
    localStorage.removeItem('username')

    ElMessage.success('已退出登录')
    // 跳转到登录页面
    router.push('/about')
  } catch {
    // 用户取消退出
  }
}

/**
 * 组件挂载时初始化数据
 *
 * @input 组件首次挂载
 * @process 1. 设置当前激活的菜单项为当前路由路径
 *          2. 调用初始化个人信息数据函数
 * @output 填充个人信息表单数据，设置菜单激活状态
 */
onMounted(() => {
  // 根据当前路由设置激活的菜单项
  activeMenu.value = route.path || '/profile'
  initProfileData()
})
</script>

<style scoped>
/* 页面根容器：全屏布局，背景与其他页面保持一致 */
.profile-container {
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

/* 个人信息卡片样式 */
.profile-card {
  border-radius: 8px;
  max-width: 800px;
  margin: 0 auto;
}

/* 卡片头部样式 */
.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

/* 个人信息表单样式 */
.profile-form {
  margin-top: 20px;
}

/* 退出登录区域样式 */
.logout-section {
  margin-top: 30px;
  text-align: center;
}

.logout-section .el-button {
  width: 200px;
}

/* 响应式设计：在窄屏幕上调整内边距 */
@media (max-width: 768px) {
  .main-container {
    padding: 10px;
  }

  .profile-card {
    max-width: 100%;
  }
}
</style>
