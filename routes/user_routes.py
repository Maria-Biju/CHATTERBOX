from fastapi import APIRouter, HTTPException
from models.user_models import UserRegister, UserLogin, UserResponse
from database import get_db
import hashlib

router = APIRouter()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    db = get_db()
    cursor = db.cursor()

    hashed = hash_password(user.password)

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, hashed)
        )
        db.commit()
        user_id = cursor.lastrowid
    except:
        raise HTTPException(status_code=400, detail="User already exists")

    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email
    )


@router.post("/login")
def login(user: UserLogin):
    db = get_db()
    cursor = db.cursor()

    hashed = hash_password(user.password)

    cursor.execute(
        "SELECT id, username, email FROM users WHERE username=? AND password_hash=?",
        (user.username, hashed)
    )

    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user": {
            "id": result[0],
            "username": result[1],
            "email": result[2]
        }
    }
