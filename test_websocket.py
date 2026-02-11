"""
WebSocket 连接测试脚本
"""
import asyncio
import json

async def test_websocket():
    try:
        import websockets
        
        print("正在连接到 WebSocket...")
        async with websockets.connect("ws://localhost:8000/ws/collaborate/1") as websocket:
            print("连接成功！")
            
            # 发送加入消息
            join_msg = {"type": "join", "username": "test_user"}
            await websocket.send(json.dumps(join_msg))
            print(f"发送: {join_msg}")
            
            # 接收响应
            response = await websocket.recv()
            print(f"收到: {response}")
            
            # 保持连接一小段时间
            await asyncio.sleep(2)
            
            # 关闭连接
            await websocket.close()
            print("连接已关闭")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
