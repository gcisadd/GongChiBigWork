/**
 * WebSocket 协作编辑服务模块
 *
 * 提供实时协作编辑功能，支持多用户同时编辑同一个文档
 * 使用 WebSocket 实现实时通信
 */

import { ref, type Ref } from 'vue'

/**
 * 协作用户信息
 */
interface CollaboratorInfo {
  username: string
  cursor?: {
    index: number
    length: number
  }
  color?: string
}

type MessageType =
  | 'join'
  | 'user_joined'
  | 'user_left'
  | 'content_change'
  | 'cursor_position'
  | 'sync_request'
  | 'sync_users'
  | 'sync_content'
  | 'ping'
  | 'pong'

/**
 * 消息数据接口
 */
interface MessageData {
  type: MessageType
  username?: string
  users?: string[]
  delta?: Record<string, unknown>
  source?: string
  content?: string
  cursor?: {
    index: number
    length: number
  }
}

/**
 * WebSocket 协作服务类
 *
 * 管理 WebSocket 连接、消息发送和接收
 * 支持多用户实时协作编辑
 */
class CollaborationService {
  private ws: WebSocket | null = null
  private documentId: number = 0
  private username: string = ''
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 1000
  private messageQueue: MessageData[] = []
  private serverUrl: string = ''

  // 已处理 delta 的去重 Set（防止重复应用）
  private processedDeltas: Set<string> = new Set()

  // 在线用户列表
  onlineUsers: Ref<string[]> = ref([])

  // 其他用户光标位置
  cursors: Ref<Map<string, CollaboratorInfo>> = ref(new Map())

  // 连接状态
  isConnected: Ref<boolean> = ref(false)

  // 连接错误信息
  connectionError: Ref<string> = ref('')

  // 消息回调
  private onContentChange: ((delta: Record<string, unknown>, source: string) => void) | null =
    null
  private onUserJoined: ((username: string, users: string[]) => void) | null = null
  private onUserLeft: ((username: string, users: string[]) => void) | null = null
  private onSyncUsers: ((users: string[]) => void) | null = null
  private onSyncContent: ((content: string) => void) | null = null
  private onCursorPosition:
    | ((username: string, cursor: { index: number; length: number }) => void)
    | null = null

