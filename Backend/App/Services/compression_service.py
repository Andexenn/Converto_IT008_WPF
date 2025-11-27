"""
compression service interface
"""
from abc import ABC, abstractmethod
from typing import Tuple, List

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

    @abstractmethod
    async def compress_images_batch(self, input_paths: List[str], quality: int = 50, timeout: int = 300) -> List[Tuple[str, str, int, bool]]:
        """
        Compress images batch
        
        Parameters:
        -----------
            input_paths(List[str]): a list of input paths
            quality(int): the quality of the image after compressing
            timeout(int): timeout in seconds
        
        Returns:
        --------
            List[Tuple[str, str, int, bool]]: a list of compression results
        """

    # @abstractmethod
    # async def 
    


