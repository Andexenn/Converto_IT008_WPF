from pydantic import BaseModel
from decimal import Decimal 

class WalletBase(BaseModel):
    CurrencyCode: str = "USD"

class WalletCreate(WalletBase):
    UserID: int 

class WalletResponse(WalletBase):
    WalletID: int 
    UserID: int 
    Balance: Decimal 

    class Config:
        from_attributes = True



