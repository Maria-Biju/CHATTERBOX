from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.websocket_routes import router as websocket_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(user_router)
app.include_router(websocket_router)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def home():
    return {"message": "Chat server running"}
