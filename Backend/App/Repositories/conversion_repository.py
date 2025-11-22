"""
conversion_repository module
"""
import io
import os
import multiprocessing
from pathlib import Path
import subprocess

from PIL import Image
from fastapi import HTTPException, status

from Services.conversion_service import IConversionService

FFMPEG_EXECUTABLE_NAME = 'ffmpeg.exe'
class ConversionRepository(IConversionService):
    """
    Conversion repository class
    """
    def __init__(self):
        """
        Initialize with ffmpeg path
        """
        self.ffmpeg_path = self._get_ffmpeg_path

    @property
    def _get_ffmpeg_path(self) -> str:
        """
        Get the ffmpeg path
        """
        current_dir = Path(__file__).parent.parent.parent.parent
        ffmpeg_path = current_dir / 'bin' / 'Debug' / 'net9.0-windows' / FFMPEG_EXECUTABLE_NAME

        if not ffmpeg_path.exists():
            raise FileNotFoundError(
                f"FFmpeg executable not found. Please ensure {FFMPEG_EXECUTABLE_NAME} exists"
            )

        return str(ffmpeg_path.absolute())

    async def convert_image(self, file_content: bytes, out_format: str) -> tuple[str, bytes]:
        """
        Convert image from various types using Pillow

        Paramenters:
        ------------
            file_content(bytes): the input file as bytes
            out_format(str): the format that user want to convert to

        Returns:
        --------
            tuple(str, bytes): (output format and converted bytes)

        Raises:
        -------
            Exception: if convert failed
        """
        try:
            image = Image.open(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(
                f"Failed to convert to {out_format.upper()}: {str(e)}"
            ) from e

        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        try:
            image.save(buffer, format=out_format.upper(), optimize=True)
        except Exception as e:
            raise ValueError(
                 f"Failed to convert {image.format} to {out_format.upper()}: {str(e)}"
            ) from e
        return str(image.format), buffer.getvalue()

    async def convert_video_audio(self, input_path: str, output_path: str, timeout: int = 300) -> bool:
        """
        Convert audio and video from various types using ffmpeg with multiprocessing

        Paramenters:
        ------------
            file_content(bytes): the input file as bytes
            out_format(str): desired output format
            timeout(int): maximum time in seconds

        Returns:
        --------
            True if convert successfully else False

        Raises:
            ValueError: If conversion failed
            FileNotFoundError: If input file doesn't exist
        """

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_dir = Path(output_path).parent

        if not os.path.exists(output_dir):
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can not create a folder for output file"
                ) from e
            
        output_format = Path(output_path).suffix.lstrip('.').lower()
        
        try:
            is_success = await self._run_ffmpeg_conversion(input_path, output_path, output_format, timeout)

            if is_success is False:
                raise ValueError(f"FFmpeg conversion to {output_format.upper()} failed")

            if not os.path.exists(output_path):
                raise FileNotFoundError(f"output file not found: {output_path}")

            if os.path.getsize(output_path) == 0:
                raise ValueError(f"The produced file was empty: {output_path}")

            return True
        except subprocess.TimeoutExpired as e:
            raise ValueError(f"Conversion to {output_format.upper()} is timed out. Files maybe too large or complex") from e
        except Exception as e:
            raise ValueError(f"The conversion was failed: {str(e)}") from e

    async def _run_ffmpeg_conversion(self, input_path: str, output_path: str, output_format: str, timeout: int = 300) -> bool:
        """
        Run FFmpeg conversion in separate process

        Parameter:
        ----------
            input_path(str): the filepath to the file want to convert
            output_path(str): desired the conversion
            output_format(str): the desired output format
            timeout(int): maximum time in seconds

        Returns:
        --------
            True if run successfully else False
        """

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-y',
        ]

        if output_format in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
            if output_format == 'webm':
                cmd.extend([
                    '-c:v', 'libvpx',  # VP8 codec (LGPL-compatible)
                    '-b:v', '1M',
                    '-c:a', 'libvorbis',  # Vorbis audio (LGPL-compatible)
                    '-b:a', '128k',
                ])
            else:
                cmd.extend([
                    '-c:v', 'mpeg4', # video codec
                    '-q:v', '5', # Encoding speed/quality
                    '-c:a', 'aac', #Audio codec
                    '-b:a', '128k', #audio bitrate
                ])
        elif output_format in ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a']:
            if output_format == 'mp3':
                cmd.extend(['-c:a', 'mp2', '-b:a' ,'192k']) #MP2 as fallback
            elif output_format == 'wav':
                cmd.extend(['-c:a', 'pcm_s16le'])
            elif output_format == 'aac':
                cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
            elif output_format == 'ogg':
                cmd.extend(['-c:a', 'libvorbis', '-q:a', '6'])
            elif output_format == 'flac':
                cmd.extend(['-c:a', 'flac', '-compression_level', '5'])
            elif output_format == 'm4a':
                cmd.extend(['-c:a', 'aac', '-b:a', '192k'])

        cmd.append(output_path)

        try:
            with multiprocessing.Pool() as pool:
                result = pool.apply_async(self._execute_ffmpeg, (cmd, ))
                return_code = result.get(timeout=timeout)
            return return_code == 0
        except Exception as e:
            raise ValueError(f"run ffmpeg conversion failed: {e}") from e

    @staticmethod
    def _execute_ffmpeg(cmd: list) -> int:
        """
        Execute the ffmpeg with config statistic

        Parameter:
        ----------
            cmd(list): FFmpeg command as input
        Returns:
        --------
            int: Return code from the ffmpeg
        """

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

            return result.returncode
        except Exception as e:
            print(f"FFmpeg execution error: {str(e)}") 
            return 1
