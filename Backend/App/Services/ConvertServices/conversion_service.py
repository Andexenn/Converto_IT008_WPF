from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from Schemas.conversion import ConversionResponse
from Entities.conversion_history import ConversionHistory
from Entities.service import Service

class IConversionService(ABC):
    """Interface for conversion history management (shared across all converters)"""
    
    @abstractmethod
    async def get_or_create_service(
        self, 
        input_format: str, 
        output_format: str
    ) -> Service:
        pass

    @abstractmethod
    async def record_conversion(
        self,
        user_id: int,
        input_format: str,
        output_format: str,
        original_filename: str,
        converted_filename: str,
        file_size_bytes: int,
        converted_file_bytes: bytes
    ) -> Tuple[ConversionResponse, bytes]:
        """Record conversion and return response with file bytes"""
        pass
    
    @abstractmethod
    async def get_user_conversion_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[ConversionHistory]:
        """Get user's conversion history"""
        pass
