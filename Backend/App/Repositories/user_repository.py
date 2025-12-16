"""User repository"""
from datetime import datetime, timedelta
import secrets
import string
import jwt
import time

from sqlalchemy import desc, update
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from Database.connection import r 

from Schemas.user import UserData, UserPref
from Services.user_service import IUserService
from Entities.user import User
from Entities.user_otp import UserOTP
from Entities.user_preferences import UserPreferences
from config import settings
from Helpers.email_template import get_email_template
from Core.security import verify_password, hash_password


class UserRepository(IUserService):
    """User repository class"""

    def __init__(self, db: Session):
        self.db = db
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD.get_secret_value(),
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=int(settings.MAIL_PORT),
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fast_email = FastMail(self.conf)
        self.max_attempts = 5

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Create OTP code with 6 character length"""
        characters = string.digits

        otp = ''.join(secrets.choice(characters) for _ in range(length))
        return otp

    async def store_otp(self, user_id: int, otp_code: str) -> None:
        try:
            user_otp = self.db.query(UserOTP).filter(UserOTP.UserID == user_id).first()

            if not user_otp:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to query UserOTP"
                )

            expiry_time = datetime.utcnow() + timedelta(hours=1)

            user_otp.OTPCode = otp_code
            user_otp.OTPExpiry = expiry_time
            user_otp.OTPAttempts = user_otp.OTPAttempts + 1

            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store OTP: {str(e)}"
            ) from e

    async def get_user(self, user_id: int) -> UserData:
        try:
            user_data = self.db.query(User).filter(User.UserID == user_id).first()

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            return UserData(
                Email=user_data.Email or "",
                FirstName=user_data.FirstName or "",
                LastName=user_data.LastName or "",
                Address=user_data.Address or "",
                City=user_data.City or "",
                DateOfBirth=user_data.DateOfBirth,
                PhoneNumber=user_data.PhoneNumber or "",
                ProfilePictureURL=user_data.ProfilePictureURL or "",
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
                    detail="User preference not found!"
                )

            return UserPref(
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
            user = self.db.query(User).filter(User.Email == user_data.Email).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_data.Email} not found"
                )

            # Only update non-None fields
            update_data = user_data.model_dump(exclude_unset=True, exclude={'UserID'})

            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            self.db.commit()
            self.db.refresh(user)

            return UserData(
                Email=user.Email or "",
                FirstName=user.FirstName or "",
                LastName=user.LastName or "",
                Address=user.Address or "",
                City=user.City or "",
                DateOfBirth=user.DateOfBirth,
                PhoneNumber=user.PhoneNumber or "",
                ProfilePictureURL=user.ProfilePictureURL or "",
                MemberSince=user.MemberSince or datetime.utcnow(),
                LastLogin=user.LastLogin or datetime.utcnow()
            )

        except Exception as e:
            raise HTTPException (
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fail to update user data: {str(e)}"
            ) from e


    async def update_user_preferences(self, user_preferences: UserPref, user_id: int) -> UserPref:
        try:

            user_pref = self.db.query(UserPreferences).filter(UserPreferences.UserID==user_id).first()

            if not user_pref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )

            update_data = user_preferences.model_dump(exclude_unset=True, exclude={'UserID'})

            for field, value in update_data.items():
                if hasattr(user_pref, field):
                    setattr(user_pref, field, value)

            self.db.commit()
            self.db.refresh(user_pref)

            return UserPref(
                DefaultOutputFolder=user_pref.DefaultOutputFolder,
                Language=user_pref.Language,
                Theme=user_pref.Theme
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fail to update user data: {str(e)}"
            ) from e


    async def verify_email_user(self, email: str) -> bool:
        try:
            user = self.db.query(User).filter(User.Email == email).first()
            return user is not None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify email: {str(e)}"
            ) from e

    async def send_email(self, email: str, email_type: str, background_tasks: BackgroundTasks) -> dict:
        if self.verify_email_user(email):
            user = self.db.query(User).filter(User.Email == email).first()
            otp_code = self.generate_otp()

            # user = UserData.model_validate(user)
            try:
                if email_type == "forgot_password":
                    template_subject, template_body = get_email_template(email_type, user, otp_code)
                elif email_type == "welcome":
                    template_subject, template_body = get_email_template(email_type, user)
                else:
                    template_subject = "Notification"
                    template_body = "Notification message"

                message = MessageSchema(
                    subject=template_subject,
                    recipients=[email],
                    body=template_body,
                    subtype=MessageType.html
                )

                await self.store_otp(user.UserID, otp_code)

                background_tasks.add_task(self.fast_email.send_message, message)
                # await self.fast_email.send_message(message)

                return {
                    "success": True,
                    "message": f"Email sent successfully to {email}",
                    "email_type": email_type
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {str(e)}"
                ) from e
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{email} didn't exist"
            )

    async def verify_otp(self, email: str, otp_code: str) -> dict:
        """Verify OTP code"""
        try:
            user = self.db.query(User).options(
                joinedload(User.UserOTP)
            ).filter(User.Email == email).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if not user.UserOTP:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No OTP record found. Please request a new OTP."
                )

            if not user.UserOTP.OTPCode:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No OTP code found. Please request a new one."
                )

            if user.UserOTP.OTPAttempts > self.max_attempts:
                user.OTPCode = None
                user.OTPExpiry = None
                user.OTPPurpose = None
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed attempts. Please request a new OTP."
                )

            if user.UserOTP.OTPExpiry < datetime.utcnow():
                user.OTPCode = None
                user.OTPExpiry = None
                user.OTPPurpose = None
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP code has expired. Please request a new one."
                )

            if user.UserOTP.OTPCode != otp_code:
                user.UserOTP.OTPAttempts += 1
                self.db.commit()

                remaining_attempts = self.max_attempts - user.UserOTP.OTPAttempts
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid OTP code. {remaining_attempts} attempts remaining."
                )

            user.UserOTP.OTPCode = None
            user.UserOTP.OTPExpiry = None
            user.UserOTP.OTPAttempts = 0
            self.db.commit()

            return {
                "success": True,
                "message": "OTP verified successfully",
                "user_id": user.UserID,
                "email": user.Email
            }

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify OTP: {str(e)}"
            ) from e

    async def delete_user(self, user_id: int) -> None:
        """Delete user from database"""
        try:
            user_to_delete = self.db.query(User).filter(User.UserID == user_id).first()

            if not user_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to find the user with id: {user_id}"
                )

            self.db.delete(user_to_delete)
            self.db.commit()

            return None

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete user: {str(e)}") from e

    async def change_password(self, user_id: int, new_password: str) -> bool:
        """Change password"""
        user = self.db.query(User).filter(User.UserID == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can not find the user with id: {user_id}"
            )
        
        try:
            hashed_password = hash_password(new_password)
            user.HashedPassword = hashed_password
            self.db.commit()

            return True
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to change password: {str(e)}"
            ) from e
        
    async def logout(self, refresh_token: str) -> bool:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            jti = payload.get("jti")
            exp = payload.get("exp")

            current_time = time.time()
            ttl = exp - current_time

            if ttl > 0:
                r.setex(
                    name=f"blacklist:refresh:{jti}",
                    time=int(ttl),
                    value="revoked"
                )

            return {"message": "Logout successfully"}
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to log out {str(e)}"
            ) from e 
            