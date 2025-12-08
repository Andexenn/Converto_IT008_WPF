from pydantic import BaseModel 
from decimal import Decimal

class ServiceBase(BaseModel):
    InputFormat: str 
    OutputFormat: str 
    ServiceName: str 
    Price: Decimal

class ServiceCreate(ServiceBase):
    pass 

class ServiceResponse(ServiceBase):
    ServiceID: int 

    class Config:
        from_attributes = True

class ThirdPartyRequest(BaseModel):
    code: str 

