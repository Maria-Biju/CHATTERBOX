from fastapi import APIRouter, HTTPException
import sqlite3, hashlib, uuid
from models.user_models import UserRegister, UserLogin, UserResponse
from typing import List
from models.user_models import UserResponse
router = APIRouter()
sessions = {}  # token -> username

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    hashed = hash_password(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

    return UserResponse(id=user_id, username=user.username, email=user.email)

@router.post("/login")
def login(user: UserLogin):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    hashed = hash_password(user.password)

    cursor.execute(
        "SELECT username FROM users WHERE username = ? AND password_hash = ?",
        (user.username, hashed)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid.uuid4())
    sessions[token] = user.username

    return {"token": token, "username": user.username}
@router.get("/users", response_model=List[UserResponse])
def list_users():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    rows = cursor.fetchall()
    conn.close()

    return [
        UserResponse(id=row[0], username=row[1], email=row[2])
        for row in rows
    ]