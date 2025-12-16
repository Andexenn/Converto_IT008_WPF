"""
dependencies module
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt 
from sqlalchemy.orm import Session

from config import settings
from Database.connection import get_db
from Entities.user import User


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User :
    """
    Get the current user and authenticate that one

    Parameters:
    -----------
    credentials(HTTPAuthorizationCredentials): depend on security
    db(Session): depend on get_db
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") == "refresh":
            raise credentials_exception

        email: str | None = payload.get("sub")
        user_id: int | None = payload.get("user_id")

        if email is None or user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError as e:
        raise credentials_exception from e

    user = db.query(User).filter(User.UserID == user_id).first()
    if user is None:
        raise credentials_exception

    return user

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

