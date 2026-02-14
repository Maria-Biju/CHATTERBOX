from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List

router = APIRouter()

active_connections: List[WebSocket] = []

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # send message to all connected users
            for connection in active_connections:
                await connection.send_text(data)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
