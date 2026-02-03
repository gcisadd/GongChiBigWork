<template>
  <div class="register-container">
    <!-- 注册卡片容器 -->
    <el-card class="register-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>用户注册</h2>
        </div>
      </template>

      <!-- 注册表单 -->
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        class="register-form"
      >
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20个字符）"
            :prefix-icon="User"
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 邮箱输入框 -->
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            :prefix-icon="Message"
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 手机号输入框 -->
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号（可选）"
            :prefix-icon="Phone"
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（6-20个字符）"
            :prefix-icon="Lock"
            show-password
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 确认密码输入框 -->
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
            size="large"
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-button"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>

        <!-- 登录链接 -->
        <el-form-item>
          <div class="login-link">
            已有账号？<el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Lock, Message, Phone, User } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

/**
 * 注册页面组件
 *
 * 提供用户注册功能，包含用户名、邮箱、手机号、密码输入、表单验证、注册提交等功能
 * 使用 Element Plus 组件库构建美观的注册界面
 * 注册成功后跳转到登录页面
 *
 * @component
 */

/**
 * 注册表单数据接口
 *
 * @interface RegisterForm
 * @property {string} username - 用户名
 * @property {string} email - 邮箱
 * @property {string} phone - 手机号（可选）
 * @property {string} password - 密码
 * @property {string} confirmPassword - 确认密码
 */
interface RegisterForm {
  username: string
  email: string
  phone: string
  password: string
  confirmPassword: string
}

// 路由实例，用于页面跳转
const router = useRouter()

// 表单引用对象，用于表单验证和重置
const registerFormRef = ref<FormInstance>()

// 注册按钮加载状态
const loading = ref(false)

// 注册表单数据
const registerForm = reactive<RegisterForm>({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

/**
 * 验证确认密码是否与密码一致
 *
 * @param rule - 验证规则对象
 * @param value - 输入的值
 * @param callback - 回调函数
 */
const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

/**
 * 验证手机号格式（可选）
 *
 * @param rule - 验证规则对象
 * @param value - 输入的值
 * @param callback - 回调函数
 */
const validatePhone = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value && !/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号格式'))
  } else {
    callback()
  }
}

/**
 * 表单验证规则
 *
 * @input 表单字段值
 * @process 1. 检查用户名是否为空
 *          2. 检查邮箱格式是否正确
 *          3. 检查密码长度是否符合要求
 *          4. 检查两次密码是否一致
 * @output 返回验证错误信息或通过验证
 */
const registerRules: FormRules<RegisterForm> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

/**
 * 跳转到登录页面
 */
const goToLogin = () => {
  router.push('/login')
}

/**
 * 处理注册提交
 *
 * @input 用户点击注册按钮或按回车键
 * @process 1. 验证表单字段是否符合规则
 *          2. 如果验证通过，调用后端注册 API
 *          3. 注册成功后跳转到登录页面
 * @output 跳转到登录页面或显示错误消息
 */
const handleRegister = async () => {
  if (!registerFormRef.value) return

  // 验证表单
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        // 调用后端注册 API
        await authApi.register({
          username: registerForm.username,
          email: registerForm.email,
          phone: registerForm.phone || undefined,
          password: registerForm.password,
        })

        ElMessage.success('注册成功，请登录')
        // 跳转到登录页面
        router.push('/login')
      } catch (error: unknown) {
        // 显示错误消息
        const errorMessage = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || '注册失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 注册容器样式 - 全屏居中显示注册卡片 */
.register-container {
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

/* 注册卡片样式 */
.register-card {
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

/* 注册表单样式 */
.register-form {
  margin-top: 20px;
}

/* 注册按钮样式 */
.register-button {
  width: 100%;
  margin-top: 10px;
}

/* 登录链接样式 */
.login-link {
  width: 100%;
  text-align: center;
  color: #606266;
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .register-card {
    max-width: 100%;
    margin: 0 10px;
  }

  .register-form {
    margin-top: 10px;
  }
}
</style>
