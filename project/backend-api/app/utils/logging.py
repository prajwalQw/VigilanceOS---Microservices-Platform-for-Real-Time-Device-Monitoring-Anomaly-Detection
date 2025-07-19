import logging
from sqlalchemy.orm import Session
from app.models.telemetry import AuditLog

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vigilance.log'),
            logging.StreamHandler()
        ]
    )

async def log_audit(db: Session, admin_id: int, action: str, target_id: str = None, details: str = None):
    """Log an audit event"""
    try:
        audit_log = AuditLog(
            admin_id=admin_id,
            action=action,
            target_id=target_id,
            details=details
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to log audit event: {e}")