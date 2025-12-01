from typing import Optional
from datetime import timedelta
import httpx

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from Services.auth_service import IAuthService
from Schemas.user import GoogleUserData, UserCreate, UserResponse, UserLogin, UserLoginResponse
from Entities.user import User
from Core.security import hash_password, verify_password, create_access_token
from config import settings

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

            self.db.commit()
            self.db.refresh(new_user)

            return UserResponse.model_validate(new_user)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "User registration failed. Email might already exist."
            ) from e
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during registration: {str(e)}"
            ) from e

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = self.db.query(User).filter(User.Email == email).first()
        if(user):
            return UserResponse.model_validate(user)
        return None

    async def user_exists(self, email: str) -> bool:
        user = self.db.query(User).filter(User.Email == email).first()
        return user is not None

    async def login(self, user_data: UserLogin) -> dict[str, str | UserLoginResponse]:
        try:
            user = self.db.query(User).filter(User.Email == user_data.Email).first()

            if not user or not verify_password(user_data.Password, user.HashedPassword):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.Email,      # "sub" = subject (standard JWT claim)
                    "user_id": user.UserID, # Custom claim
                    "email": user.Email     # Custom claim
                },
                expires_delta=access_token_expires
            )

            return{
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserLoginResponse.model_validate(user)
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An  error occured during login: {str(e)}"
            ) from e

    async def google_auth(self, google_data: GoogleUserData) -> dict[str, str | UserLoginResponse]:
        try:
            if google_data.id_token:
                user_info = await self._verify_google_token(google_data.id_token)
            else:
                user_info = {
                    "email": google_data.email,
                    "given_name": google_data.given_name,
                    "family_name": google_data.family_name,
                    "picture": google_data.picture
                }

            return await self._process_google_user(user_info)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google authentication failed: {str(e)}"
            ) from e

    async def _verify_google_token(self, id_token: str) -> dict:
        try:
            token_info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            async with httpx.AsyncClient() as client:
                response = await client.get(token_info_url)
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google ID token"
                    )

                token_info = response.json()

                if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token was not issued for this application"
                    )

                return {
                    "email": token_info.get("email"),
                    "given_name": token_info.get("given_name"),
                    "family_name": token_info.get("family_name"),
                    "picture": token_info.get("picture")
                }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            ) from e

    async def _process_google_user(self, user_info: dict) -> dict[str, str | UserLoginResponse]:
        """
        Create new user or login existing user from Google Data
        """

        try:
            email = user_info.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )

            user = self.db.query(User).filter(User.Email == email).first()

            if not user:
                user = User(
                    Email=email,
                    FirstName=user_info.get("given_name"),
                    LastName=user_info.get("family_name"),
                    PhoneNumber=None,
                    Address=None,
                    City=None,
                    DateOfBirth=None,
                    HashedPassword=hash_password(f"google_oauth_{email}")
                )

                self.db.add(user)
                self.db.flush()

                self.db.commit()
                self.db.refresh(user)

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.Email,
                    "user_id": user.UserID,
                    "email": user.Email
                },
                expires_delta=access_token_expires
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserLoginResponse.model_validate(user)
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process Google login: {str(e)}"
            ) from e
