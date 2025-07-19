from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.db_service import get_db
from app.models.device import Device
from app.schemas.telemetry import DeviceCreate, DeviceUpdate, DeviceResponse
from app.middleware.auth import get_current_user
from app.models.admin_user import AdminUser
from app.utils.logging import log_audit

router = APIRouter()

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get all devices with optional filtering"""
    query = db.query(Device)
    
    if status:
        query = query.filter(Device.status == status)
    
    devices = query.offset(skip).limit(limit).all()
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get a specific device by ID"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device

@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Create a new device"""
    # Check if device already exists
    existing_device = db.query(Device).filter(Device.device_id == device_data.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    device = Device(**device_data.dict())
    db.add(device)
    db.commit()
    db.refresh(device)
    
    # Log the action
    await log_audit(db, current_user.id, "CREATE_DEVICE", device.device_id, f"Created device {device.name}")
    
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Update a device"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update only provided fields
    update_data = device_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    db.commit()
    db.refresh(device)
    
    # Log the action
    await log_audit(db, current_user.id, "UPDATE_DEVICE", device.device_id, f"Updated device {device.name}")
    
    return device

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Delete a device"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    device_name = device.name
    db.delete(device)
    db.commit()
    
    # Log the action
    await log_audit(db, current_user.id, "DELETE_DEVICE", device_id, f"Deleted device {device_name}")
    
    return {"message": "Device deleted successfully"}