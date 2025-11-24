"""
Conversion service interface
"""

from abc import ABC, abstractmethod

class IConversionService(ABC):
    """
    Conversion service interface
    """
    @abstractmethod
    async def convert_image(self, input_path: str, output_path: str) -> bool:
        """
        Converts image file content to out format
        
        Parameter:
        ----------
        - file_content (bytes): image file content loaded as bytes
        - out_format (str): target output format
        """

    @abstractmethod
    async def convert_video_audio(self, input_path: str, output_path: str, timeout: int) -> bool:
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
    async def convert_gif(self, input_path: str, output_path: str, timeout: int) -> bool:
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
    async def convert_pdf_office(self, input_path: str, output_path: str, timeout: int) -> bool:
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
        