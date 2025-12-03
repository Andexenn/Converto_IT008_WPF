"""User handler"""

from typing import List

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from Database.connection import get_db
from Core.dependencies import get_current_user
from Repositories.user_repository import UserRepository
from Services.user_service import IUserService
from Schemas.user import UserData, UserPref
from Entities.user import User

router = APIRouter()

@router.get('/user/get_user_data', response_model=UserData)
async def get_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserData:
    """..."""

    user_serivce: IUserService = UserRepository(db)
    return await user_serivce.get_user(current_user.UserID)

@router.get('/user/get_user_preference', response_model=UserPref)
async def get_user_preference(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserPref:
    """..."""

    user_serivce: IUserService = UserRepository(db)
    return await user_serivce.get_user_preference(current_user.UserID)

@router.post('/user/update_user_data', response_model=UserData)
async def update_user_data(
    updated_user: UserData = Body(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
) -> UserData:
    
    user_serivce: IUserService = UserRepository(db)
    return await user_serivce.update_user_data(updated_user)

@router.post('/user/update_user_pref', response_model=UserPref)
async def update_user_pref(
    updated_user_pref: UserPref = Body(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
) -> UserPref:
    
    user_service: IUserService = UserRepository(db)
    return await user_service.update_user_preferences(updated_user_pref)

@router.get('/user/verify_email', response_model=dict)
async def verify_email(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    
    user_service: IUserService = UserRepository(db)
    if await user_service.verify_email_user(current_user.Email):
        return {
            "success": True,
            "message": "Email exists"
        }
    else:
        return {
            "success": False,
            "message": "Email didn't exist"
        }

@router.get('/user/send_email/{email_type}', response_model=dict)
async def send_email(
    email_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:

    user_service: IUserService = UserRepository(db)
    return await user_service.send_email(current_user.Email, email_type)

@router.get('/user/verify_otp/{otp_code}', response_model=dict)
async def verify_otp(
    otp_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    
    user_service: IUserService = UserRepository(db)
    return await user_service.verify_otp(current_user.Email, otp_code)