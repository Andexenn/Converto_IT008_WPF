"""
Conversion service interface
"""

from abc import ABC, abstractmethod

class IConversionService(ABC):
    """
    Conversion service interface
    """
    @abstractmethod
    async def convert(self, file_content: bytes, out_format: str) -> bytes:
        """
        Converts image file content to out format
        
        Parameter:
        ----------
        - file_content (bytes): image file content loaded as bytes
        - out_format (str): target output format
        """
