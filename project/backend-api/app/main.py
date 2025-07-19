from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import auth, admin, devices, telemetry, websocket
from app.services.db_service import init_db
from app.utils.logging import setup_logging

load_dotenv()

app = FastAPI(
    title="VigilanceOS API",
    description="Real-time device monitoring and anomaly detection platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and logging on startup"""
    setup_logging()
    await init_db()

@app.get("/")
async def root():
    return {"message": "VigilanceOS API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vigilance-api"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )