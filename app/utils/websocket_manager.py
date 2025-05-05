import json
from typing import Dict, List, Any
from fastapi import WebSocket

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
            await connection.send_text(message)

    async def broadcast_json(self, data: Dict[str, Any]):
        json_data = json.dumps(data)
        await self.broadcast(json_data)

    async def broadcast_log(self, log: Dict[str, Any]):
        await self.broadcast_json({
            "type": "log",
            "payload": log
        })

    async def broadcast_attack(self, attack: Dict[str, Any]):
        await self.broadcast_json({
            "type": "attack",
            "payload": attack
        })

    async def broadcast_resource_update(self, resource: Dict[str, Any]):
        await self.broadcast_json({
            "type": "resource_update",
            "payload": resource
        })
