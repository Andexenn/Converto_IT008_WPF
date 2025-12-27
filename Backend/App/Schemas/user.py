"""User"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    Email: EmailStr
    FirstName: str
    LastName: str
    Address: Optional[str] = None
    PhoneNumber: Optional[str] = None
    City: Optional[str] = None
    DateOfBirth: Optional[datetime] = None

class UserCreate(UserBase):
    Password: str

class UserUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Address: Optional[str] = None
    PhoneNumber: Optional[str] = None
    City: Optional[str] = None
    DateOfBirth: Optional[datetime] = None
    Password: Optional[str] = None

class UserResponse(UserBase):
    UserID: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    Email: EmailStr
    Password: str

    class Config:
        from_attributes = True

class UserLoginResponse(BaseModel):
    Email: EmailStr
    FirstName: str
    LastName: str
    Address: Optional[str] = None
    PhoneNumber: Optional[str] = None
    City: Optional[str] = None
    DateOfBirth: Optional[datetime] = None
    ProfilePictureURL: Optional[str] = None 
    MemberSince: Optional[datetime] = None 
    LastLogin: Optional[datetime] = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

class GoogleUserData(BaseModel):
    email: EmailStr
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    id_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserLoginResponse

    model_config = ConfigDict(from_attributes=True)

class UserData(BaseModel):
    Email: Optional[EmailStr] = None 
    FirstName: Optional[str] = None 
    LastName: Optional[str] = None 
    Address: Optional[str] = None
    PhoneNumber: Optional[str] = None
    City: Optional[str] = None
    DateOfBirth: Optional[datetime] = None
    ProfilePictureURL: Optional[str] = None
    MemberSince: Optional[datetime] = None 
    LastLogin: Optional[datetime] = None 

class UserPref(BaseModel):
    DefaultOutputFolder: Optional[str] = None 
    Language: Optional[str] = None 
    Theme: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)