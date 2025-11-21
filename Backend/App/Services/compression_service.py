"""
compression service interface
"""
from abc import ABC, abstractmethod

class ICompressionSerivce(ABC):
    """
    A compress interface
    """
    @abstractmethod
    async def compress(self, file_content: bytes, out_format: str) -> tuple[str, bytes]:
        """
        Compress image file content to smaller size

        Parameters:
        -----------
        file_contents(bytes): the image loaded as bytes
        out_format: target format for compression
        """