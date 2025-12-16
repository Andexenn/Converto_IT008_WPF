"""
Authentication handler module
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from Database.connection import get_db
from Repositories.auth_repository import AuthRepository
from Services.auth_service import IAuthService
from Schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse, GoogleUserData
from Schemas.service import ThirdPartyRequest

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
    Mount a function to a check email exist endpoint
    """
    auth_service: IAuthService = AuthRepository(db)
    exists = await auth_service.user_exists(email)
    return {"exists": exists, "email": email}

@router.get("/user/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)) -> UserResponse:
    """
    Mount a function to get information of the user
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
    Mount a fucntion to login 
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.login(user_data)

@router.post("/google_login", response_model=dict)
async def google_login(
    google_data: GoogleUserData,
    db: Session = Depends(get_db)
)->dict[str, str | UserLoginResponse]:
    """
    Mount a function to google login
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.google_auth(google_data)

@router.post("/github_login", response_model=dict)
async def github_login(
    code: ThirdPartyRequest = Body(),
    db: Session = Depends(get_db)
)->dict[str, str | UserLoginResponse]:
    """
    Mount a function to github login
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.github_auth(code.code)

@router.post("/refresh_access_token", response_model=dict)
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Mount a function to github login
    """
    auth_service: IAuthService = AuthRepository(db)
    return await auth_service.refresh_access_token(refresh_token)
