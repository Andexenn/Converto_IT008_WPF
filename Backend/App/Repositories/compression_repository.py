"""
Improved compression repository module with temporary file handling
"""

import tempfile
import os
from pathlib import Path
from typing import Tuple, List
import subprocess
import multiprocessing

from Services.compression_service import ICompressionSerivce

MAGICK_EXECUTABLE_NAME = 'magick.exe'

class CompressionRepository(ICompressionSerivce):
    """
    Compression class with temporary file handling
    """

    def __init__(self):
        """Initialize with path to magickpath"""
        self.magick_path = self._get_magick_path

    @property
    def _get_magick_path(self) -> str:
        """
        Get the path to Magick executable
        """
        magick_path = Path(__file__).parent.parent.parent.parent / 'bin' / 'Debug' / 'net9.0-windows' / MAGICK_EXECUTABLE_NAME

        if not Path(magick_path).exists():
            raise FileNotFoundError("MAGICK executable file not found")
        
        return str(magick_path.absolute())
    
    @staticmethod
    def _verify_input_path(input_path: str) -> None:
        """ Verify input path if it exists """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"{input_path} not found")
        
    @staticmethod
    def create_temp_output_file(suffix: str) -> str:
        """
        Create a temporary file 

        Parameters:
        -----------
            suffix(str): file extension 

        Returns:
        --------
            str: path to temporary file
        """

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def _execute_magick(cmd: List) -> int:
        """Execute the subprocess with magick"""
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

            return result.returncode
        except Exception as e:
            raise ValueError(f"execute magick failed: {str(e)}") from e 


    #================ IMAGE ================

    async def compress_image(self, input_path: str, quality: int = 50) -> Tuple[str, int]:
        """
        Compress image file keeping the same format (PNG stays PNG, JPEG stays JPEG)
        Returns path to temporary output file and its size

        Parameters:
        ------------
            input_path(str): the path of the original file
            reduce_colors(bool): for PNG, reduce to 256 colors for better compression

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
        -------
            Exception: if compress failed
        """

        self._verify_input_path(input_path)
        output_path = self.create_temp_output_file(Path(input_path).suffix)

        try:
            is_success = await self._compress_with_imagemagick(input_path, output_path, quality, 300)

            if not is_success:
                if Path(output_path).exists():
                    os.unlink(output_path)
            
            if not Path(output_path).exists():
                raise FileExistsError("Ouput file was not created")
            
            if os.path.getsize(output_path) == 0:
                os.unlink(output_path)
                raise ValueError("The produced file was empty")
        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Compress {input_path} failed") from e 
        
        file_size = os.path.getsize(output_path)
        return output_path, file_size
        
    async def _compress_with_imagemagick(self, input_path: str, output_path: str, quality: int, timeout: int = 300) -> bool:
        """
        Compress image using ImageMagick (Universal - ALL formats)
        
        ImageMagick compression results:
        - PNG: 50-80% reduction
        - JPEG: 40-70% reduction  
        - WebP: 60-85% reduction
        - GIF: 30-60% reduction
        - TIFF: 40-70% reduction
        - BMP: 60-90% reduction
        
        Parameters:
        -----------
            input_path(str): input file path
            quality(int): quality level (1-100)
            
        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """

        input_format = Path(input_path).suffix.lstrip('.').lower()
    
        # Build ImageMagick command based on format
        cmd = [self.magick_path, input_path]
        
        # Format-specific optimizations
        if input_format in ['jpg', 'jpeg']:
            # JPEG compression with Google PageSpeed recommendations
            cmd.extend([
                '-sampling-factor', '4:2:0',  # Reduce chroma channel resolution
                '-strip',  # Remove metadata
                '-quality', str(quality),
                '-interlace', 'JPEG',  # Progressive JPEG
                '-colorspace', 'sRGB'
            ])
        
        elif input_format == 'png':
            # PNG compression
            cmd.extend([
                '-strip',  # Remove metadata
                '-quality', str(quality),
                '-define', 'png:compression-level=9',  # Maximum compression
                '-define', 'png:compression-filter=5',
                '-define', 'png:compression-strategy=1'
            ])
            
            # For aggressive compression, reduce colors
            if quality < 85:
                cmd.extend(['-colors', '256'])  # Reduce to 256 colors
        
        elif input_format == 'gif':
            # GIF compression
            cmd.extend([
                '-strip',
                '-layers', 'optimize',  # Optimize animation layers
                '-define', 'gif:optimize-transparency',
                '-quality', str(quality)
            ])
        
        elif input_format == 'webp':
            # WebP compression (excellent compression)
            cmd.extend([
                '-strip',
                '-quality', str(quality),
                '-define', 'webp:method=6',  # Best compression method
                '-define', f'webp:lossless=false'
            ])
        
        elif input_format in ['tiff', 'tif']:
            # TIFF compression
            cmd.extend([
                '-strip',
                '-compress', 'LZW',  # Lossless compression
                '-quality', str(quality)
            ])
        
        elif input_format == 'bmp':
            # BMP compression (convert to more efficient format structure)
            cmd.extend([
                '-strip',
                '-compress', 'RLE',  # Run-length encoding
                '-quality', str(quality)
            ])
        
        elif input_format == 'svg':
            # SVG optimization (remove unnecessary data)
            cmd.extend([
                '-strip',
                '-quality', str(quality)
            ])
        
        elif input_format == 'avif':
            # AVIF compression (next-gen format)
            cmd.extend([
                '-strip',
                '-quality', str(quality),
                '-define', 'avif:speed=0'  # Best compression (slower)
            ])
        
        else:
            # Generic compression for other formats
            cmd.extend([
                '-strip',
                '-quality', str(quality),
                '-compress', 'LZW'
            ])
        
        # Add output path
        cmd.append(output_path)

        try:
            with multiprocessing.Pool() as pool:
                result = pool.apply_async(self._execute_magick, (cmd, ))
                return_code = result.get(timeout=timeout)
            return return_code == 0
        except subprocess.TimeoutExpired:
            if Path(output_path).exists():
                os.unlink(output_path)
        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"run ffmpeg conversion failed: {e}") from e

           
            