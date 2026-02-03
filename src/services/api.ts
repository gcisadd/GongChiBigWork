/**
 * 后端 API 服务模块
 *
 * 提供与后端服务器通信的统一接口，包含认证、文档管理、个人信息等功能
 * 使用 axios 进行 HTTP 请求，自动处理 token 认证
 */

import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

/**
 * API 基础配置
 *
 * @constant
 * @property {string} BASE_URL - 后端 API 服务器地址
 * @property {number} TIMEOUT - 请求超时时间（毫秒）
 */
const API_BASE_URL = 'http://localhost:8000'
const API_TIMEOUT = 30000

/**
 * 创建 axios 实例
 *
 * @description 配置请求拦截器和响应拦截器
 * @returns {AxiosInstance} 配置后的 axios 实例
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 请求拦截器
 *
 * @description 在请求发送前自动添加认证 token
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')

    // 如果存在 token，添加到请求头
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    // 请求错误处理
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 *
 * @description 统一处理响应错误，包括 token 过期等
 */
api.interceptors.response.use(
  (response) => {
    // 成功响应，直接返回数据
    return response
  },
  (error) => {
    // 错误响应处理
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Token 过期或无效，清除本地存储并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('username')
          window.location.href = '/about'
          break
        case 403:
          // 无权限访问
          console.error('无权访问:', data?.detail || '没有权限')
          break
        case 404:
          // 资源不存在
          console.error('资源不存在:', data?.detail || '请求的资源未找到')
          break
        case 500:
          // 服务器错误
          console.error('服务器错误:', data?.detail || '内部服务器错误')
          break
        default:
          // 其他错误
          console.error('请求错误:', data?.detail || error.message)
      }
    } else if (error.request) {
      // 请求已发送但未收到响应
      console.error('网络错误:', '无法连接到服务器，请检查网络连接')
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message)
    }

    return Promise.reject(error)
  }
)

/**
 * 认证相关 API
 */
export const authApi = {
  /**
   * 用户登录
   *
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @param {boolean} remember - 是否记住登录状态
   * @returns {Promise} 登录结果，包含 access_token 和 username
   */
  login: async (username: string, password: string, remember: boolean = false) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    // 保存 token 到本地存储
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('username', response.data.username)
    }

    return response.data
  },

  /**
   * 用户注册
   *
   * @param {Object} userData - 用户注册信息
   * @param {string} userData.username - 用户名
   * @param {string} userData.password - 密码
   * @param {string} userData.email - 邮箱
   * @param {string} [userData.phone] - 手机号（可选）
   * @returns {Promise} 注册结果，包含新创建的用户信息
   */
  register: async (userData: {
    username: string
    password: string
    email: string
    phone?: string
  }) => {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  /**
   * 获取当前用户信息
   *
   * @returns {Promise} 当前用户信息
   */
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

/**
 * 文档管理相关 API
 */
export const documentApi = {
  /**
   * 获取文档列表
   *
   * @param {number} page - 页码，从 1 开始
   * @param {number} pageSize - 每页数量
   * @returns {Promise} 文档列表和总数
   */
  getDocuments: async (page: number = 1, pageSize: number = 10) => {
    const response = await api.get('/api/documents', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  /**
   * 获取单个文档详情
   *
   * @param {number} documentId - 文档 ID
   * @returns {Promise} 文档详情
   */
  getDocument: async (documentId: number) => {
    const response = await api.get(`/api/documents/${documentId}`)
    return response.data
  },

  /**
   * 创建新文档
   *
   * @param {Object} documentData - 文档数据
   * @param {string} documentData.title - 文档标题
   * @param {string} [documentData.content] - 文档内容（HTML 格式）
   * @returns {Promise} 新创建的文档
   */
  createDocument: async (documentData: { title: string; content?: string }) => {
    const response = await api.post('/api/documents', documentData)
    return response.data
  },

  /**
   * 更新文档
   *
   * @param {number} documentId - 文档 ID
   * @param {Object} documentData - 要更新的文档数据
   * @param {string} [documentData.title] - 文档标题
   * @param {string} [documentData.content] - 文档内容
   * @returns {Promise} 更新后的文档
   */
  updateDocument: async (
    documentId: number,
    documentData: { title?: string; content?: string }
  ) => {
    const response = await api.put(`/api/documents/${documentId}`, documentData)
    return response.data
  },

  /**
   * 删除文档
   *
   * @param {number} documentId - 文档 ID
   * @returns {Promise} 删除结果
   */
  deleteDocument: async (documentId: number) => {
    const response = await api.delete(`/api/documents/${documentId}`)
    return response.data
  },
}

/**
 * 个人信息相关 API
 */
export const profileApi = {
  /**
   * 获取当前用户个人信息
   *
   * @returns {Promise} 用户信息
   */
  getProfile: async () => {
    const response = await api.get('/api/profile')
    return response.data
  },

  /**
   * 更新当前用户个人信息
   *
   * @param {Object} profileData - 要更新的个人信息
   * @param {string} [profileData.phone] - 手机号
   * @param {string} [profileData.bio] - 个人简介
   * @returns {Promise} 更新后的用户信息
   */
  updateProfile: async (profileData: { phone?: string; bio?: string }) => {
    const response = await api.put('/api/profile', profileData)
    return response.data
  },
}

/**
 * 健康检查
 *
 * @returns {Promise} 健康状态
 */
export const healthCheck = async () => {
  const response = await api.get('/api/health')
  return response.data
}

export default api
