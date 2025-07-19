from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.services.db_service import get_db
from app.services.jwt_service import verify_token
from app.models.admin_user import AdminUser, UserRole

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(AdminUser).filter(AdminUser.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def require_admin(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_operator_or_admin(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """Require operator or admin role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator or admin access required"
        )
    return current_user