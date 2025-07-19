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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(f"Heartbeat: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def broadcast_telemetry(telemetry_data: dict):
    """Broadcast telemetry data to all connected WebSocket clients"""
    message = json.dumps({
        "type": "telemetry",
        "data": telemetry_data
    })
    await manager.broadcast(message)

async def broadcast_anomaly(anomaly_data: dict):
    """Broadcast anomaly alert to all connected WebSocket clients"""
    message = json.dumps({
        "type": "anomaly",
        "data": anomaly_data
    })
    await manager.broadcast(message)

async def broadcast_device_status(device_data: dict):
    """Broadcast device status change to all connected WebSocket clients"""
    message = json.dumps({
        "type": "device_status",
        "data": device_data
    })
    await manager.broadcast(message)