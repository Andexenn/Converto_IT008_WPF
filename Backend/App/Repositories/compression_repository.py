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
import multiprocessing
import time 

from sqlalchemy.orm import Session

from Services.compression_service import ICompressionSerivce
from Schemas.task import TaskCompression
from Entities.tasks import Tasks

MAGICK_EXECUTABLE_NAME = 'magick.exe'
FFMPEG_EXECUTABLE_NAME = 'ffmpeg.exe'
SERVICETYPEID = 2

class CompressionRepository(ICompressionSerivce):
    """
    Compression class with temporary file handling
    """

    def __init__(self, db: Session, UserID: int):
        """Initialize with path to magickpath"""
        self.magick_path = self._get_magick_path
        self.max_workers = max(1, multiprocessing.cpu_count()  - 1)
        self.ffmpeg_path = self._get_ffmpeg_path

        self.db = db
        self.user_id = UserID

    @property
    def _get_magick_path(self) -> str:
        """
        Get the path to Magick executable
        """
        magick_path = Path(__file__).parent.parent.parent.parent / 'bin' / 'Debug' / 'net9.0-windows' / MAGICK_EXECUTABLE_NAME

        if not Path(magick_path).exists():
            raise FileNotFoundError("MAGICK executable file not found")

        return str(magick_path.absolute())

    @property
    def _get_ffmpeg_path(self) -> str:
        """Get the path to FFmpeg executable file"""
        ffmpeg_path = Path(__file__).parent.parent.parent.parent / 'bin' / 'Debug' / 'net9.0-windows' / FFMPEG_EXECUTABLE_NAME

        if not Path(ffmpeg_path).exists():
            raise FileNotFoundError("FFmpeg executable file not found")

        return str(ffmpeg_path.absolute())


    @staticmethod
    def _verify_input_path(input_path: str) -> None:
        """ Verify input path if it exists """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"{input_path} not found")

    @staticmethod
    def _create_temp_output_file(suffix: str) -> str:
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
    
    def _record_task(self, task: TaskCompression ):
        """Record the task"""
        task_dict = task.model_dump(exclude_unset=True)
        cur_task = Tasks(**task_dict)
        self.db.add(cur_task)

        self.db.commit()

        return True

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

        try:
            data = await self._run_in_executor(
                self._compress_with_imagemagick_sync,
                input_path,
                self.magick_path,
                quality,
                timeout
            )

            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                CompressionLevel=data["CompressionLevel"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)

        except Exception as e:
            print(f"Fail to compress {input_path}: {str(e)}")
            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID, 
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)

        return (str(task.OutputFilePath), int(task.OutputFileSize))
        

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
            future_to_path = {
                executor.submit(
                    self._compress_with_imagemagick_sync,
                    input_path,
                    self.magick_path,
                    quality,
                    timeout
                ): input_path for input_path in input_paths
            }

            results = []

            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result(timeout=timeout + 10)
                    
                    task = TaskCompression(
                        UserID=self.user_id, 
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        CompressionLevel=data["CompressionLevel"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    task = TaskCompression(
                        UserID=self.user_id, 
                        ServiceTypeID=SERVICETYPEID, 
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))


        return results
    
    @staticmethod
    def _compress_with_imagemagick_sync(
        input_path: str,
        magick_path: str,
        quality: int,
        timeout: int = 300
    ) -> dict:
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

        if input_format in ['jpg', 'jpeg']:
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
                '-define', 'webp:lossless=false'
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
            cmd.extend([
                '-strip',
                '-quality', str(quality),
                '-compress', 'LZW'
            ])

        # Create output path
        output_path = CompressionRepository._create_temp_output_file(f'.{input_format}')
        cmd.append(output_path)

        if quality > 75:
            compression_level = "low"
        elif quality > 50:
            compression_level = "medium"
        else:
            compression_level = "high"

        start_time = time.perf_counter()

        try:
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

        except subprocess.TimeoutExpired as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Compression timed out after {timeout} seconds") from e

        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Compression failed: {str(e)}") from e
        
        
        end_time = time.perf_counter()

        return {
            "OriginalFileName": Path(input_path).stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": input_path,
            "OutputFileName": Path(output_path).stem,
            "OutputFileSize": os.path.getsize(output_path),
            "OutputFilePath": output_path,
            "TaskStatus": (True if file_size != 0 else False),
            "CompressionLevel": compression_level,
            "TaskTime": end_time - start_time
        }

    #================ Video ================
    async def compress_video(
        self,
        input_path: str,
        quality: str = "low",
        timeout: int = 600
    ) -> Tuple[str, int]:
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

        try:
            data = await self._run_in_executor(
                self._compress_video_sync,
                input_path,
                self.ffmpeg_path,
                quality,
                timeout
            )

            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                CompressionLevel=data["CompressionLevel"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)
        except Exception as e:
            print(f"Fail to compress {input_path}: {str(e)}")
            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID, 
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)            

        return (str(task.OutputFilePath), int(task.OutputFileSize))

    async def compress_audio(
        self,
        input_path: str,
        bitrate: str = "64k",
        timeout: int = 300
    ) -> Tuple[str, int]:
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

        try:
            data = await self._run_in_executor(
                self._compress_audio_sync,
                input_path,
                self.ffmpeg_path,
                bitrate,
                timeout
            )

            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                CompressionLevel=data["CompressionLevel"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)
        
        except Exception as e:
            print(f"Fail to compress {input_path}: {str(e)}")
            task = TaskCompression(
                UserID=self.user_id, 
                ServiceTypeID=SERVICETYPEID, 
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)

        return (str(task.OutputFilePath), int(task.OutputFileSize))

    async def compress_videos_batch(
        self,
        input_paths: List[str],
        quality: str = "low",
        timeout: int = 600
    ) -> List[Tuple[str, str, int, bool]]:
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
        if not input_paths:
            return []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._compress_video_sync,
                    input_path,
                    self.ffmpeg_path,
                    quality,
                    timeout
                ): input_path for input_path in input_paths
            }

            results = []

            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result(timeout=timeout + 10)
                    
                    task = TaskCompression(
                        UserID=self.user_id, 
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        CompressionLevel=data["CompressionLevel"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    task = TaskCompression(
                        UserID=self.user_id, 
                        ServiceTypeID=SERVICETYPEID, 
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))

        return results

    async def compress_audios_batch(
        self,
        input_paths: List[str],
        bitrate: str = "64k",
        timeout: int = 300
    ) -> List[Tuple[str, str, int, bool]]:
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
        if not input_paths:
            return []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._compress_audio_sync,
                    input_path,
                    self.ffmpeg_path,
                    bitrate,
                    timeout
                ): input_path for input_path in input_paths
            }

            results = []

            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    output_path, file_size = future.result(timeout=timeout + 10)
                    results.append((input_path, output_path, file_size, True))
                except Exception as e:
                    print(f"Failed to compress audio {input_path}: {str(e)}")
                    results.append((input_path, "", 0, False))

            return results

    @staticmethod
    def _compress_video_sync(
        input_path: str,
        ffmpeg_path: str,
        quality: str = "low",
        timeout: int = 600
    ) -> dict:
        """
        Compress video using LGPL-compatible codecs only

        Available LGPL codecs in your FFmpeg:
        - VP9 (libvpx-vp9) for WebM
        - MPEG4 (mpeg4) for MP4/AVI/MKV/MOV
        - AAC (aac) for audio
        - Vorbis (libvorbis) for audio

        Compression ratios by quality:
        - low: 60-80% size reduction
        - medium: 40-60% size reduction
        - high: 20-40% size reduction

        Parameters:
        -----------
            input_path(str): input file path
            ffmpeg_path(str): path to FFmpeg executable
            quality(str): quality preset ("low", "medium", "high")
            timeout(int): timeout in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        input_format = Path(input_path).suffix.lstrip('.').lower()

        # Quality settings
        quality_settings = {
            "low": {
                "video_quality": "8",     # For MPEG4 q:v (lower quality)
                "vp9_crf": "40",          # For VP9 (higher = lower quality)
                "audio_bitrate": "96k"
            },
            "medium": {
                "video_quality": "5",
                "vp9_crf": "32",
                "audio_bitrate": "128k"
            },
            "high": {
                "video_quality": "2",
                "vp9_crf": "24",
                "audio_bitrate": "192k"
            }
        }

        if quality not in quality_settings:
            quality = "medium"

        settings = quality_settings[quality]

        # Create temp output file
        output_path = CompressionRepository._create_temp_output_file(f'.{input_format}')

        # Build FFmpeg command
        cmd = [
            ffmpeg_path,
            '-i', input_path,
            '-y',  # Overwrite output
        ]

        # Choose codec based on format
        if input_format == 'webm':
            # WebM: Use VP9 (LGPL)
            cmd.extend([
                '-c:v', 'libvpx-vp9',
                '-crf', settings['vp9_crf'],
                '-b:v', '0',              # Use CRF mode
                '-row-mt', '1',           # Multithreading
                '-cpu-used', '2',         # Speed/quality tradeoff (0=slowest/best, 5=fastest)
            ])
            # Audio: Vorbis for WebM (LGPL)
            cmd.extend([
                '-c:a', 'libvorbis',
                '-q:a', '4',              # Vorbis quality (0-10)
            ])
        else:
            # MP4/MOV/MKV/AVI: Use MPEG4 (LGPL)
            cmd.extend([
                '-c:v', 'mpeg4',
                '-q:v', settings['video_quality'],
                '-g', '300',              # Keyframe interval
            ])
            # Audio: AAC (LGPL)
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', settings['audio_bitrate'],
            ])

        # Common settings
        cmd.extend([
            '-ar', '44100',               # Sample rate
            '-pix_fmt', 'yuv420p',        # Pixel format
        ])

        # MP4/MOV specific optimization
        if input_format in ['mp4', 'mov']:
            cmd.extend(['-movflags', '+faststart'])

        cmd.append(output_path)

        start_time = time.perf_counter()

        try:
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
                raise ValueError(f"FFmpeg video compression failed: {error_msg}")

            if not Path(output_path).exists():
                raise FileNotFoundError("Output file was not created")

            file_size = os.path.getsize(output_path)

            if file_size == 0:
                os.unlink(output_path)
                raise ValueError("The created file was empty")

        except subprocess.TimeoutExpired as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Video compression timed out after {timeout} seconds") from e

        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Video compression failed: {str(e)}") from e

        end_time = time.perf_counter()

        return {
            "OriginalFileName": Path(input_path).stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": input_path,
            "OutputFileName": Path(output_path).stem,
            "OutputFileSize": os.path.getsize(output_path),
            "OutputFilePath": output_path,
            "TaskStatus": (True if file_size != 0 else False),
            "CompressionLevel": quality,
            "TaskTime": end_time - start_time
        }

    @staticmethod
    def _compress_audio_sync(
        input_path: str,
        ffmpeg_path: str,
        bitrate: str = "64k",
        timeout: int = 300
    ) -> dict:
        """
        Compress audio using LGPL-compatible codecs only

        Available LGPL audio codecs:
        - AAC (aac) - Most formats
        - Vorbis (libvorbis) - OGG
        - Opus (libopus) - Opus
        - PCM (pcm_s16le) - WAV
        - FLAC (flac) - FLAC

        Compression ratios by bitrate:
        - 64k: 70-85% size reduction
        - 128k: 50-70% size reduction
        - 192k: 30-50% size reduction
        - 256k: 10-30% size reduction

        Parameters:
        -----------
            input_path(str): input file path
            ffmpeg_path(str): path to FFmpeg executable
            bitrate(str): target audio bitrate (e.g., "128k")
            timeout(int): timeout in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        input_format = Path(input_path).suffix.lstrip('.').lower()

        # Create temp output file
        output_path = CompressionRepository._create_temp_output_file(f'.{input_format}')

        # Build FFmpeg command
        cmd = [
            ffmpeg_path,
            '-i', input_path,
            '-y',
        ]

        if input_format == 'mp3':
            cmd.extend([
                '-c:a', 'libmp3lame',
                '-b:a', bitrate,
                '-q:a', '2',
            ])
        elif input_format in ['m4a', 'aac']:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', bitrate,
            ])
        elif input_format == 'ogg':
            cmd.extend([
                '-c:a', 'libvorbis',
                '-q:a', '4',  # Quality level (0-10)
            ])
        elif input_format == 'opus':
            cmd.extend([
                '-c:a', 'libopus',
                '-b:a', bitrate,
                '-vbr', 'on',
                '-compression_level', '10',
            ])
        elif input_format == 'wav':
            # WAV: PCM (LGPL, lossless)
            cmd.extend([
                '-c:a', 'pcm_s16le',
                '-ar', '44100',
            ])
        elif input_format == 'flac':
            cmd.extend([
                '-c:a', 'flac',
                '-compression_level', '8',
            ])
        elif input_format == 'wma':
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', bitrate,
            ])
        else:
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', bitrate,
            ])

        if input_format not in ['wav', 'flac']:  # Don't change sample rate for lossless
            cmd.extend([
                '-ar', '44100',
                '-ac', '2',
            ])

        cmd.append(output_path)

        start_time = time.perf_counter()

        if bitrate == "64k":
            compression_level = "low"
        elif bitrate == "128k":
            compression_level = "medium"
        else:
            compression_level = "high"

        try:
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
                raise ValueError(f"FFmpeg audio compression failed: {error_msg}")

            if not Path(output_path).exists():
                raise FileNotFoundError("Output file was not created")

            file_size = os.path.getsize(output_path)

            if file_size == 0:
                os.unlink(output_path)
                raise ValueError("The created file was empty")

        except subprocess.TimeoutExpired as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Audio compression timed out after {timeout} seconds") from e

        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise ValueError(f"Audio compression failed: {str(e)}") from e
        
        end_time = time.perf_counter()

        return {
            "OriginalFileName": Path(input_path).stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": input_path,
            "OutputFileName": Path(output_path).stem,
            "OutputFileSize": os.path.getsize(output_path),
            "OutputFilePath": output_path,
            "TaskStatus": (True if file_size != 0 else False),
            "CompressionLevel": compression_level,
            "TaskTime": end_time - start_time
        }
