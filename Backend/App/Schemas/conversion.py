"""
conversion schema
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

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
    CreatedAt: datetime
    ServiceName: str
    Cost: Decimal
    
    class Config:
        from_attributes = True

class ConversionResponse(BaseModel):
    """Response after conversion (metadata only, file returned separately)"""
    success: bool
    message: str
    original_filename: str
    converted_filename: str
    file_size_bytes: bytes
    service_name: str
    created_at: datetime
    cost: Decimal
    conversion_history_id: Optional[int] = None