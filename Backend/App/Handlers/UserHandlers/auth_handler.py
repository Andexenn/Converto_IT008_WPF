from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session 

from Database.connection import get_db
from Repositories.UserRepositories.auth_repository import AuthRepository
from Schemas.user import UserCreate, UserResponse


router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_repo = AuthRepository(db)
    return await auth_repo.sign_up(user_data)

@router.get("/check-email/{email}")
async def check_email_exists(email: str, db: Session = Depends(get_db)):
    """
    Check if an email is already registered
    
    Useful for frontend validation before signup
    """
    auth_repo = AuthRepository(db)
    exists = await auth_repo.user_exists(email)
    return {"exists": exists, "email": email}


@router.get("/user/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Get user information by email
    """
    auth_repo = AuthRepository(db)
    user = await auth_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


