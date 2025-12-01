from pydantic import BaseModel, EmailStr
from typing import Optional
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