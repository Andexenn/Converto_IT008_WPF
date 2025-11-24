"""
compression service interface
"""
from abc import ABC, abstractmethod

class ICompressionSerivce(ABC):
    """
    A compress interface
    """
    @abstractmethod
    async def compress(self, input_path: str, output_path: str) -> bool:
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