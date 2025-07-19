from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.services.db_service import get_db
from app.models.admin_user import AdminUser, UserRole
from app.models.telemetry import AuditLog
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.middleware.auth import get_current_user, require_admin
from app.services.jwt_service import get_password_hash
from app.utils.logging import log_audit

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_admin)
):
    """Get all users (admin only)"""
    users = db.query(AdminUser).offset(skip).limit(limit).all()
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    existing_user = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    
    user = AdminUser(**user_dict)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log the action
    await log_audit(db, current_user.id, "CREATE_USER", str(user.id), f"Created user {user.email}")
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_admin)
):
    """Update a user (admin only)"""
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log the action
    await log_audit(db, current_user.id, "UPDATE_USER", str(user.id), f"Updated user {user.email}")
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_admin)
):
    """Delete a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    db.delete(user)
    db.commit()
    
    # Log the action
    await log_audit(db, current_user.id, "DELETE_USER", str(user_id), f"Deleted user {user_email}")
    
    return {"message": "User deleted successfully"}

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get audit logs"""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Get admin dashboard statistics"""
    from app.models.device import Device
    from app.models.telemetry import Telemetry, Anomaly
    from datetime import datetime, timedelta
    
    # Device counts by status
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    offline_devices = db.query(Device).filter(Device.status == "offline").count()
    warning_devices = db.query(Device).filter(Device.status == "warning").count()
    
    # Recent telemetry count (last 24 hours)
    since_24h = datetime.utcnow() - timedelta(hours=24)
    recent_telemetry = db.query(Telemetry).filter(Telemetry.timestamp >= since_24h).count()
    
    # Unresolved anomalies
    unresolved_anomalies = db.query(Anomaly).filter(Anomaly.resolved == "false").count()
    
    return {
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": offline_devices,
            "warning": warning_devices
        },
        "telemetry_24h": recent_telemetry,
        "unresolved_anomalies": unresolved_anomalies
    }