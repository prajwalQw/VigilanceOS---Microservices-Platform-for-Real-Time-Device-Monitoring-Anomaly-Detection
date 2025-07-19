from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TelemetryBase(BaseModel):
    device_id: str
    temperature: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryResponse(TelemetryBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    name: str
    device_id: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class DeviceCreate(DeviceBase):
    threshold_config: Optional[dict] = None

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    threshold_config: Optional[dict] = None

class DeviceResponse(DeviceBase):
    id: int
    status: str
    last_seen: Optional[datetime] = None
    threshold_config: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnomalyResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    anomaly_type: str
    reason: Optional[str] = None
    severity: str
    resolved: str
    
    class Config:
        from_attributes = True