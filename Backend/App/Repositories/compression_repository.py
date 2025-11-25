"""
Improved compression repository module with temporary file handling
"""

import io
import tempfile
import os
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, status
from PIL import Image

from Services.compression_service import ICompressionSerivce

class CompressionRepository(ICompressionSerivce):
    """
    Compression class with temporary file handling
    """

    @staticmethod
    def _verify_input_path(input_path: str) -> None:
        """Verify only the input path exists"""
        if not Path(input_path).exists():
            raise FileNotFoundError(f"File not found: {input_path}")

    @staticmethod
    def create_temp_output_file(suffix: str) -> str:
        """
        Create a temporary output file
        
        Parameters:
        -----------
            suffix(str): file extension (e.g., '.png', '.jpg')
            
        Returns:
        --------
            str: path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        return temp_file.name

    #================ IMAGE ================

    async def compress_image(self, input_path: str, reduce_colors: bool = False) -> Tuple[str, int]:
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

        try:
            with open(input_path, "rb") as f:
                file_content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read input file: {str(e)}") from e

        try:
            image = Image.open(io.BytesIO(file_content))
            original_format = image.format
        except Exception as e:
            raise ValueError(
                f"Failed to open input file: {str(e)}"
            ) from e

        # Get output format from input file to keep same format
        output_format = Path(input_path).suffix.lstrip('.').upper()
        
        # Create temporary output file with same extension
        output_path = self.create_temp_output_file(Path(input_path).suffix)

        try:
            # PNG-specific compression
            if output_format == 'PNG':
                if reduce_colors:
                    # Method 1: Reduce to indexed color (256 colors) - SIGNIFICANT size reduction
                    if image.mode == 'RGBA':
                        # Preserve transparency
                        alpha = image.split()[3]
                        # Convert RGB channels to palette mode
                        rgb = Image.merge('RGB', image.split()[:3])
                        rgb = rgb.convert('P', palette=Image.ADAPTIVE, colors=255)
                        # Convert back to RGBA with reduced colors
                        rgb = rgb.convert('RGBA')
                        rgb.putalpha(alpha)
                        image = rgb
                    elif image.mode == 'RGB':
                        # Convert to palette mode with 256 colors
                        image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
                        image = image.convert('RGB')  # Convert back for compatibility
                
                # Save with maximum PNG compression
                image.save(output_path, format='PNG', optimize=True, compress_level=9)
            
            # JPEG-specific compression
            elif output_format in ('JPEG', 'JPG'):
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Convert to RGB (JPEG doesn't support transparency)
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                    image = rgb_image
                
                image.save(output_path, format='JPEG', quality=85, optimize=True, progressive=True)
            
            # Other formats
            else:
                image.save(output_path, format=original_format, optimize=True)
                
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ValueError(f"Failed when compressing {input_path}: {str(e)}") from e

        file_size = os.path.getsize(output_path)
        return output_path, file_size