"""Service schema"""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class ServiceBase(BaseModel):
    InputFormat: str
    OutputFormat: str
    ServiceName: str
    Price: Decimal

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    ServiceID: int

    model_config = ConfigDict(from_attributes=True)

class ThirdPartyRequest(BaseModel):
    code: str
