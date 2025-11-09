from sqlalchemy.orm import Session 
from sqlalchemy.exc import IntegrityError
from typing import Optional 
from fastapi import HTTPException, status 

from Services.UserServices.auth_service import IAuthService
from Schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse
from Entities.user import User 
from Entities.wallet import Wallet
from Core.security import hash_password, verify_password, create_access_token


class AuthRepository(IAuthService):
    def __init__(self, db: Session):
        self.db = db 

    async def sign_up(self, user_data: UserCreate) -> UserResponse:
        try:
            if await self.user_exists(user_data.Email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            hashed_password = hash_password(user_data.Password)

            new_user = User(
                Email = user_data.Email,
                FirstName = user_data.FirstName,
                LastName = user_data.LastName,
                PhoneNumber = user_data.PhoneNumber,
                Address = user_data.Address,
                City = user_data.City,
                DateOfBirth = user_data.DateOfBirth,
                HashedPassword = hashed_password)
            
            self.db.add(new_user)
            self.db.flush()

            new_wallet = Wallet(
                UserID = new_user.UserID,
                Balance = 0.00,
                CurrencyCode = "USD"
            )

            self.db.add(new_wallet)
            self.db.commit()
            self.db.refresh(new_user)

            return UserResponse.model_validate(new_user)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "User registration failed. Email might already exist."
            )
        except HTTPException:
            self.db.rollback()
            raise 
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during registration: {str(e)}"
            )
        
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = self.db.query(User).filter(User.Email == email).first()
        if(user):
            return UserResponse.model_validate(user)
        return None

    async def user_exists(self, email: str) -> bool:
        user = self.db.query(User).filter(User.Email == email).first()
        return user is not None
    
    async def login(self, user_data: UserLogin) -> UserResponse:
        try:
            hashed_password = hash_password(user_data.Password)
            user = self.db.query(User).filter(User.Email == user_data.Email and verify_password(user_data.Password, User.HashedPassword)).first()
            user_login_response = UserLoginResponse.model_validate(user)
            return user_login_response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An  error occured during login: {e}"
            )
        


