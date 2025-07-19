from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:secret@localhost:5432/telemetry"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    from app.models.admin_user import AdminUser
    from app.models.device import Device
    from app.models.telemetry import Telemetry, Anomaly, AuditLog
    
    # Import all models to ensure they're registered
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin_exists = db.query(AdminUser).filter(AdminUser.email == "admin@vigilance.com").first()
        if not admin_exists:
            from app.services.jwt_service import get_password_hash
            from app.models.admin_user import UserRole
            
            default_admin = AdminUser(
                name="System Administrator",
                email="admin@vigilance.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(default_admin)
            db.commit()
            print("Default admin user created: admin@vigilance.com / admin123")
    finally:
        db.close()