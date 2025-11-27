"""
Conversion service interface
"""

from abc import ABC, abstractmethod
from typing import Tuple, List

class IConversionService(ABC):
    """
    Conversion service interface
    """
    @abstractmethod
    async def convert_image(self, input_path: str, output_format: str) -> Tuple[str, int]:
        """
        Converts image file content to out format
        
        Parameter:
        ----------
        - file_content (bytes): image file content loaded as bytes
        - out_format (str): target output format
        """

    @abstractmethod
    async def convert_images_batch(self, input_paths: List[str], output_format: str) -> List[Tuple[str, str, int, bool]]:
        """
        Convert multiple images in parallel using multiprocessing
        
        Parameters:
        ------------
            input_paths(List[str]): list of input file paths
            output_format(str): desired output format (e.g., 'png', 'jpg')

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: List of (input_path, output_path, file_size, success)

        Example:
        --------
            results = await convert_images_batch([
                "image1.png",
                "image2.bmp",
                "image3.tiff"
            ], "jpg")
            
            for input_path, output_path, size, success in results:
                if success:
                    print(f"Converted {input_path} -> {size} bytes")
                else:
                    print(f"Failed to convert {input_path}")
        """

    @abstractmethod
    async def convert_video_audio(self, input_path: str, output_format: str, timeout: int) -> Tuple[str, int]:
        """
        Converts video, audio file content to out format

        Parameter:
        ----------
            input_path(str): contains the original file path
            output_path(str): contains the final file path
            timeout(int): timeout in second
        
        Return:
        -------
            True if convert successfully else False
        """

    @abstractmethod 
    async def convert_video_audio_batch(self, input_paths: List[str], output_format: str, timeout: int) -> List[Tuple[str, str, int, bool]]:
        """
        Convert multiple video/audio files in parallel using multiprocessing
        
        Parameters:
        ------------
            input_paths(List[str]): list of input file paths
            output_format(str): desired output format (e.g., 'mp4', 'mp3')
            timeout(int): maximum time in seconds per file

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: List of (input_path, output_path, file_size, success)
        """

    @abstractmethod
    async def convert_gif(self, input_path: str, output_format: str, timeout: int) -> Tuple[str, int]:
        """
        Convert GIF using FFmpeg

        Parameter:
        ----------
            input_path(str): contains the original file path
            output_path(str): contains the final file path
            timeout(int): timeout in second
        
        Return:
        -------
            True if convert successfully else False
        """

    @abstractmethod 
    async def convert_gif_batch(self, input_paths: List[str], output_format: str, timeout: int) -> List[Tuple[str, str, int, bool]]:
        """
        Convert multiple GIF/image/video files in parallel using multiprocessing
        
        Parameters:
        ------------
            input_paths(List[str]): list of input file paths
            output_format(str): desired output format
            timeout(int): maximum time in seconds per file

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: List of (input_path, output_path, file_size, success)
        """


    @abstractmethod
    async def convert_pdf_office(self, input_path: str, output_format: str, timeout: int) -> Tuple[str, int]:
        """
        Convert PDF to office or office to PDF 

        Parameter:
        ----------
            input_path(str): contains the original file path
            output_path(str): contains the final file path
            timeout(int): timeout in second
        
        Return:
        -------
            True if convert successfully else False
        """
        