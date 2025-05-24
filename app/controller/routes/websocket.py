from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.utils.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
