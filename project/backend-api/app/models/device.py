from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class DeviceStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    threshold_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())