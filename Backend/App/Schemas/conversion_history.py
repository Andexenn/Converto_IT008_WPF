from pydantic import BaseModel
from typing import Optional 
from datetime import datetime 
from decimal import Decimal 

class ConversionHistoryBase(BaseModel):
    UserID: int 
    ServiceID: int 

class ConversionHistoryCreate(ConversionHistoryBase):
    pass 

class ConversionHistoryResponse(ConversionHistoryBase):
    ConversionHistoryID: int 
    CreatedAt: datetime

    class Config:
        from_attributes: True

class ConversionRequest(BaseModel):
    input_format: str 
    output_format: str 

class ConversionResponse(BaseModel):
    success: bool 
    message: str 
    original_filename: str 
    converted_filename: str 
    file_size_bytes: int 
    service_name: str 
    CreateAt: datetime
    Cost: Decimal
    conversion_history_id: Optional[int] = None 

    

