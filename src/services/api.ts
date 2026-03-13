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
   * @param {Array} [documentData.permissions] - 权限列表
   * @returns {Promise} 新创建的文档
   */
  createDocument: async (documentData: { title: string; content?: string; permissions?: Array<{user_id: number, permission_level: string}> }) => {
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

  /**
   * AI 概括文档内容
   *
   * @param {string} content - 文档内容
   * @returns {Promise} AI 概括结果
   */
  generateAISummary: async (content: string) => {
    const response = await api.post('/api/documents/ai-summary', { content })
    return response.data
  },

  /**
   * 更新文档概括
   *
   * @param {number} documentId - 文档 ID
   * @param {string} summary - 概括内容
   * @returns {Promise} 更新后的文档
   */
  updateDocumentSummary: async (documentId: number, summary: string) => {
    const response = await api.put(`/api/documents/${documentId}/summary`, { summary })
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
  updateProfile: async (profileData: { phone?: string; bio?: string; avatar?: string }) => {
    const response = await api.put('/api/profile', profileData)
    return response.data
  },

  /**
   * 获取指定用户的头像
   *
   * @param {number} userId - 用户ID
   * @returns {Promise} 头像数据（Base64）
   */
  getUserAvatar: async (userId: number) => {
    const response = await api.get(`/api/profile/${userId}/avatar`)
    return response.data
  },

  /**
   * 根据用户名获取用户头像（用于协作编辑等展示）
   *
   * @param {string} username - 用户名
   * @returns {Promise} 头像数据（Base64）
   */
  getAvatarByUsername: async (username: string) => {
    const response = await api.get(`/api/profile/by-username/${encodeURIComponent(username)}/avatar`)
    return response.data
  },

  /**
   * 上传/更新当前用户头像
   *
   * @param {string} avatar - 头像Base64数据
   * @returns {Promise} 操作结果
   */
  uploadAvatar: async (avatar: string) => {
    const response = await api.post('/api/profile/avatar', { avatar })
    return response.data
  },
}

/**
 * 好友管理相关 API
 */
export const friendApi = {
  /**
   * 搜索用户
   *
   * @param {string} q - 搜索关键词
   * @returns {Promise} 匹配的用户列表
   */
  searchUsers: async (q: string) => {
    const response = await api.get('/api/friends/search', { params: { q } })
    return response.data
  },

  /**
   * 获取好友列表
   *
   * @returns {Promise} 好友列表
   */
  getFriends: async () => {
    const response = await api.get('/api/friends/friends')
    return response.data
  },

  /**
   * 获取收到的好友请求列表
   *
   * @returns {Promise} 收到的好友请求列表
   */
  getReceivedRequests: async () => {
    const response = await api.get('/api/friends/requests/received')
    return response.data
  },

  /**
   * 获取发送的好友请求列表
   *
   * @returns {Promise} 发送的好友请求列表
   */
  getSentRequests: async () => {
    const response = await api.get('/api/friends/requests/sent')
    return response.data
  },

  /**
   * 发送好友请求
   *
   * @param {string} username - 目标用户名
   * @returns {Promise} 操作结果
   */
  sendFriendRequest: async (username: string) => {
    const response = await api.post('/api/friends/request', { username })
    return response.data
  },

  /**
   * 接受好友请求
   *
   * @param {number} requestId - 好友请求ID
   * @returns {Promise} 操作结果
   */
  acceptFriendRequest: async (requestId: number) => {
    const response = await api.post(`/api/friends/request/${requestId}/accept`)
    return response.data
  },

  /**
   * 拒绝好友请求
   *
   * @param {number} requestId - 好友请求ID
   * @returns {Promise} 操作结果
   */
  rejectFriendRequest: async (requestId: number) => {
    const response = await api.post(`/api/friends/request/${requestId}/reject`)
    return response.data
  },

  /**
   * 删除好友
   *
   * @param {number} friendId - 好友ID
   * @returns {Promise} 操作结果
   */
  removeFriend: async (friendId: number) => {
    const response = await api.delete(`/api/friends/friend/${friendId}`)
    return response.data
  },

  /**
   * 取消发送的好友请求
   *
   * @param {number} requestId - 好友请求ID
   * @returns {Promise} 操作结果
   */
  cancelFriendRequest: async (requestId: number) => {
    const response = await api.delete(`/api/friends/request/${requestId}`)
    return response.data
  },
}

/**
 * 文档权限管理相关 API
 */
export const permissionApi = {
  /**
   * 获取当前用户有权限访问的文档列表
   *
   * @returns {Promise} 文档列表（包含权限信息）
   */
  getAccessibleDocuments: async () => {
    const response = await api.get('/api/documents')
    return response.data
  },

  /**
   * 获取文档的权限列表
   *
   * @param {number} documentId - 文档ID
   * @returns {Promise} 权限列表
   */
  getDocumentPermissions: async (documentId: number) => {
    const response = await api.get(`/api/documents/${documentId}/permissions`)
    return response.data
  },

  /**
   * 为文档添加权限
   *
   * @param {number} documentId - 文档ID
   * @param {Object} permissionData - 权限数据
   * @param {number} permissionData.user_id - 被授权用户ID
   * @param {string} permissionData.permission_level - 权限级别：'view' 或 'edit'
   * @returns {Promise} 操作结果
   */
  addDocumentPermission: async (
    documentId: number,
    permissionData: { user_id: number; permission_level: string }
  ) => {
    const response = await api.post(
      `/api/documents/${documentId}/permissions`,
      permissionData
    )
    return response.data
  },

  /**
   * 更新文档权限
   *
   * @param {number} documentId - 文档ID
   * @param {number} userId - 被授权用户ID
   * @param {string} permissionLevel - 权限级别：'view' 或 'edit'
   * @returns {Promise} 操作结果
   */
  updateDocumentPermission: async (
    documentId: number,
    userId: number,
    permissionLevel: string
  ) => {
    const response = await api.put(
      `/api/documents/${documentId}/permissions/${userId}`,
      { permission_level: permissionLevel }
    )
    return response.data
  },

  /**
   * 撤销文档权限
   *
   * @param {number} documentId - 文档ID
   * @param {number} userId - 被授权用户ID
   * @returns {Promise} 操作结果
   */
  revokeDocumentPermission: async (documentId: number, userId: number) => {
    const response = await api.delete(
      `/api/documents/${documentId}/permissions/${userId}`
    )
    return response.data
  },

  /**
   * 检查当前用户对文档的访问权限级别
   *
   * @param {number} documentId - 文档ID
   * @returns {Promise} 权限级别信息
   */
  checkDocumentAccess: async (documentId: number) => {
    const response = await api.get(`/api/documents/${documentId}/access`)
    return response.data
  },
}

/**
 * 评论管理相关 API
 */
export const commentApi = {
  /**
   * 获取文档的评论列表
   *
   * @param {number} documentId - 文档ID
   * @returns {Promise} 评论列表（树形结构）
   */
  getComments: async (documentId: number) => {
    const response = await api.get(`/api/documents/${documentId}/comments`)
    return response.data
  },

  /**
   * 创建评论
   *
   * @param {number} documentId - 文档ID
   * @param {Object} commentData - 评论数据
   * @param {string} commentData.content - 评论内容
   * @returns {Promise} 创建的评论
   */
  createComment: async (documentId: number, commentData: { content: string }) => {
    const response = await api.post(`/api/documents/${documentId}/comments`, commentData)
    return response.data
  },

  /**
   * 回复评论
   *
   * @param {number} documentId - 文档ID
   * @param {Object} replyData - 回复数据
   * @param {string} replyData.content - 回复内容
   * @param {number} replyData.parent_id - 父评论ID
   * @returns {Promise} 创建的回复
   */
  replyComment: async (
    documentId: number,
    replyData: { content: string; parent_id: number }
  ) => {
    const response = await api.post(`/api/documents/${documentId}/comments/reply`, replyData)
    return response.data
  },

  /**
   * 删除评论
   *
   * @param {number} documentId - 文档ID
   * @param {number} commentId - 评论ID
   * @returns {Promise} 操作结果
   */
  deleteComment: async (documentId: number, commentId: number) => {
    const response = await api.delete(`/api/documents/${documentId}/comments/${commentId}`)
    return response.data
  },

  /**
   * 编辑评论
   *
   * @param {number} documentId - 文档ID
   * @param {number} commentId - 评论ID
   * @param {Object} commentData - 评论数据
   * @param {string} commentData.content - 评论内容
   * @returns {Promise} 更新后的评论
   */
  updateComment: async (
    documentId: number,
    commentId: number,
    commentData: { content: string }
  ) => {
    const response = await api.put(
      `/api/documents/${documentId}/comments/${commentId}`,
      commentData
    )
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
