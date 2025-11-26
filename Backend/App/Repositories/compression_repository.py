"""
Improved compression repository module with temporary file handling
"""

import tempfile
import os
import asyncio
import subprocess
from pathlib import Path
from typing import Tuple, List
from concurrent.futures import ProcessPoolExecutor, as_completed

from Services.compression_service import ICompressionSerivce

MAGICK_EXECUTABLE_NAME = 'magick.exe'

class CompressionRepository(ICompressionSerivce):
    """
    Compression class with temporary file handling
    """

    def __init__(self):
        """Initialize with path to magickpath"""
        self.magick_path = self._get_magick_path
        self.max_workers = max(1, os.cpu_count() - 1)

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
    async def _run_in_executor(func, *args):
        """Helper to run sync function for single file processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    #================ IMAGE ================

    async def compress_image(self, input_path: str, quality: int = 50, timeout: int = 300) -> Tuple[str, int]:
        """
        Compress image file keeping the same format (PNG stays PNG, JPEG stays JPEG)
        Returns path to temporary output file and its size

        Parameters:
        ------------
            input_path(str): the path of the original file
            quality(int): compression quality (1-100)
            timeout(int): timeout in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
        -------
            ValueError: if compression failed
        """
        return await self._run_in_executor(
            self._compress_with_imagemagick_sync,
            input_path,
            self.magick_path,
            quality,
            timeout
        )
    
    async def compress_images_batch(
        self, 
        input_paths: List[str], 
        quality: int = 50, 
        timeout: int = 300
    ) -> List[Tuple[str, str, int, bool]]:
        """
        Compress multiple images in parallel

        Parameters:
        -----------
            input_paths(List[str]): list of input file paths
            quality(int): compression quality
            timeout(int): timeout per file

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: (input_path, output_path, size, success)
        """
        if not input_paths:
            return []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # ✅ Fixed: Correct parameter order
            future_to_path = {
                executor.submit(
                    self._compress_with_imagemagick_sync,
                    input_path,          # First parameter
                    self.magick_path,    # Second parameter
                    quality,             # Third parameter
                    timeout              # Fourth parameter
                ): input_path for input_path in input_paths
            }

            results = []

            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    output_path, file_converted_size = future.result(timeout=timeout + 10)
                    results.append((input_path, output_path, file_converted_size, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    results.append((input_path, "", 0, False))

            return results

    @staticmethod    
    def _compress_with_imagemagick_sync(
        input_path: str, 
        magick_path: str, 
        quality: int, 
        timeout: int = 300
    ) -> Tuple[str, int]:
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
            magick_path(str): path to ImageMagick executable
            quality(int): quality level (1-100)
            timeout(int): timeout in seconds
            
        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """
        # Verify input exists
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        input_format = Path(input_path).suffix.lstrip('.').lower()
    
        # Build ImageMagick command based on format
        cmd = [magick_path, input_path]
        
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
        
        # Create output path
        output_path = CompressionRepository.create_temp_output_file(f'.{input_format}')
        cmd.append(output_path)

        try:
            # ✅ Fixed: Use subprocess directly instead of multiprocessing
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                if Path(output_path).exists():
                    os.unlink(output_path)
                raise ValueError(f"ImageMagick compression failed: {error_msg}")
            
            # Verify output file exists and is not empty
            if not Path(output_path).exists():
                raise FileNotFoundError("Output file was not created")
            
            file_size = os.path.getsize(output_path)
            
            if file_size == 0:
                os.unlink(output_path)
                raise ValueError("The created file was empty")
            
            # ✅ Fixed: Return the tuple!
            return output_path, file_size
            
        except subprocess.TimeoutExpired as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Compression timed out after {timeout} seconds") from e
            
        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Compression failed: {str(e)}") from e