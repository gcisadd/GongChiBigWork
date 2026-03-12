/**
 * WebSocket 协作编辑服务模块
 *
 * 提供实时协作编辑功能，支持多用户同时编辑同一个文档
 * 使用 WebSocket 实现实时通信
 */

import { ref, type Ref } from "vue";

/**
 * 协作用户信息
 */
interface CollaboratorInfo {
  username: string;
  cursor?: {
    index: number;
    length: number;
  };
  color?: string;
}

type MessageType =
  | "join"
  | "user_joined"
  | "user_left"
  | "prepare_sync"
  | "content_change"
  | "cursor_position"
  | "sync_request"
  | "sync_users"
  | "sync_content"
  | "ping"
  | "pong"
  | "document_saved"
  | "save_done"; // 保存完成后请求同步内容

/**
 * 消息数据接口
 */
interface MessageData {
  type: MessageType;
  username?: string;
  users?: string[];
  delta?: Record<string, unknown>;
  source?: string;
  content?: string;
  cursor?: {
    index: number;
    length: number;
  };
  trigger_save?: boolean; // 标记是否触发保存
  title?: string; // 文档标题（用于 document_saved 消息）
  message?: string; // 消息内容（用于 document_saved 消息）
}

/**
 * WebSocket 协作服务类
 *
 * 管理 WebSocket 连接、消息发送和接收
 * 支持多用户实时协作编辑
 */
class CollaborationService {
  private ws: WebSocket | null = null;
  private documentId: number = 0;
  private username: string = "";
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private messageQueue: MessageData[] = [];
  private serverUrl: string = "";

  // 接收端短时窗去重：同一用户、同一 delta 在 80ms 内只应用一次，避免一次按键触发多次 text-change 导致“输入一个出现三个”
  private lastContentChangeKey: string = "";
  private lastContentChangeTime: number = 0;
  private static readonly CONTENT_CHANGE_DEDUP_MS = 80;

  // 在线用户列表
  onlineUsers: Ref<string[]> = ref([]);

  // 其他用户光标位置
  cursors: Ref<Map<string, CollaboratorInfo>> = ref(new Map());

  // 连接状态
  isConnected: Ref<boolean> = ref(false);

  // 连接错误信息
  connectionError: Ref<string> = ref("");

  // 消息回调
  private onContentChange:
    | ((delta: Record<string, unknown>, source: string, username: string) => void)
    | null = null;
  private onUserJoined: ((username: string, users: string[], triggerSave: boolean) => void) | null =
    null;
  private onUserLeft: ((username: string, users: string[], triggerSave: boolean) => void) | null =
    null;
  private onSyncUsers: ((users: string[]) => void) | null = null;
  private onSyncContent: ((content: string) => void) | null = null;
  private onCursorPosition:
    | ((username: string, cursor: { index: number; length: number }) => void)
    | null = null;
  private onDocumentSaved: ((username: string, title: string, message: string) => void) | null =
    null;
  // 用户加入/离开时触发保存的回调
  private onTriggerSave: (() => void) | null = null;