  /**
   * 获取服务器 URL
   */
  private getServerUrl(): string {
    // 优先使用环境变量配置的后端地址
    const wsHost = import.meta.env?.VITE_WS_HOST || 'localhost:8000'
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${wsHost}/ws/collaborate/${this.documentId}`
  }

  /**
   * 连接到协作房间
   *
   * @param documentId - 文档ID
   * @param username - 用户名
   * @returns 是否连接成功
   */
  async connect(documentId: number, username: string): Promise<boolean> {
    this.documentId = documentId
    this.username = username
    this.connectionError.value = ''
    this.reconnectAttempts = 0

    // 生成 WebSocket URL
    this.serverUrl = this.getServerUrl()
    console.log(`[协作] 正在连接到: ${this.serverUrl}`)

    return new Promise((resolve) => {
      try {
        this.ws = new WebSocket(this.serverUrl)

        // 设置连接超时
        const timeout = setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            console.error('[协作] 连接超时')
            this.connectionError.value = '连接超时，请检查后端服务是否运行'
            this.ws?.close()
            this.ws = null
            resolve(false)
          }
        }, 10000)

        this.ws.onopen = () => {
          console.log('[协作] WebSocket 连接已建立')
          clearTimeout(timeout)

          // 发送加入消息
          this.send({
            type: 'join',
            username: this.username,
          })

          // 发送消息队列中的消息
          this.flushMessageQueue()

          this.isConnected.value = true
          this.reconnectAttempts = 0
          resolve(true)
        }

        this.ws.onmessage = (event) => {
          console.log('[协作] onmessage 原始数据:', event.data)
          try {
            const data: MessageData = JSON.parse(event.data)
            console.log('[协作] 解析后的消息:', data)
            this.handleMessage(data)
          } catch (error) {
            console.error('[协作] 解析 WebSocket 消息失败:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log(`[协作] WebSocket 连接已关闭: code=${event.code}, reason=${event.reason || '无'}`)
          this.isConnected.value = false

          // 保存错误信息
          if (event.code !== 1000 && event.code !== 1001) {
            this.connectionError.value = `连接已断开 (code: ${event.code})`
          }

          // 尝试重连（如果不是正常关闭）
          if (this.reconnectAttempts < this.maxReconnectAttempts && event.code !== 1000) {
            console.log(`[协作] 准备重连...`)
            this.reconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('[协作] WebSocket 错误:', error)
          this.connectionError.value = '无法连接到协作服务器，请确保后端服务已启动'
          resolve(false)
        }
      } catch (error) {
        console.error('[协作] 创建 WebSocket 连接失败:', error)
        this.connectionError.value = '创建连接失败，请检查网络设置'
        resolve(false)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected.value = false
    this.onlineUsers.value = []
    this.cursors.value.clear()
  }

  /**
   * 发送消息
   *
   * @param message - 消息数据
   */
  send(message: MessageData): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      // 连接未建立，先加入队列
      this.messageQueue.push(message)
    }
  }

  /**
   * 发送内容变更
   *
   * @param delta - Quill delta 对象
   * @param source - 变更来源
   */
  sendContentChange(delta: Record<string, unknown>, source: string = 'user'): void {
    // 不修改原始 delta，避免序列号影响 Quill 处理
    // 直接发送原始 delta，后端会广播给其他用户
    this.send({
      type: 'content_change',
      username: this.username,
      delta,
      source,
    })
  }

  /**
   * 发送光标位置
   *
   * @param index - 光标起始位置
   * @param length - 选中文本长度
   */
  sendCursorPosition(index: number, length: number = 0): void {
    this.send({
      type: 'cursor_position',
      username: this.username,
      cursor: { index, length },
    })
  }

  /**
   * 请求同步用户列表
   */
  requestSync(): void {
    this.send({
      type: 'sync_request',
    })
  }

  /**
   * 设置内容变更回调
   */
  onContentChangeCallback(
    callback: (delta: Record<string, unknown>, source: string) => void
  ): void {
    this.onContentChange = callback
  }

  /**
   * 设置用户加入回调
   */
  onUserJoinedCallback(callback: (username: string, users: string[]) => void): void {
    this.onUserJoined = callback
  }

  /**
   * 设置用户离开回调
   */
  onUserLeftCallback(callback: (username: string, users: string[]) => void): void {
    this.onUserLeft = callback
  }

  /**
   * 设置用户列表同步回调
   */
  onSyncUsersCallback(callback: (users: string[]) => void): void {
    this.onSyncUsers = callback
  }

  /**
   * 设置内容同步回调
   */
  onSyncContentCallback(callback: (content: string) => void): void {
    this.onSyncContent = callback
  }

  /**
   * 设置光标位置回调
   */
  onCursorPositionCallback(
    callback: (username: string, cursor: { index: number; length: number }) => void
  ): void {
    this.onCursorPosition = callback
  }

  /**
   * 处理接收到的消息
   *
   * @param data - 消息数据
   */
  private handleMessage(data: MessageData): void {
    console.log('[协作] 收到消息:', JSON.stringify(data))

    switch (data.type) {
      case 'user_joined':
        console.log('[协作] 处理 user_joined:', data.username, '在线用户:', data.users)
        this.onlineUsers.value = data.users || []
        this.onUserJoined?.(data.username || '', this.onlineUsers.value)
        break

      case 'user_left':
        console.log('[协作] 处理 user_left:', data.username)
        this.onlineUsers.value = data.users || []
        // 移除离开用户的光标
        if (data.username) {
          this.cursors.value.delete(data.username)
        }
        this.onUserLeft?.(data.username || '', this.onlineUsers.value)
        break

      case 'content_change':
        console.log('[协作] 收到 content_change:', JSON.stringify(data))
        if (data.delta && data.username !== this.username) {
          // 生成 delta 的唯一标识（用户名 + delta 内容）
          const deltaKey = `${data.username}-${JSON.stringify(data.delta)}`

          // 检查是否已经处理过这个 delta
          if (this.processedDeltas.has(deltaKey)) {
            console.log('[协作] 跳过已处理的 delta:', deltaKey)
            break
          }

          // 标记为已处理
          this.processedDeltas.add(deltaKey)

          // 10秒后清理这个标记
          setTimeout(() => {
            this.processedDeltas.delete(deltaKey)
          }, 10000)

          // 直接处理 delta
          console.log('[协作] 处理 delta:', JSON.stringify(data.delta))
          this.onContentChange?.(data.delta, data.source || 'remote')
        }
        break

      case 'cursor_position':
        if (data.username && data.username !== this.username && data.cursor) {
          const cursors = this.cursors.value
          const collaborator = cursors.get(data.username) || {
            username: data.username,
          }
          collaborator.cursor = data.cursor
          collaborator.color = this.generateUserColor(data.username)
          cursors.set(data.username, collaborator)
          this.cursors.value = new Map(cursors)
          // 触发回调
          this.onCursorPosition?.(data.username, data.cursor)
        }
        break

      case 'sync_users':
        console.log('[协作] 处理 sync_users:', data.users)
        this.onlineUsers.value = data.users || []
        this.onSyncUsers?.(this.onlineUsers.value)
        break

      case 'sync_content':
        console.log('[协作] 收到 sync_content, 内容长度:', data.content?.length)
        if (data.content) {
          this.onSyncContent?.(data.content)
        }
        break

      case 'pong':
        // 心跳响应
        break

      default:
        console.log('[协作] 未知消息类型:', data.type)
    }
  }

  /**
   * 尝试重连
   */
  private reconnect(): void {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`[协作] 尝试重连（${this.reconnectAttempts}/${this.maxReconnectAttempts}），${delay}ms 后...`)
    this.connectionError.value = `正在重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`

    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect(this.documentId, this.username)
      } else {
        console.error('[协作] 重连次数已达上限，停止重连')
        this.connectionError.value = '无法连接到协作服务器，请刷新页面重试'
      }
    }, delay)
  }

  /**
   * 清空消息队列
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message))
      }
    }
  }

  /**
   * 根据用户名生成用户颜色
   *
   * @param username - 用户名
   * @returns 颜色代码
   */
  private generateUserColor(username: string): string {
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

    // 确保 colors 数组不为空
    if (colors.length === 0) {
      return '#85C1E9' // 默认颜色
    }

    let hash = 0
    for (let i = 0; i < username.length; i++) {
      hash = username.charCodeAt(i) + ((hash << 5) - hash)
    }

    return colors[Math.abs(hash) % colors.length] ?? '#85C1E9'
  }
}

// 创建单例实例
const collaborationService = new CollaborationService()

export default collaborationService
