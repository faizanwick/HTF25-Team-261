from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            if message_data.get("type") == "voice_command":
                # Simulate voice command processing
                command = message_data.get("command", "")
                response = {
                    "type": "voice_response",
                    "command": command,
                    "response": f"Processed: {command}",
                    "code_generated": "def example():\n    pass" if "function" in command.lower() else None
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                
            elif message_data.get("type") == "ping":
                # Respond to ping with pong
                pong_response = {"type": "pong", "timestamp": message_data.get("timestamp")}
                await manager.send_personal_message(json.dumps(pong_response), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
