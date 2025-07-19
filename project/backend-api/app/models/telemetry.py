from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    temperature = Column(Float, nullable=True)
    battery = Column(Float, nullable=True)
    signal_strength = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    anomaly_type = Column(String(50), nullable=False)
    reason = Column(String(500), nullable=True)
    severity = Column(String(20), default="medium")
    resolved = Column(String(10), default="false")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    target_id = Column(String(50), nullable=True)
    details = Column(String(500), nullable=True)