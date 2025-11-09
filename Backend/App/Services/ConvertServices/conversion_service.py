from abc import ABC, abstractmethod
from typing import Optional, List
from Schemas.conversion_history import ConversionHistoryCreate, ConversionHistoryResponse

class IConversionService(ABC):

    @abstractmethod
    async def create_conversion_history(self, user_id: int, service_id: int) -> ConversionHistoryResponse:
        pass 

    @abstractmethod
    async def get_user_conversion_history(self, user_id: int, limit: int = 50) -> List[ConversionHistoryResponse]:
        pass

    @abstractmethod
    async def get_or_create_service(self, input_format: str, output_format: str) -> int:
        pass 
    

