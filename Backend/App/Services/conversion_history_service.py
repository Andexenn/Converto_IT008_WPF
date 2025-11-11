"""
conversion history module
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from Schemas.conversion import ConversionResponse
from Entities.conversion_history import ConversionHistory
from Entities.service import Service

class IConversionHistoryService(ABC):
    """Interface for conversion history management (shared across all converters)"""

    @abstractmethod
    async def get_or_create_service(
        self,
        input_format: str,
        output_format: str
    ) -> Service:
        """
        Target to create if not exist and get if exist

        Parameter:
        ----------
        input_format(str): input format for the original file
        output_format(str): output format for the target file
        """

    @abstractmethod
    async def record_conversion(
        self,
        user_id: int,
        input_format: str,
        output_format: str,
        original_filename: str,
        converted_filename: str,
        file_size_bytes: bytes,
        converted_file_bytes: bytes
    ) -> Tuple[ConversionResponse, bytes]:
        """Record conversion and return response with file bytes"""

    @abstractmethod
    async def get_user_conversion_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[ConversionHistory]:
        """Get user's conversion history"""
