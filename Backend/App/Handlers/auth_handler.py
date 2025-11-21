"""
Authentication handler module
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Database.connection import get_db
from Repositories.auth_repository import AuthRepository
from Services.auth_service import IAuthService
from Schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Sign up request handler
    
    Parameter:
    ----------
    - user_data (UserCreate): ...
    - db (Session): ...

    Return:
    -------
    UserResponse ...
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.sign_up(user_data)

@router.get("/check-email/{email}")
async def check_email_exists(email: str, db: Session = Depends(get_db)) -> dict[str, bool | str]:
    """
    ...
    """
    auth_service: IAuthService = AuthRepository(db)
    exists = await auth_service.user_exists(email)
    return {"exists": exists, "email": email}

@router.get("/user/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)) -> UserResponse:
    """
    ...
    """
    auth_service: IAuthService = AuthRepository(db)
    user = await auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/login", response_model=dict)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> dict[str, str | UserLoginResponse]:
    """
    ...
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.login(user_data)
