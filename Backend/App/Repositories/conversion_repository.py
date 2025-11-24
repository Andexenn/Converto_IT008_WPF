"""
conversion_repository module
"""
import io
import os
import multiprocessing
from pathlib import Path
import subprocess
from typing import List

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

    #================ IMAGE ================

    async def convert_image(self, file_content: bytes, out_format: str, output_path: str) -> tuple[str, bytes]:
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
                f"Failed to convert to open input file: {str(e)}"
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

        output_bytes = buffer.getvalue()

        try:
            with open(output_path, "wb") as f:
                f.write(output_bytes)
        except Exception as e:
            raise ValueError(f"Failed to save file to local path {str(e)}") from e

        return str(image.format), output_bytes

    #================ VIDEO & AUDIO ================

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

        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_dir = Path(output_path).parent

        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can not create a folder for output file"
                ) from e

        output_format = Path(output_path).suffix.lstrip('.').lower()

        try:
            is_success = await self._convert_video_audio_ffmpeg(input_path, output_path, output_format, timeout)

            if is_success is False:
                raise ValueError(f"FFmpeg conversion to {output_format.upper()} failed")

            if not Path(output_path).exists:
                raise FileNotFoundError(f"output file not found: {output_path}")

            if os.path.getsize(output_path) == 0:
                raise ValueError(f"The produced file was empty: {output_path}")

            return True
        except subprocess.TimeoutExpired as e:
            raise ValueError(f"Conversion to {output_format.upper()} is timed out. Files maybe too large or complex") from e
        except Exception as e:
            raise ValueError(f"The conversion was failed: {str(e)}") from e

    async def _convert_video_audio_ffmpeg(self, input_path: str, output_path: str, output_format: str, timeout: int = 300) -> bool:
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

    #================ GIF ================
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
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_dir = Path(output_path).parent

        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can not create a folder for output file"
                ) from e

        output_format = Path(output_path).suffix.lstrip('.').lower()
        input_format = Path(input_path).suffix.lstrip('.').lower()

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-y',
        ]

        try:
            # GIF to Image
            if input_format == "gif" and output_format in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "ppm", "pgm", "pbm", "tga"]:
                is_success = await self.convert_gif_to_image(input_format, output_format, timeout, output_path, cmd)

            # Image to GIF
            elif input_format in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "ppm", "pgm", "pbm", "tga"] and output_format == "gif":
                is_success = await self.convert_image_to_gif(input_format, output_format, timeout, output_path, cmd)

            # GIF to Video
            elif input_format == "gif" and output_format in ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "mpeg", "mpg", "ogv", "3gp"]:
                is_success = await self.convert_gif_to_video(input_format, output_format, timeout, output_path, cmd)

            # Video to GIF
            elif input_format in ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "mpeg", "mpg", "ogv", "3gp"] and output_format == "gif":
                is_success = await self.convert_video_to_gif(input_format, output_format, timeout, output_path, cmd)

            else:
                raise ValueError(f"Unsupported conversion: {input_format} to {output_format}")

            if not is_success:
                raise ValueError(f"Failed to convert from {input_format} to {output_format}")

            if not Path(output_path).exists():
                raise FileNotFoundError(f"Output file not created: {output_path}")

            return True

        except Exception as e:
            raise ValueError(f"Conversion failed: {str(e)}") from e

    async def convert_gif_to_image(self, input_format: str, output_format: str, timeout: int, output_path: str, cmd: List) -> bool:
        """
            Convert from GIF to image using FFmpeg
            Parameter:
            ----------
                input_path(str): contains the original file path
                output_path(str): contains the final file path
                timeout(int): timeout in second
                cmd(List(str)): contains the list of parameters to create a subprocess
            Return:
            -------
                True if convert successfully else False
        """
        try:
            cmd.extend(['-vframes', '1'])

            if output_format in ['jpg', 'jpeg']:
                cmd.extend(['-q:v', '2'])
            elif output_format == 'png':
                cmd.extend(['-compression_level', '6',])
            elif output_format == 'webp':
                cmd.extend(['-q:v', '90'])
            
            cmd.append(output_path)

            with multiprocessing.Pool() as pool:
                result  = pool.apply_async(self._execute_ffmpeg, (cmd, ))
                return_code = result.get(timeout=timeout)

            return return_code == 0
        except Exception as e:
            raise ValueError(f"Conversion from GIF to {output_format} failed: {str(e)}") from e 

    async def convert_image_to_gif(self, input_format: str, output_format: str, timeout: int, output_path: str, cmd: List) -> bool:
        """
            Convert from image to GIF using FFmpeg
            Parameter:
            ----------
                input_path(str): contains the original file path
                output_path(str): contains the final file path
                timeout(int): timeout in second

            Return:
            -------
                True if convert successfully else False
        """
        try:
            cmd.extend([
                '-t', '1',
                '-loop', '0',
            ])

            cmd.append(output_path)

            with multiprocessing.Pool() as pool:
                result = pool.apply_async(self._execute_ffmpeg, (cmd, ))
                return_code = result.get(timeout=timeout)

            return return_code == 0
        except Exception as e:
            raise ValueError(f"Image to GIF conversion failed: {str(e)}") from e

    async def convert_video_to_gif(self, input_format: str, output_format: str, timeout: int, output_path: str, cmd: List) -> bool:
        """
            Convert from video to GIF using FFmpeg
            Parameter:
            ----------
                input_path(str): contains the original file path
                output_path(str): contains the final file path
                timeout(int): timeout in second

            Return:
            -------
                True if convert successfully else False
        """

        try:
            # High-quality GIF conversion with palette generation
            # This creates a 2-pass conversion for better quality
            cmd.extend([
                '-vf', 'fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5',
                # fps=15: 15 frames per second (good balance)
                # scale=640:-1: resize to 640px width, maintain aspect ratio
                # palettegen: generate optimal 256 color palette
                # paletteuse: apply palette with dithering for smoother colors
                '-loop', '0',  # Loop forever
            ])
            
            cmd.append(output_path)
            
            # Execute FFmpeg
            with multiprocessing.Pool() as pool:
                result = pool.apply_async(self._execute_ffmpeg, (cmd,))
                return_code = result.get(timeout=timeout)
        
            return return_code == 0 
        except Exception as e:
            raise ValueError(f"Video to GIF conversion failed: {str(e)}") from e

    async def convert_gif_to_video(self, input_format: str, output_format: str, timeout: int, output_path: str, cmd: List) -> bool:
        """
            Convert from GIF to video using FFmpeg
            Parameter:
            ----------
                input_path(str): contains the original file path
                output_path(str): contains the final file path
                timeout(int): timeout in second

            Return:
            -------
                True if convert successfully else False
        """
        try:
            # Video format-specific settings (LGPL-compatible codecs)
            if output_format == 'webm':
                cmd.extend([
                    '-c:v', 'libvpx',  # VP8 video codec (LGPL)
                    '-b:v', '1M',  # Video bitrate
                    '-crf', '10',  # Quality (4-63, lower = better)
                    '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
                    '-auto-alt-ref', '0',  # Disable alt reference frames
                ])
            elif output_format == 'mp4':
                cmd.extend([
                    '-c:v', 'mpeg4',  # MPEG-4 video codec (LGPL)
                    '-q:v', '5',  # Quality (1-31, lower = better)
                    '-pix_fmt', 'yuv420p',  # Pixel format
                    '-movflags', '+faststart',  # Enable streaming
                ])
            elif output_format in ['avi', 'mkv']:
                cmd.extend([
                    '-c:v', 'mpeg4',  # MPEG-4 codec
                    '-q:v', '5',
                    '-pix_fmt', 'yuv420p',
                ])
            elif output_format == 'mov':
                cmd.extend([
                    '-c:v', 'mpeg4',
                    '-q:v', '5',
                    '-pix_fmt', 'yuv420p',
                ])
            elif output_format in ['mpeg', 'mpg']:
                cmd.extend([
                    '-c:v', 'mpeg2video',  # MPEG-2 codec
                    '-b:v', '2M',
                    '-pix_fmt', 'yuv420p',
                ])
            elif output_format == 'ogv':
                cmd.extend([
                    '-c:v', 'libtheora',  # Theora codec (LGPL)
                    '-q:v', '7',  # Quality (0-10)
                ])
            elif output_format == '3gp':
                cmd.extend([
                    '-c:v', 'mpeg4',
                    '-s', '176x144',  # Standard 3GP resolution
                    '-b:v', '256k',
                ])
            elif output_format in ['flv', 'wmv']:
                cmd.extend([
                    '-c:v', 'mpeg4',
                    '-q:v', '5',
                ])
            else:
                # Default fallback
                cmd.extend([
                    '-c:v', 'mpeg4',
                    '-q:v', '5',
                    '-pix_fmt', 'yuv420p',
                ])
            
            cmd.append(output_path)
            
            # Execute FFmpeg
            with multiprocessing.Pool() as pool:
                result = pool.apply_async(self._execute_ffmpeg, (cmd,))
                return_code = result.get(timeout=timeout)
            
            return return_code == 0
            
        except Exception as e:
            raise ValueError(f"GIF to video conversion failed: {str(e)}") from e