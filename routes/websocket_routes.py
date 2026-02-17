from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import sqlite3
from routes.user_routes import sessions

router = APIRouter()
online_users = set()

# Simple toxicity list;
TOXIC_WORDS = {
    "fuck", "shit", "bitch", "noob",
    "idiot", "stupid", "dumb"
}

def is_toxic(text: str) -> bool:
    t = text.lower()
    return any(bad in t for bad in TOXIC_WORDS)


class Manager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket, username: str):
        await ws.accept()
        self.connections.append(ws)
        online_users.add(username)
        await self.broadcast_users()

    async def disconnect(self, ws: WebSocket, username: str):
        if ws in self.connections:
            self.connections.remove(ws)
        online_users.discard(username)
        # update all clients when someone leaves
        await self.broadcast_users()

    async def broadcast(self, data: dict):
        # send to all active connections, drop broken ones
        for c in list(self.connections):
            try:
                await c.send_json(data)
            except Exception:
                if c in self.connections:
                    self.connections.remove(c)

    async def broadcast_users(self):
        await self.broadcast({
            "type": "users",
            "users": list(online_users)
        })


manager = Manager()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    if token not in sessions:
        await ws.close()
        return

    username = sessions[token]
    await manager.connect(ws, username)

    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    # send history with seen flag
    cursor.execute("SELECT id, username, message, timestamp, seen FROM messages")
    for row in cursor.fetchall():
        await ws.send_json({
            "type": "message",
            "id": row[0],
            "user": row[1],
            "text": row[2],
            "time": row[3],
            "seen": bool(row[4])
        })

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")  # SAFE access

            if msg_type == "send":
                text = data.get("text", "").strip()
                if not text:
                    continue

                # TOXICITY CHECK: block and DO NOT save/broadcast
                if is_toxic(text):
                    await ws.send_json({
                        "type": "error",
                        "message": "Message blocked due to toxic content"
                    })
                    continue

                time = datetime.now().strftime("%H:%M")
                cursor.execute(
                    "INSERT INTO messages(username, message, timestamp) VALUES (?, ?, ?)",
                    (username, text, time)
                )
                conn.commit()
                msg_id = cursor.lastrowid

                await manager.broadcast({
                    "type": "message",
                    "id": msg_id,
                    "user": username,
                    "text": text,
                    "time": time,
                    "seen": False  # green single tick on frontend
                })

            elif msg_type == "delete":
                cursor.execute("DELETE FROM messages WHERE id=?", (data["id"],))
                conn.commit()
                await manager.broadcast({"type": "delete", "id": data["id"]})

            elif msg_type == "edit":
                cursor.execute(
                    "UPDATE messages SET message=? WHERE id=?",
                    (data["text"], data["id"])
                )
                conn.commit()
                await manager.broadcast({
                    "type": "edit",
                    "id": data["id"],
                    "text": data["text"]
                })

            else:
                # ignore unknown / malformed payloads
                continue

    except WebSocketDisconnect:
        await manager.disconnect(ws, username)
        conn.close()
