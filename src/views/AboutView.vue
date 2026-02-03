<template>
  <div class="login-container">
    <!-- 登录卡片容器 -->
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>用户登录</h2>
        </div>
      </template>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        class="login-form"
      >
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <!-- 记住我选项 -->
        <el-form-item>
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Lock, User } from '@element-plus/icons-vue'
import { type FormInstance, type FormRules, ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

/**
 * 登录页面组件
 *
 * 提供用户登录功能，包含用户名和密码输入、表单验证、登录提交等功能
 * 使用 Element Plus 组件库构建美观的登录界面
 * 登录成功后跳转到表格页面
 *
 * @component
 */

/**
 * 登录表单数据接口
 *
 * @interface LoginForm
 * @property {string} username - 用户名
 * @property {string} password - 密码
 * @property {boolean} remember - 是否记住登录状态
 */
interface LoginForm {
  username: string
  password: string
  remember: boolean
}

// 路由实例，用于页面跳转
const router = useRouter()

// 表单引用对象，用于表单验证和重置
const loginFormRef = ref<FormInstance>()

// 登录按钮加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive<LoginForm>({
  username: '',
  password: '',
  remember: false,
})

/**
 * 表单验证规则
 *
 * @input 表单字段值
 * @process 1. 检查用户名是否为空
 *          2. 检查密码是否为空
 *          3. 检查密码长度是否符合要求
 * @output 返回验证错误信息或通过验证
 */
const loginRules: FormRules<LoginForm> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

/**
 * 处理登录提交
 *
 * @input 用户点击登录按钮或按回车键
 * @process 1. 验证表单字段是否符合规则
 *          2. 如果验证通过，调用后端登录 API
 *          3. 登录成功后跳转到表格页面
 * @output 跳转到表格页面或显示错误消息
 */
const handleLogin = async () => {
  if (!loginFormRef.value) return

  // 验证表单
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        // 调用后端登录 API
        await authApi.login(loginForm.username, loginForm.password, loginForm.remember)
        ElMessage.success('登录成功')
        // 跳转到表格页面
        router.push('/table')
      } catch (error: any) {
        // 显示错误消息
        const errorMessage = error.response?.data?.detail || '登录失败，请检查用户名和密码'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 登录容器样式 - 全屏居中显示登录卡片 */
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
  margin: 0;
}

/* 登录卡片样式 */
.login-card {
  width: 100%;
  max-width: 450px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

/* 卡片头部样式 */
.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

/* 登录表单样式 */
.login-form {
  margin-top: 20px;
}

/* 登录按钮样式 */
.login-button {
  width: 100%;
  margin-top: 10px;
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .login-card {
    max-width: 100%;
    margin: 0 10px;
  }

  .login-form {
    margin-top: 10px;
  }
}
</style>
