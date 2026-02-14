# CHATTERBOX
A realtime websocket based chat application
# ChatterBox 💬

ChatterBox is a real-time WebSocket chat application built with FastAPI and SQLite.  
It supports user registration and login, authenticated WebSocket chat with message history, basic toxicity filtering, message editing and deletion, and an admin dashboard to inspect users and online presence.

---

## Features

- FastAPI backend with async WebSocket endpoint.
- SQLite database for users and chat messages.
- User registration and login with password hashing.
- Token-based session for WebSocket authentication.
- Real-time broadcast to all connected clients.
- Message history loaded on connect.
- WhatsApp-style chat UI:
  - Username and timestamp per message.
  - Green tick indicator for sent messages.
  - Edit and delete options for your own messages.
- Basic toxicity detection:
  - Blocks messages containing configured toxic words.
  - Shows an error to the sender and does not broadcast or store the message.
- Admin dashboard:
  - List of all registered users.
  - Live view of currently online users via WebSocket.

---

## Tech Stack

- **Backend:** FastAPI, WebSockets, SQLite (`sqlite3`)
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Auth:** Simple token-based session (in-memory)

---

## Project Structure

```text
chatterbox/
├── main.py
├── chat.db
├── models/
│   ├── __init__.py
│   └── user_models.py
├── routes/
│   ├── __init__.py
│   ├── user_routes.py
│   ├── websocket_routes.py
│   └── chat_routes.py   # (optional / legacy)
└── frontend/
    ├── login.html
    ├── register.html
    ├── chat.html
    ├── admin.html
    └── style.css
