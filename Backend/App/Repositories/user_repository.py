"""User repository"""
from typing import List
from datetime import datetime

from sqlalchemy import desc, update
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from Schemas.user import UserData, UserPref
from Services.user_service import IUserService
from Entities.user import User
from Entities.user_preferences import UserPreferences

class UserRepository(IUserService):
    """User repository class"""

    def __init__(self, db: Session):
        self.db = db

    async def get_user(self, user_id: int) -> UserData:
        try:
            user_data = self.db.query(User).filter(User.UserID == user_id).first()
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            return UserData(
                UserID=user_data.UserID,
                Email=user_data.Email or "",
                FirstName=user_data.FirstName or "",
                LastName=user_data.LastName or "",
                Address=user_data.Address or "",
                City=user_data.City or "",
                DateOfBirth=user_data.DateOfBirth,
                PhoneNumber=user_data.PhoneNumber or "",
                ProfilePictureUrl=user_data.ProfilePictureURL or "",
                MemberSince=user_data.MemberSince or datetime.utcnow(),
                LastLogin=user_data.LastLogin or datetime.utcnow()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user data: {str(e)}"
            ) from  e
        

    async def get_user_preference(self, user_id: int) -> UserPref:
        try:
            user_preference = self.db.query(UserPreferences).filter(UserPreferences.UserID == user_id).first()
            if not user_preference:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User preference not found!: {str(e)}"
                )
            
            return UserPref(
                UserID=user_id,
                DefaultOutputFolder=user_preference.DefaultOutputFolder,
                Language=user_preference.Language,
                Theme=user_preference.Theme
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User preferences not found!: {str(e)}"
            ) from e 
        
    async def update_user_data(self, user_data: UserData) -> UserData:
        try:
            user = self.db.query(User).filter(User.UserID == user_data.UserID).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_data.UserID} not found"
                )
            
            # Only update non-None fields
            update_data = user_data.model_dump(exclude_unset=True, exclude={'UserID'})
            
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            return UserData(
                UserID=user.UserID,
                Email=user.Email or "",
                FirstName=user.FirstName or "",
                LastName=user.LastName or "",
                Address=user.Address or "",
                City=user.City or "",
                DateOfBirth=user.DateOfBirth,
                PhoneNumber=user.PhoneNumber or "",
                ProfilePictureUrl=user.ProfilePictureURL or "",
                MemberSince=user.MemberSince or datetime.utcnow(),
                LastLogin=user.LastLogin or datetime.utcnow()
            )
           
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fail to update user data: {str(e)}"
            ) from e 
        

    async def update_user_preferences(self, user_preferences: UserPref) -> UserPref:
        try:

            user_pref = self.db.query(UserPreferences).filter(UserPreferences.UserID==user_preferences.UserID).first()

            if not user_pref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_preferences.UserID} not found"
                )
            
            update_data = user_preferences.model_dump(exclude_unset=True, exclude={'UserID'})

            for field, value in update_data.items():
                if hasattr(user_pref, field):
                    setattr(user_pref, field, value)

            self.db.commit()
            self.db.refresh(user_pref)

            return UserPref(
                UserID=user_pref.UserID,
                DefaultOutputFolder=user_pref.DefaultOutputFolder,
                Language=user_pref.Language,
                Theme=user_pref.Theme
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fail to update user data: {str(e)}"
            ) from e 
