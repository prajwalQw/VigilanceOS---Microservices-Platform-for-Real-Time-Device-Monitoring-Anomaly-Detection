from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.db_service import get_db
from app.models.telemetry import Telemetry, Anomaly
from app.models.device import Device, DeviceStatus
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse, AnomalyResponse
from app.services.anomaly_forwarder import check_anomaly
from app.routes.websocket import broadcast_telemetry

router = APIRouter()

@router.post("/", response_model=TelemetryResponse)
async def submit_telemetry(
    telemetry_data: TelemetryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit telemetry data from a device"""
    # Check if device exists
    device = db.query(Device).filter(Device.device_id == telemetry_data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Create telemetry record
    telemetry = Telemetry(**telemetry_data.dict())
    db.add(telemetry)
    
    # Update device status and last seen
    device.status = DeviceStatus.ONLINE
    device.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(telemetry)
    
    # Broadcast to WebSocket clients
    await broadcast_telemetry(telemetry_data.dict())
    
    # Check for anomalies in background
    background_tasks.add_task(check_anomaly, telemetry_data.dict(), db)
    
    return telemetry

@router.get("/", response_model=List[TelemetryResponse])
async def get_telemetry(
    device_id: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # Last 24 hours by default, max 1 week
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get telemetry data with optional filtering"""
    query = db.query(Telemetry)
    
    # Filter by device if specified
    if device_id:
        query = query.filter(Telemetry.device_id == device_id)
    
    # Filter by time range
    since = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(Telemetry.timestamp >= since)
    
    # Order by timestamp descending
    query = query.order_by(Telemetry.timestamp.desc())
    
    telemetry_data = query.offset(skip).limit(limit).all()
    return telemetry_data

@router.get("/latest/{device_id}", response_model=TelemetryResponse)
async def get_latest_telemetry(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Get the latest telemetry data for a specific device"""
    telemetry = db.query(Telemetry).filter(
        Telemetry.device_id == device_id
    ).order_by(Telemetry.timestamp.desc()).first()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No telemetry data found for this device"
        )
    
    return telemetry

@router.get("/anomalies/", response_model=List[AnomalyResponse])
async def get_anomalies(
    device_id: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get anomalies with optional filtering"""
    query = db.query(Anomaly)
    
    if device_id:
        query = query.filter(Anomaly.device_id == device_id)
    
    if resolved is not None:
        resolved_str = "true" if resolved else "false"
        query = query.filter(Anomaly.resolved == resolved_str)
    
    # Filter by time range
    since = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(Anomaly.timestamp >= since)
    
    # Order by timestamp descending
    query = query.order_by(Anomaly.timestamp.desc())
    
    anomalies = query.offset(skip).limit(limit).all()
    return anomalies

@router.put("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db)
):
    """Mark an anomaly as resolved"""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomaly not found"
        )
    
    anomaly.resolved = "true"
    db.commit()
    
    return {"message": "Anomaly marked as resolved"}