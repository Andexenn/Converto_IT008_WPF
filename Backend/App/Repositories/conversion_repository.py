"""
conversion_repository module
"""
import io
import time
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import subprocess
from typing import List, Tuple
import tempfile
import asyncio
import shutil

from sqlalchemy.orm import Session
from PIL import Image

from Services.conversion_service import IConversionService
from Schemas.task import TaskConversion
from Entities.tasks import Tasks

FFMPEG_EXECUTABLE_NAME = 'ffmpeg.exe'
SOFFICE_EXECUTABLE_NAME = 'soffice.exe'
SERVICETYPEID = 1

class ConversionRepository(IConversionService):
    """
    Conversion repository class
    """
    def __init__(self, db: Session, UserID: int):
        """
        Initialize with ffmpeg path
        """
        self.ffmpeg_path = self._get_ffmpeg_path
        self.max_workers = max(1, multiprocessing.cpu_count() - 1)
        self.soffice_path = self._get_soffice_path

        self.db = db
        self.user_id = UserID

    @property
    def _get_ffmpeg_path(self) -> str:
        """
        Get the ffmpeg path
        """
        ffmpeg_path = Path(__file__).parent.parent.parent.parent / 'bin' / 'Debug' / 'net9.0-windows' / FFMPEG_EXECUTABLE_NAME

        if not ffmpeg_path.exists():
            raise FileNotFoundError(
                f"FFmpeg executable not found. Please ensure {FFMPEG_EXECUTABLE_NAME} exists"
            )

        return str(ffmpeg_path.absolute())

    @property
    def _get_soffice_path(self) -> str:
        """
        Get soffice path
        """
        soffice_path = Path(__file__).parent.parent.parent.parent / 'bin' / 'Debug' / 'net9.0-windows' / SOFFICE_EXECUTABLE_NAME

        if not soffice_path.exists():
            raise FileNotFoundError(
                f"Soffice executable not found. Please ensure {SOFFICE_EXECUTABLE_NAME} exists"
            )

        return str(soffice_path)

    @staticmethod
    def _execute_subprocess(cmd: List) -> int:
        """
        Execute the ffmpeg with config statistic

        Parameter:
        ----------
            cmd(list): FFmpeg/soffice command as input
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

    @staticmethod
    async def _run_in_executor(func, *args):
        """Helper to run sync function in executor for single file processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    @staticmethod
    def _verify_path(input_path: str) -> None:
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

    @staticmethod
    def create_temp_output_file(suffix: str) -> str:
        """
        Create a temporary file

        Parameters:
        -----------
            suffix(str): file extension

        Returns:
        --------
            return the temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()
        return temp_file.name

    def _record_task(self, task:TaskConversion):
        """Record the task"""
        task_dict = task.model_dump(exclude_unset=True)
        cur_task = Tasks(**task_dict)
        self.db.add(cur_task)

        self.db.commit()

        return True


    #================ IMAGE ================

    async def convert_image(self, input_path: str, output_format: str) -> Tuple[str, int]:
        """
        Convert image from various types using Pillow
        Returns path to temporary output file and its size

        Parameters:
        ------------
            input_path(str): the path of the original file
            output_format(str): desired output format (e.g., 'png', 'jpg')

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
        -------
            Exception: if convert failed
        """

        self._verify_path(input_path)

        try:
            data = await self._run_in_executor(
                self._convert_image_sync,
                input_path,
                output_format
            )

            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                InputFormat=data["InputFormat"],
                OutputFormat=data["OutputFormat"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)
        
        except Exception as e:
            print(f"Failed to convert {input_path}: {str(e)}")
            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                OutputFormat=output_format.upper(),
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)

        return (str(task.OutputFilePath), int(task.OutputFileSize))


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
        if not input_paths:
            return []

        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_path = {
                executor.submit(
                    self._convert_image_sync,
                    input_path,
                    output_format
                ): input_path
                for input_path in input_paths
            }

            results = []
            # Collect results as they complete
            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result()

                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        InputFormat=data["InputFormat"],
                        OutputFormat=data["OutputFormat"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to convert {input_path}: {str(e)}")
                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                        OutputFormat=output_format.upper(),
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))

        return results

    @staticmethod
    def _convert_image_sync(input_path: str, output_format: str) -> dict:
        """
        Synchronous image conversion function for multiprocessing
        This is called by each worker process

        Parameters:
        -----------
            input_path(str): input file path
            output_format(str): desired output format (e.g., 'png', 'jpg')

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        try:
            with open(input_path, "rb") as fp:
                file_content = fp.read()
        except Exception as e:
            raise ValueError(f"Failed to read input file: {str(e)}") from e

        output_format = output_format.lstrip('.').lower()

        start_time = time.perf_counter()

        try:
            image = Image.open(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Failed to open input file: {str(e)}") from e

        # Handle transparency for JPEG
        if output_format in ['jpg', 'jpeg'] and image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode not in ["RGB", "RGBA"] and output_format not in ['png']:
            image = image.convert("RGB")

        # Create temp output file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        output_path = temp_file.name
        temp_file.close()

        try:
            image.save(output_path, format=output_format.upper(), optimize=True)
        except Exception as e:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ValueError(f"Failed to convert to {output_format.upper()}: {str(e)}") from e

        end_time = time.perf_counter()

        return {
            "OriginalFileName": Path(input_path).stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": input_path,
            "OutputFileName": Path(output_path).stem,
            "OutputFileSize": os.path.getsize(output_path),
            "OutputFilePath": output_path,
            "TaskStatus": (True if os.path.getsize(output_path) != 0 else False),
            "InputFormat": Path(input_path).suffix.lstrip('.').upper(),
            "OutputFormat": output_format,
            "TaskTime": end_time - start_time
        }

    #================ VIDEO & AUDIO ================

    async def convert_video_audio(self, input_path: str, output_format: str, timeout: int = 300) -> Tuple[str, int]:
        """
        Convert audio and video from various types using ffmpeg
        Returns path to temporary output file and its size

        Parameters:
        ------------
            input_path(str): the input file path
            output_format(str): desired output format (e.g., 'mp4', 'mp3')
            timeout(int): maximum time in seconds

        Returns:
        --------
            Tuple[str, int]: (output_file_path, file_size_bytes)

        Raises:
            ValueError: If conversion failed
            FileNotFoundError: If input file doesn't exist
        """

        try:
            data = await self._run_in_executor(
                self._convert_video_audio_sync,
                input_path,
                output_format,
                self.ffmpeg_path,
                timeout
            )

            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                InputFormat=data["InputFormat"],
                OutputFormat=data["OutputFormat"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)

        except Exception as e:
            print(f"Failed to convert {input_path}: {str(e)}")
            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                OutputFormat=output_format.upper(),
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)

        return (str(task.OutputFilePath), int(task.OutputFileSize))

    async def convert_video_audio_batch(self, input_paths: List[str], output_format: str, timeout: int = 300) -> List[Tuple[str, str, int, bool]]:
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
        if not input_paths:
            return []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._convert_video_audio_sync,
                    input_path,
                    output_format,
                    self.ffmpeg_path,
                    timeout
                ): input_path
                for input_path in input_paths
            }

            results = []
            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result()

                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        InputFormat=data["InputFormat"],
                        OutputFormat=data["OutputFormat"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                        OutputFormat=output_format.upper(),
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))

        return results


    @staticmethod
    def _convert_video_audio_sync(input_path: str, output_format: str, ffmpeg_path: str, timeout: int) -> dict:
        """
        Synchronous video/audio conversion for multiprocessing
        Used by both single and batch conversions
        """

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        output_format = output_format.lstrip('.').lower()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        output_path = temp_file.name
        temp_file.close()

        try:
            cmd = [ffmpeg_path, '-i', input_path, '-y']

            if output_format in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
                if output_format == 'webm':
                    cmd.extend(['-c:v', 'libvpx', '-b:v', '1M', '-c:a', 'libvorbis', '-b:a', '128k'])
                else:
                    cmd.extend(['-c:v', 'mpeg4', '-q:v', '5', '-c:a', 'aac', '-b:a', '128k'])

            elif output_format in ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a']:
                if output_format == 'mp3':
                    cmd.extend(['-vn', '-c:a', 'libmp3lame', '-b:a', '192k'])
                elif output_format == 'wav':
                    cmd.extend(['-vn', '-c:a', 'pcm_s16le', '-ar', '44100'])
                elif output_format == 'aac':
                    cmd.extend(['-vn', '-c:a', 'aac', '-b:a', '192k'])
                elif output_format == 'ogg':
                    cmd.extend(['-vn', '-c:a', 'libvorbis', '-q:a', '6'])
                elif output_format == 'flac':
                    cmd.extend(['-vn', '-c:a', 'flac', '-compression_level', '5'])
                elif output_format == 'm4a':
                    cmd.extend(['-vn', '-c:a', 'aac', '-b:a', '192k'])

            cmd.append(output_path)

            start_time = time.perf_counter()

            # Execute FFmpeg with timeout
            with multiprocessing.Pool(processes=1) as pool:
                result = pool.apply_async(ConversionRepository._execute_subprocess, (cmd,))
                return_code = result.get(timeout=timeout)

            if return_code != 0:
                raise ValueError("FFmpeg conversion failed")

            if not os.path.exists(output_path):
                raise FileNotFoundError("Output file not created")

            if os.path.getsize(output_path) == 0:
                raise ValueError("Output file is empty")

            end_time = time.perf_counter()

            return {
                "OriginalFileName": Path(input_path).stem,
                "OriginalFileSize": os.path.getsize(input_path),
                "OriginalFilePath": input_path,
                "OutputFileName": Path(output_path).stem,
                "OutputFileSize": os.path.getsize(output_path),
                "OutputFilePath": output_path,
                "TaskStatus": (True if os.path.getsize(output_path) != 0 else False),
                "InputFormat": Path(input_path).suffix.lstrip('.').upper(),
                "OutputFormat": output_format,
                "TaskTime": end_time - start_time
            }

        except Exception as e:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise

    #================ GIF ================
    async def convert_gif(self, input_path: str, output_format: str, timeout: int) -> Tuple[str, int]:
        """
        Convert GIF using FFmpeg

        Parameter:
        ----------
            input_path(str): contains the original file path
            output_format(str): desired output format
            timeout(int): timeout in second

        Return:
        -------
            Tuple[str, int]: (output_file_path, file_size_bytes)
        """

        try:
            data = await self._run_in_executor(
                self._convert_gif_sync,
                input_path,
                output_format,
                self.ffmpeg_path,
                timeout
            )

            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                InputFormat=data["InputFormat"],
                OutputFormat=data["OutputFormat"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)

        except Exception as e:
            print(f"Failed to convert {input_path}: {str(e)}")
            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                OutputFormat=output_format.upper(),
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)

        return (str(task.OutputFilePath), task.OutputFileSize or 0)

    async def convert_gif_batch(self, input_paths: List[str], output_format: str, timeout: int = 300) -> List[Tuple[str, str, int, bool]]:
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
        if not input_paths:
            return []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._convert_gif_sync,
                    input_path,
                    output_format,
                    self.ffmpeg_path,
                    timeout
                ) : input_path for input_path in input_paths
            }

            results = []
            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result()

                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        InputFormat=data["InputFormat"],
                        OutputFormat=data["OutputFormat"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)

                    results.append((task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True))
                except Exception as e:
                    print(f"Failed to compress {input_path}: {str(e)}")
                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                        OutputFormat=output_format.upper(),
                        TaskStatus=False,
                        TaskTime=0
                    )

                    self._record_task(task)
                    results.append((input_path, "", 0, False))

        return results

    @staticmethod
    def _convert_gif_sync(input_path: str, output_format: str, ffmpeg_path: str, timeout: int) -> dict:
        """
        Synchronous GIF conversion for multiprocessing
        Handles: GIF↔Image, GIF↔Video conversions
        """

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        input_format = Path(input_path).suffix.lstrip('.').lower()
        output_format = output_format.lstrip('.').lower()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        output_path = temp_file.name
        temp_file.close()

        try:
            cmd = [ffmpeg_path, '-i', input_path, '-y']

            # GIF to Image
            if input_format == "gif" and output_format in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "ppm", "pgm", "pbm", "tga"]:
                cmd.extend(['-vframes', '1'])
                if output_format in ['jpg', 'jpeg']:
                    cmd.extend(['-q:v', '2'])
                elif output_format == 'png':
                    cmd.extend(['-compression_level', '6'])
                elif output_format == 'webp':
                    cmd.extend(['-q:v', '90'])

            # Image to GIF
            elif input_format in ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "ppm", "pgm", "pbm", "tga"] and output_format == "gif":
                cmd.extend(['-t', '1', '-loop', '0'])

            # GIF to Video
            elif input_format == "gif" and output_format in ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "mpeg", "mpg", "ogv", "3gp"]:
                if output_format == 'webm':
                    cmd.extend([
                        '-c:v', 'libvpx',
                        '-b:v', '1M',
                        '-crf', '10',
                        '-pix_fmt', 'yuv420p',
                        '-auto-alt-ref', '0',
                    ])
                elif output_format == 'mp4':
                    cmd.extend([
                        '-c:v', 'mpeg4',
                        '-q:v', '5',
                        '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart',
                    ])
                elif output_format in ['avi', 'mkv', 'mov']:
                    cmd.extend(['-c:v', 'mpeg4', '-q:v', '5', '-pix_fmt', 'yuv420p'])
                elif output_format in ['mpeg', 'mpg']:
                    cmd.extend(['-c:v', 'mpeg2video', '-b:v', '2M', '-pix_fmt', 'yuv420p'])
                elif output_format == 'ogv':
                    cmd.extend(['-c:v', 'libtheora', '-q:v', '7'])
                elif output_format == '3gp':
                    cmd.extend(['-c:v', 'mpeg4', '-s', '176x144', '-b:v', '256k'])
                else:
                    cmd.extend(['-c:v', 'mpeg4', '-q:v', '5', '-pix_fmt', 'yuv420p'])

            # Video to GIF
            elif input_format in ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv", "mpeg", "mpg", "ogv", "3gp"] and output_format == "gif":
                cmd.extend([
                    '-vf', 'fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop', '0',
                ])

            else:
                raise ValueError(f"Unsupported conversion: {input_format} to {output_format}")

            cmd.append(output_path)

            start_time = time.perf_counter()

            # Execute FFmpeg with timeout
            with multiprocessing.Pool(processes=1) as pool:
                result = pool.apply_async(ConversionRepository._execute_subprocess, (cmd,))
                return_code = result.get(timeout=timeout)

            if return_code != 0:
                raise ValueError("FFmpeg conversion failed")

            if not os.path.exists(output_path):
                raise FileNotFoundError("Output file not created")

            if os.path.getsize(output_path) == 0:
                raise ValueError("Output file is empty")

            end_time = time.perf_counter()

            return {
                "OriginalFileName": Path(input_path).stem,
                "OriginalFileSize": os.path.getsize(input_path),
                "OriginalFilePath": input_path,
                "OutputFileName": Path(output_path).stem,
                "OutputFileSize": os.path.getsize(output_path),
                "OutputFilePath": output_path,
                "TaskStatus": (True if os.path.getsize(output_path) != 0 else False),
                "InputFormat": Path(input_path).suffix.lstrip('.').upper(),
                "OutputFormat": output_format,
                "TaskTime": end_time - start_time
            }

        #pylint: disable = unused-variable
        except Exception as e:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise

    #================ PDF & OFFICE ================

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
        self._verify_path(input_path)

        input_format = Path(input_path).suffix.lstrip('.').lower()
        output_format = output_format.lstrip('.').lower()

        try:
            data = await self._run_in_executor(
                self._convert_office_to_pdf_sync,
                input_path,
                self.soffice_path,
                timeout
            )

            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=data["OriginalFileName"],
                OriginalFileSize=data["OriginalFileSize"],
                OriginalFilePath=data["OriginalFilePath"],
                OutputFileName=data["OutputFileName"],
                OutputFileSize=data["OutputFileSize"],
                OutputFilePath=data["OutputFilePath"],
                InputFormat=data["InputFormat"],
                OutputFormat=data["OutputFormat"],
                TaskStatus=True,
                TaskTime=data["TaskTime"]
            )

            self._record_task(task)


        except Exception as e:
            print(f"Failed to convert {input_path}: {str(e)}")
            task = TaskConversion(
                UserID=self.user_id,
                ServiceTypeID=SERVICETYPEID,
                OriginalFileName=Path(input_path).stem,
                OriginalFileSize=os.path.getsize(input_path),
                OriginalFilePath=input_path,
                InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                OutputFormat=output_format.upper(),
                TaskStatus=False,
                TaskTime=0
            )

            self._record_task(task)
        return (str(task.OutputFilePath), task.OutputFileSize or 0)

    async def convert_pdf_office_batch(
        self,
        input_paths: List[str],
        output_format: str,
        timeout: int = 300
    ) -> List[Tuple[str, str, int, bool]]:
        """
        Batch convert multiple files SYNCHRONOUSLY (one at a time)
        
        No multiprocessing - processes each file sequentially
        More reliable for Office conversions

        Parameters:
        -----------
            input_paths (List[str]): List of input file paths
            output_format (str): Desired output format
            timeout (int): Timeout per file in seconds

        Returns:
        --------
            List[Tuple[str, str, int, bool]]: List of (input_path, output_path, size, success)
        """
        if not input_paths:
            return []

        results = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._convert_office_to_pdf_sync,
                    input_path,
                    self.soffice_path,
                    timeout
                ) : input_path for input_path in input_paths
            }
            results = []
            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    data = future.result()
                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=data["OriginalFileName"],
                        OriginalFileSize=data["OriginalFileSize"],
                        OriginalFilePath=data["OriginalFilePath"],
                        OutputFileName=data["OutputFileName"],
                        OutputFileSize=data["OutputFileSize"],
                        OutputFilePath=data["OutputFilePath"],
                        InputFormat=data["InputFormat"],
                        OutputFormat=data["OutputFormat"],
                        TaskStatus=True,
                        TaskTime=data["TaskTime"]
                    )

                    self._record_task(task)
                    results.append([task.OriginalFilePath, task.OutputFilePath, task.OutputFileSize, True])
                except Exception as e:
                    print(f"Failed to convert {input_path}: {str(e)}")
                    task = TaskConversion(
                        UserID=self.user_id,
                        ServiceTypeID=SERVICETYPEID,
                        OriginalFileName=Path(input_path).stem,
                        OriginalFileSize=os.path.getsize(input_path),
                        OriginalFilePath=input_path,
                        InputFormat=Path(input_path).suffix.lstrip('.').upper(),
                        OutputFormat=output_format.upper(),
                        TaskStatus=False,
                        TaskTime=0
                    )
                    self._record_task(task)
                    results.append([task.OriginalFilePath, None, 0, False])
        
        return results

    @staticmethod
    def _convert_office_to_pdf_sync(input_path: str, soffice_path: str, timeout: int = 300) -> dict:
        """
        Convert from office to PDF using LibreOffice (headless)
        """
        # 1. Validate 

        if soffice_path is None:
            raise ValueError("soffice_path cannot be None. Please provide the path to LibreOffice executable.")
    
        if not os.path.exists(soffice_path):
            raise FileNotFoundError(f"LibreOffice executable not found at: {soffice_path}")

        input_path_obj = Path(input_path)
        if not input_path_obj.exists():
            raise FileNotFoundError(f"File {input_path} not found!")

        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {input_path}")

        start_time = time.perf_counter()

        # 2. Tạo nơi chứa file kết quả cuối cùng (Persistent Temp File)
        # Chúng ta tạo một file giữ chỗ để sau khi convert xong sẽ move data vào đây.
        final_output_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        final_output_path = final_output_temp.name
        final_output_temp.close()

        try:
            # 3. Sử dụng TemporaryDirectory để làm môi trường chạy (Sandbox)
            # Điều này giúp tự động dọn dẹp các file rác của LibreOffice sau khi chạy xong
            with tempfile.TemporaryDirectory() as temp_run_dir:
                
                # Cấu hình UserProfile riêng biệt cho process này để tránh lỗi "Lock file"
                user_profile_path = Path(temp_run_dir) / "user_profile"
                # Lưu ý: Cú pháp file:/// cần đúng chuẩn URI
                user_installation_arg = f"-env:UserInstallation=file:///{user_profile_path.as_posix()}"

                cmd = [
                    "soffice",
                    user_installation_arg,  # Quan trọng: Chạy profile độc lập
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", temp_run_dir, # Output tạm thời vào thư mục này
                    str(input_path)
                ]

                # 4. Thực thi lệnh (Thay thế multiprocessing)
                result = subprocess.run(
                    cmd,
                    capture_output=True, # Bắt log stdout/stderr
                    text=True,
                    timeout=timeout,
                    check=False
                )

                if result.returncode != 0:
                    # Gộp stderr vào lỗi để debug dễ hơn
                    raise ValueError(f"Soffice conversion failed (Code {result.returncode}): {result.stderr}")

                # 5. Xác định file PDF do LibreOffice sinh ra
                # LibreOffice giữ nguyên tên file gốc, chỉ đổi đuôi. Ví dụ: abc.docx -> abc.pdf
                original_stem = input_path_obj.stem
                expected_temp_pdf = Path(temp_run_dir) / f"{original_stem}.pdf"

                if not expected_temp_pdf.exists():
                    raise FileNotFoundError(f"Conversion finished but output file not found at {expected_temp_pdf}")
                
                if expected_temp_pdf.stat().st_size == 0:
                    raise ValueError("Generated PDF file is empty")

                # 6. Di chuyển file kết quả từ thư mục tạm sang file đích cuối cùng
                shutil.move(str(expected_temp_pdf), final_output_path)

        except subprocess.TimeoutExpired:
            # Dọn dẹp file output rỗng nếu timeout
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            raise TimeoutError(f"Soffice conversion timed out after {timeout}s")
            
        except Exception as e:
            # Dọn dẹp file output rỗng nếu có lỗi
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            raise ValueError(f"Conversion process error: {str(e)}") from e

        end_time = time.perf_counter()
        
        # Lấy kích thước file cuối cùng
        final_size = os.path.getsize(final_output_path)

        return {
            "OriginalFileName": input_path_obj.stem,
            "OriginalFileSize": os.path.getsize(input_path),
            "OriginalFilePath": str(input_path),
            "OutputFileName": Path(final_output_path).stem, # Tên file temp (ngẫu nhiên)
            "OutputFileSize": final_size,
            "OutputFilePath": final_output_path,
            "TaskStatus": (True if final_size > 0 else False),
            "InputFormat": input_path_obj.suffix.lstrip('.').upper(),
            "OutputFormat": 'pdf',
            "TaskTime": end_time - start_time
        }

    @staticmethod
    def _convert_pdf_to_office_sync(input_path: str, output_format: str, soffice_path: str , timeout: int = 300) -> Tuple[str, int]:
        """Convert from pdf to office"""

        if not Path(input_path).exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        output_format = output_format.lstrip('.').lower()

        format_to_filter = {
            'docx': 'docx',
            'doc':  'doc',
            'xlsx': 'xlsx',
            'xls':  'xls',
            'pptx': 'pptx',
            'ppt':  'ppt',
        }

        if output_format not in format_to_filter:
            raise ValueError(f"Unsupported convert from PDF to {output_format}")

        libreoffice_filter = format_to_filter[output_format]

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        output_path = temp_file.name
        temp_file.close()

        try:
            cmd = [
                "soffice",
                "--headless",
                "--invisible",
                "--nocrashreport",
                "--nodefault",
                "--nofirststartwizard",
                "--nologo",
                "--norestore",
                '--convert-to', libreoffice_filter,
                output_path,
                '--outdir', str(Path(output_path).parent),
                str(input_path)
            ]

            with multiprocessing.Pool(processes=1) as pool:
                result = pool.apply_async(ConversionRepository._execute_subprocess, (cmd, ))
                return_code = result.get(timeout=timeout)

            if return_code != 0:
                raise ValueError("Soffice conversion failed")

            if not os.path.exists(output_path):
                raise FileNotFoundError("Output file not created")

            if os.path.getsize(output_path) == 0:
                raise ValueError("Output file is empty")

            file_size = os.path.getsize(output_path)
            return output_path, file_size

        #pylint: disable=unused-variable
        except Exception as e:
            if Path(output_path).exists():
                os.unlink(output_path)
            raise