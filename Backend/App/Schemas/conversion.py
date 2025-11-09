from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ConversionHistoryBase(BaseModel):
    UserID: int
    ServiceID: int

class ConversionHistoryResponse(ConversionHistoryBase):
    ConversionHistoryID: int
    CreatedAt: datetime
    
    class Config:
        from_attributes = True

class ConversionHistoryWithServiceResponse(BaseModel):
    """Conversion history with service details"""
    ConversionHistoryID: int
    UserID: int
    ServiceID: int
    CreatedAt: datetime
    ServiceName: str
    InputFormat: str
    OutputFormat: str
    Cost: Decimal
    
    class Config:
        from_attributes = True

class ConversionResponse(BaseModel):
    """Response after conversion (metadata only, file returned separately)"""
    success: bool
    message: str
    original_filename: str
    converted_filename: str
    file_size_bytes: int
    service_name: str
    created_at: datetime
    cost: Decimal
    conversion_history_id: Optional[int] = None