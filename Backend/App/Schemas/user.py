from pydantic import BaseModel, EmailStr 
from typing import Optional
from datetime import datetime 

class UserBase(BaseModel):
    Email: EmailStr 
    FirstName: Optional[str] = None 
    LastName: Optional[str] = None 
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

class UserResponse(UserBase):
    UserID: int 

    class Config:
        from_attributes = True
