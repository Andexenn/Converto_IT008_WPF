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
    async def compress_images_batch(self, input_paths: List[str], quality: int = 50, timeout: int = 600) -> List[Tuple[str, str, int, bool]]:
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

    @abstractmethod
    async def compress_video(self, input_path: str, quality: str = "low", timeout: int = 600) -> Tuple[str, int]:
        """
        Compress video file while maintaining format

        Quality presets:
        - "low": Aggressive compression (smallest file, lower quality)
        - "medium": Balanced compression (good quality/size ratio)
        - "high": Light compression (best quality, larger file)

        Parameters:
        -----------
            input_path(str): path to input video file
            quality(str): compression quality preset
            timeout(int): timeout in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
        -------
            ValueError: if compression failed
        """

    @abstractmethod
    async def compress_audio(self, input_path: str, bitrate: str = "64k", timeout: int = 600) -> Tuple[str, int]:
        """
        Compress audio file while maintaining format

        Parameters:
        -----------
            input_path(str): path to input audio file
            bitrate(str): target audio bitrate (e.g., "128k")
            timeout(int): timeout in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
        -------
            ValueError: if compression failed
        """

    @abstractmethod
    async def compress_videos_batch(self, input_paths: List[str], quality: str = 'low', timeout: int = 600) -> List[Tuple[str, str, int, bool]]:
        """
        Compress multiple videos in parallel

        Parameters:
        -----------
            input_paths(List[str]): list of input video paths
            quality(str): compression quality preset
            timeout(int): timeout per file

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: (input_path, output_path, size, success)
        """

    @abstractmethod
    async def compress_audios_batch(self, input_paths: List[str], bitrate: str = '64k', timeout: int = 600) -> List[Tuple[str, str, int, bool]]:
        """
        Compress multiple audio files in parallel

        Parameters:
        -----------
            input_paths(List[str]): list of input audio paths
            bitrate(str): target audio bitrate
            timeout(int): timeout per file

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: (input_path, output_path, size, success)
        """
    


