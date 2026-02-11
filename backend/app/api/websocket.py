"""
WebSocket 服务模块

提供实时协作编辑功能，支持多用户同时编辑同一个文档
使用 FastAPI 的 WebSocket 端点实现实时通信
"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """
    WebSocket 连接管理器

    管理所有 WebSocket 连接，按文档ID分组
    支持广播消息给特定文档房间的所有用户
    """

    def __init__(self):
        """
        初始化连接管理器

        @output 创建空的连接字典和在线用户字典
        """
        # active_connections: {document_id: {WebSocket连接}}
        self.active_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        # online_users: {document_id: {username}}
        self.online_users: Dict[int, Set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, document_id: int, username: str):
        """
        建立 WebSocket 连接

        @input websocket - WebSocket 连接对象（已接受）
        @input document_id - 文档ID
        @input username - 用户名
        @process 1. 将连接添加到文档房间
                  2. 广播用户加入消息
        @output 建立连接，在线用户列表更新
        """
        print(f"[WebSocket] 用户 {username} 已连接, document_id={document_id}")
        self.active_connections[document_id].add(websocket)
        print(f"[WebSocket] 当前连接数: {len(self.active_connections[document_id])}")
        self.online_users[document_id].add(username)

        # 广播用户加入消息
        print(f"[WebSocket] 准备广播 user_joined, 当前在线用户: {list(self.online_users[document_id])}")
        await self.broadcast_to_document(
            document_id,
            {
                "type": "user_joined",
                "username": username,
                "users": list(self.online_users[document_id]),
            },
            websocket,
        )
        print(f"[WebSocket] 广播完成")

    def disconnect(self, websocket: WebSocket, document_id: int, username: str):
        """
        断开 WebSocket 连接

        @input websocket - WebSocket 连接对象
        @input document_id - 文档ID
        @input username - 用户名
        @process 1. 从文档房间移除连接
                  2. 移除用户
                  3. 广播用户离开消息
        @output 断开连接，在线用户列表更新
        """
        if websocket in self.active_connections[document_id]:
            self.active_connections[document_id].remove(websocket)

        self.online_users[document_id].discard(username)

        # 如果房间为空，清理房间
        if not self.active_connections[document_id]:
            del self.active_connections[document_id]
            del self.online_users[document_id]

    async def broadcast_to_document(
        self, document_id: int, message: dict, exclude: WebSocket | None = None
    ):
        """
        广播消息给指定文档房间的所有用户

        @input document_id - 文档ID
        @input message - 要广播的消息
        @input exclude - 要排除的连接（发送者）
        @process 遍历所有连接，发送消息给除发送者外的所有用户
        @output 消息广播给所有在线用户
        """
        connections = self.active_connections.get(document_id, set())
        print(f"[WebSocket] 广播消息: type={message.get('type')}, document_id={document_id}, 连接数={len(connections)}")
        for connection in connections:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                    print(f"[WebSocket] 广播成功给连接")
                except Exception as e:
                    print(f"[WebSocket] 广播失败: {e}")
                    pass

    async def broadcast_content_change(
        self, document_id: int, username: str, delta: dict, source: str
    ):
        """
        广播内容变更

        @input document_id - 文档ID
        @input username - 用户名
        @input delta - Quill delta 对象
        @input source - 变更来源（'user' 或 'api'）
        @process 广播内容变更给其他用户
        @output 其他用户收到内容更新
        """
        print(f"[WebSocket] 广播内容变更: username={username}, delta keys={list(delta.keys())}")
        await self.broadcast_to_document(
            document_id,
            {
                "type": "content_change",
                "username": username,
                "delta": delta,
                "source": "remote",  # 标识为远程变更
            },
        )

    async def broadcast_cursor_position(
        self, document_id: int, username: str, cursor: dict
    ):
        """
        广播光标位置

        @input document_id - 文档ID
        @input username - 用户名
        @input cursor - 光标位置信息
        @process 广播光标位置给其他用户
        @output 其他用户显示发送者的光标位置
        """
        print(f"[WebSocket] 广播光标位置: username={username}, cursor={cursor}")
        await self.broadcast_to_document(
            document_id,
            {
                "type": "cursor_position",
                "username": username,
                "cursor": cursor,
            },
            None,  # 发送给包括发送者的所有用户
        )

    def get_online_users(self, document_id: int) -> list:
        """
        获取指定文档的在线用户列表

        @input document_id - 文档ID
        @output 在线用户列表
        """
        return list(self.online_users.get(document_id, set()))


# 创建全局连接管理器实例
manager = ConnectionManager()


@router.websocket("/ws/collaborate/{document_id}")
async def websocket_collaborate(websocket: WebSocket, document_id: int):
    """
    协作编辑 WebSocket 端点

    @input websocket - WebSocket 连接
    @input document_id - 文档ID，从 URL 路径获取
    @process 1. 接受连接
              2. 等待连接参数（用户名）
              3. 建立连接
              4. 处理消息循环
              5. 断开连接
    @output 实时协作编辑功能
    """
    username = None

    try:
        # 先接受连接（重要：必须在接收数据前调用）
        await websocket.accept()
        print(f"[WebSocket] 客户端已连接: document_id={document_id}")

        # 等待接收用户名
        data = await websocket.receive_json()
        if data.get("type") != "join":
            print(f"[WebSocket] 收到未知消息类型: {data.get('type')}")
            await websocket.close(code=4000)
            return

        username = data.get("username", "匿名用户")
        print(f"[WebSocket] 用户加入: {username}")

        # 建立连接
        await manager.connect(websocket, document_id, username)

        # 处理消息循环
        while True:
            try:
                data = await websocket.receive_json()

                message_type = data.get("type")

                if message_type == "content_change":
                    # 内容变更
                    raw_delta = data.get("delta", {})
                    print(f"[WebSocket] 收到 content_change, delta keys: {list(raw_delta.keys())}")
                    # 如果 delta 嵌套了（前端问题），解包
                    delta = raw_delta.get("delta") if "delta" in raw_delta else raw_delta
                    source = data.get("source", "user")
                    print(f"[WebSocket] 处理后 delta keys: {list(delta.keys())}, source: {source}")
                    await manager.broadcast_content_change(
                        document_id, username, delta, source
                    )

                elif message_type == "cursor_position":
                    # 光标位置
                    cursor = data.get("cursor", {})
                    await manager.broadcast_cursor_position(document_id, username, cursor)

                elif message_type == "sync_request":
                    # 同步请求 - 发送当前在线用户列表
                    await websocket.send_json(
                        {
                            "type": "sync_users",
                            "users": manager.get_online_users(document_id),
                        }
                    )

                elif message_type == "ping":
                    # 心跳包
                    await websocket.send_json({"type": "pong"})
                else:
                    print(f"[WebSocket] 收到未知消息类型: {message_type}")

            except WebSocketDisconnect:
                print(f"[WebSocket] 用户断开连接: {username}")
                break
            except Exception as e:
                print(f"[WebSocket] 处理消息时出错: {e}")
                break

    except WebSocketDisconnect:
        print(f"[WebSocket] 连接断开: document_id={document_id}")
        pass
    except Exception as e:
        print(f"[WebSocket] 错误: {e}")
    finally:
        # 断开连接
        if username is not None:
            manager.disconnect(websocket, document_id, username)

            # 广播用户离开消息
            if document_id in manager.active_connections:
                await manager.broadcast_to_document(
                    document_id,
                    {
                        "type": "user_left",
                        "username": username,
                        "users": manager.get_online_users(document_id),
                    },
                )


@router.get("/ws/online-users/{document_id}")
async def get_online_users(document_id: int):
    """
    获取指定文档的在线用户列表

    @input document_id - 文档ID
    @output 在线用户列表
    """
    return {"users": manager.get_online_users(document_id)}