  /**
   * 获取服务器 URL
   */
  private getServerUrl(): string {
    // 优先使用环境变量配置的后端地址
    const wsHost = import.meta.env?.VITE_WS_HOST || "localhost:8000";
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${wsHost}/ws/collaborate/${this.documentId}`;
  }

  /**
   * 连接到协作房间
   *
   * @param documentId - 文档ID
   * @param username - 用户名
   * @returns 是否连接成功
   */
  async connect(documentId: number, username: string): Promise<boolean> {
    this.documentId = documentId;
    this.username = username;
    this.connectionError.value = "";
    this.reconnectAttempts = 0;

    // 生成 WebSocket URL
    this.serverUrl = this.getServerUrl();

    return new Promise((resolve) => {
      try {
        this.ws = new WebSocket(this.serverUrl);

        // 设置连接超时
        const timeout = setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            console.error("[协作] 连接超时");
            this.connectionError.value = "连接超时，请检查后端服务是否运行";
            this.ws?.close();
            this.ws = null;
            resolve(false);
          }
        }, 10000);

        this.ws.onopen = () => {
          clearTimeout(timeout);

          // 发送加入消息
          this.send({
            type: "join",
            username: this.username,
          });

          // 发送消息队列中的消息
          this.flushMessageQueue();

          this.isConnected.value = true;
          this.reconnectAttempts = 0;
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const data: MessageData = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error("[协作] 解析 WebSocket 消息失败:", error);
          }
        };

        this.ws.onclose = (event) => {
          this.isConnected.value = false;

          // 保存错误信息
          if (event.code !== 1000 && event.code !== 1001) {
            this.connectionError.value = `连接已断开 (code: ${event.code})`;
          }

          // 尝试重连（如果不是正常关闭）
          if (this.reconnectAttempts < this.maxReconnectAttempts && event.code !== 1000) {
            this.reconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error("[协作] WebSocket 错误:", error);
          this.connectionError.value = "无法连接到协作服务器，请确保后端服务已启动";
          resolve(false);
        };
      } catch (error) {
        console.error("[协作] 创建 WebSocket 连接失败:", error);
        this.connectionError.value = "创建连接失败，请检查网络设置";
        resolve(false);
      }
    });
  }

  /**
   * 断开连接
   * @param triggerSave - 是否在断开前触发保存（默认 true）
   */
  disconnect(triggerSave: boolean = true): void {
    // 在断开连接前，发送离开消息并请求保存
    if (triggerSave && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({
        type: "user_left",
        username: this.username,
        trigger_save: true, // 标记请求保存
      });
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected.value = false;
    this.onlineUsers.value = [];
    this.cursors.value.clear();
  }

  /**
   * 发送消息
   *
   * @param message - 消息数据
   */
  send(message: MessageData): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // 连接未建立，先加入队列
      this.messageQueue.push(message);
    }
  }

  /**
   * 发送内容变更
   *
   * @param delta - Quill delta 对象
   * @param source - 变更来源
   */
  sendContentChange(delta: Record<string, unknown>, source: string = "user"): void {
    // 不修改原始 delta，避免序列号影响 Quill 处理
    // 直接发送原始 delta，后端会广播给其他用户
    this.send({
      type: "content_change",
      username: this.username,
      delta,
      source,
    });
  }

  /**
   * 发送光标位置
   *
   * @param index - 光标起始位置
   * @param length - 选中文本长度
   */
  sendCursorPosition(index: number, length: number = 0): void {
    this.send({
      type: "cursor_position",
      username: this.username,
      cursor: { index, length },
    });
  }

  /**
   * 请求同步用户列表
   */
  requestSync(): void {
    this.send({
      type: "sync_request",
    });
  }

  /**
   * 保存完成后请求同步内容
   * 用于其他用户加入时，我们保存完后发送此消息请求最新内容
   */
  requestSyncAfterSave(): void {
    this.send({
      type: "save_done",
    });
  }

  /**
   * 设置内容变更回调
   */
  onContentChangeCallback(
    callback: (delta: Record<string, unknown>, source: string, username: string) => void,
  ): void {
    this.onContentChange = callback;
  }

  /**
   * 设置用户加入回调
   */
  onUserJoinedCallback(
    callback: (username: string, users: string[], triggerSave: boolean) => void,
  ): void {
    this.onUserJoined = callback;
  }

  /**
   * 设置用户离开回调
   */
  onUserLeftCallback(
    callback: (username: string, users: string[], triggerSave: boolean) => void,
  ): void {
    this.onUserLeft = callback;
  }

  /**
   * 设置用户列表同步回调
   */
  onSyncUsersCallback(callback: (users: string[]) => void): void {
    this.onSyncUsers = callback;
  }

  /**
   * 设置内容同步回调
   */
  onSyncContentCallback(callback: (content: string) => void): void {
    this.onSyncContent = callback;
  }

  /**
   * 设置请求内容回调（当其他用户加入时，请求当前内容）
   */
  onCursorPositionCallback(
    callback: (username: string, cursor: { index: number; length: number }) => void,
  ): void {
    this.onCursorPosition = callback;
  }

  /**
   * 设置文档保存回调
   */
  onDocumentSavedCallback(
    callback: (username: string, title: string, message: string) => void,
  ): void {
    this.onDocumentSaved = callback;
  }

  /**
   * 设置用户加入/离开时触发保存的回调
   */
  onTriggerSaveCallback(callback: () => void): void {
    this.onTriggerSave = callback;
  }

  /**
   * 处理接收到的消息
   *
   * @param data - 消息数据
   */
  private handleMessage(data: MessageData): void {
    switch (data.type) {
      case "user_joined":
        this.onlineUsers.value = data.users || [];
        // 获取 trigger_save 标记
        const joinTriggerSave = data.trigger_save === true;
        this.onUserJoined?.(data.username || "", this.onlineUsers.value, joinTriggerSave);
        // 如果收到保存触发请求，执行保存回调
        if (joinTriggerSave && this.onTriggerSave) {
          this.onTriggerSave();
        }
        break;

      case "prepare_sync": {
        // 服务端要求房间内老用户先保存一次，给新成员同步用
        if (data.trigger_save === true && this.onTriggerSave) {
          this.onTriggerSave();
        }
        break;
      }

      case "user_left":
        this.onlineUsers.value = data.users || [];
        // 移除离开用户的光标
        if (data.username) {
          this.cursors.value.delete(data.username);
        }
        // 获取 trigger_save 标记
        const leaveTriggerSave = data.trigger_save === true;
        this.onUserLeft?.(data.username || "", this.onlineUsers.value, leaveTriggerSave);
        // 如果收到保存触发请求，执行保存回调
        if (leaveTriggerSave && this.onTriggerSave) {
          this.onTriggerSave();
        }
        break;

      case "content_change":
        if (data.delta && data.username !== this.username) {
          const deltaKey = `${data.username}-${JSON.stringify(data.delta)}`;
          const now = Date.now();
          if (
            deltaKey === this.lastContentChangeKey &&
            now - this.lastContentChangeTime < CollaborationService.CONTENT_CHANGE_DEDUP_MS
          ) {
            break;
          }
          this.lastContentChangeKey = deltaKey;
          this.lastContentChangeTime = now;
          this.onContentChange?.(data.delta, data.source || "remote", data.username || "");
        }
        break;

      case "cursor_position":
        if (data.username && data.username !== this.username && data.cursor) {
          const cursors = this.cursors.value;
          const collaborator = cursors.get(data.username) || {
            username: data.username,
          };
          collaborator.cursor = data.cursor;
          collaborator.color = this.generateUserColor(data.username);
          cursors.set(data.username, collaborator);
          this.cursors.value = new Map(cursors);
          // 触发回调
          this.onCursorPosition?.(data.username, data.cursor);
        }
        break;

      case "sync_users":
        this.onlineUsers.value = data.users || [];
        this.onSyncUsers?.(this.onlineUsers.value);
        break;

      case "sync_content":
        if (data.content) {
          this.onSyncContent?.(data.content);
        }
        break;

      case "pong":
        // 心跳响应
        break;

      case "document_saved":
        if (data.username && data.username !== this.username && data.title) {
          // 通知其他用户文档已保存
          this.onDocumentSaved?.(
            data.username || "",
            data.title,
            data.message || `${data.username} 已保存文档`,
          );
        }
        break;

      default:
    }
  }

  /**
   * 尝试重连
   */
  private reconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    this.connectionError.value = `正在重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`;

    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect(this.documentId, this.username);
      } else {
        console.error("[协作] 重连次数已达上限，停止重连");
        this.connectionError.value = "无法连接到协作服务器，请刷新页面重试";
      }
    }, delay);
  }

  /**
   * 清空消息队列
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message));
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
      "#FF6B6B",
      "#4ECDC4",
      "#45B7D1",
      "#96CEB4",
      "#FFEAA7",
      "#DDA0DD",
      "#98D8C8",
      "#F7DC6F",
      "#BB8FCE",
      "#85C1E9",
    ];

    // 确保 colors 数组不为空
    if (colors.length === 0) {
      return "#85C1E9"; // 默认颜色
    }

    let hash = 0;
    for (let i = 0; i < username.length; i++) {
      hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }

    return colors[Math.abs(hash) % colors.length] ?? "#85C1E9";
  }
}

// 创建单例实例
const collaborationService = new CollaborationService();

export default collaborationService;
