"""Task schema"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class TaskBase(BaseModel):
    UserID: int
    ServiceTypeID: int
    OriginalFileName: str
    OriginalFileSize: int
    OriginalFilePath: str
    OutputFileName: Optional[str] = None
    OutputFileSize: Optional[int] = None
    OutputFilePath: Optional[str] = None
    TaskStatus: bool
    TaskTime: float

class TaskConversion(TaskBase):
    InputFormat: str
    OutputFormat: str

class TaskCompression(TaskBase):
    CompressionLevel: Optional[str] = None

class TaskRemoveBackground(TaskBase):
    pass

class TaskByUserID(BaseModel):
    ServiceTypeID: int 
    OriginalFileSize: int 
    OriginalFilePath: str 
    OutputFileSize: Optional[int] = None 
    OutputFilePath: Optional[str] = None 
    TaskStatus: bool 
    TaskTime: float 
    CreatedAt: datetime



