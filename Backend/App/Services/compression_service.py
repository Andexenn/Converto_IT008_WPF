"""
compression service interface
"""
from abc import ABC, abstractmethod
from typing import Tuple

class ICompressionSerivce(ABC):
    """
    A compress interface
    """
    @abstractmethod
    async def compress_image(self, input_path: str, quality: int = 50, timeout: int = 300) -> Tuple[str, int]:
        """
        Compress image file content to smaller size

        Parameters:
        -----------
        input_path(str): the path of the original file
        output_path(str): the path of the converted file

        Return:
        -------
        True if succeed else False
        """