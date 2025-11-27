"""
Compression handler module with file streaming
"""

import os
import tempfile
from pathlib import Path
import zipfile
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.compression_repository import CompressionRepository

router = APIRouter()

def cleanup_temp_file(filepath: str):
    """Delete temporary file after response is sent"""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
    except Exception as e:
        print(f"Failed to delete temp file {filepath}: {str(e)}")

def cleanup_temp_files(filepaths: List[str]):
    for filepath in filepaths:
        cleanup_temp_file(filepath)

@router.post("/compress/image")
async def compress_image(
    input_paths: List[str] = Body(...),
    quality: int = Body(85),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Compress image and return the compressed file as download
    
    The output will keep the same format as input (PNG stays PNG, JPEG stays JPEG)

    Parameters:
    ----------
    - input_paths(List[str]): the path of the input files
    - reduce_colors(bool): whether to reduce colors for PNG (better compression)
    """

    if not input_paths:
        raise FileNotFoundError("File not found!")
    
    if len(input_paths) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too much files"
        )

    input_format = Path(input_paths[0]).suffix.lstrip('.').upper()
    is_single_file = len(input_paths) == 1

    compression_repo = CompressionRepository()

    try:
        if is_single_file:
            output_path, compressed_file_size = await compression_repo.compress_image(input_paths[0], quality, 300)
            results = [(input_paths[0], output_path, compressed_file_size, True)]
        else:
            results = await compression_repo.compress_images_batch(input_paths, quality, 300)

        successful_results = [r for r in results if r[3]]  
        failed_results = [r for r in results if not r[3]]  
        
        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All compressions failed"
            )
        
        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)

        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}_compressed.{input_format.lower()}"

            media_types = {
                'PNG': 'image/png',
                'JPG': 'image/jpeg',
                'JPEG': 'image/jpeg',
                'WEBP': 'image/webp',
                'GIF': 'image/gif',
                'BMP': 'image/bmp',
                'TIFF': 'image/tiff'
            }
            
            media_type = media_types.get(input_format, 'image/png')

            response = FileResponse(
                path=output_path,
                media_type=media_type,
                filename=download_filename,
                background=BackgroundTask(cleanup_temp_file, output_path)
            )
            
            response.headers["X-Total-Files"] = "1"
            response.headers["X-Failed-Files"] = str(len(failed_results))
            response.headers["X-Total-Original-Size"] = str(total_original_size)
            response.headers["X-Total-Converted-Size"] = str(total_converted_size)
            
            return response
        
        else:
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, compressed_file_size, _ in successful_results:
                        original_filename = Path(input_path).stem 
                        converted_filename = f"{original_filename}_compressed.{input_format.lower()}"
                        zipf.write(output_path, converted_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f"compressed_files_{input_format.lower()}.zip",
                    background=BackgroundTask(cleanup_temp_files, temp_files_to_cleanup)
                )

                response.headers["X-Total-Files"] = str(len(successful_results))
                response.headers["X-Failed-Files"] = str(len(failed_results))
                response.headers["X-Total-Original-Size"] = str(total_original_size)
                response.headers["X-Total-Converted-Size"] = str(total_converted_size)
                
                return response
                
            except Exception as e:
                cleanup_temp_files(temp_files_to_cleanup)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create ZIP file: {str(e)}"
                ) from e
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compression failed: {str(e)}"
        ) from e

@router.post("/compress/video")
async def compress_video(
    input_paths: List[str] = Body(...),
    quality: str = Body("medium"),  # "low", "medium", "high"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Compress video files and return as download
    
    Quality presets:
    - "low": Aggressive compression (60-80% reduction)
    - "medium": Balanced compression (40-60% reduction)
    - "high": Light compression (20-40% reduction)

    Parameters:
    -----------
        input_paths(List[str]): paths to input video files
        quality(str): compression quality preset
    """
    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input files provided"
        )
    
    if len(input_paths) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many files (max 20)"
        )

    if quality not in ["low", "medium", "high"]:
        quality = "medium"

    input_format = Path(input_paths[0]).suffix.lstrip('.').lower()
    is_single_file = len(input_paths) == 1

    compression_repo = CompressionRepository()

    try:
        if is_single_file:
            output_path, compressed_size = await compression_repo.compress_video(
                input_paths[0], quality, 600
            )
            results = [(input_paths[0], output_path, compressed_size, True)]
        else:
            results = await compression_repo.compress_videos_batch(
                input_paths, quality, 600
            )

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]
        
        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All video compressions failed"
            )
        
        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_compressed_size = sum(r[2] for r in successful_results)

        if is_single_file and successful_results:
            input_path, output_path, compressed_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}_compressed.{input_format}"

            media_types = {
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'avi': 'video/x-msvideo',
                'mkv': 'video/x-matroska',
                'webm': 'video/webm',
                'flv': 'video/x-flv',
                'wmv': 'video/x-ms-wmv'
            }
            
            media_type = media_types.get(input_format, 'video/mp4')

            response = FileResponse(
                path=output_path,
                media_type=media_type,
                filename=download_filename,
                background=BackgroundTask(cleanup_temp_file, output_path)
            )
            
            response.headers["X-Total-Files"] = "1"
            response.headers["X-Failed-Files"] = str(len(failed_results))
            response.headers["X-Total-Original-Size"] = str(total_original_size)
            response.headers["X-Total-Compressed-Size"] = str(total_compressed_size)
            response.headers["X-Compression-Ratio"] = f"{(1 - total_compressed_size/total_original_size)*100:.1f}%"
            
            return response
        
        else:
            # Multiple files - create ZIP
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, _, _ in successful_results:
                        original_filename = Path(input_path).stem
                        compressed_filename = f"{original_filename}_compressed.{input_format}"
                        zipf.write(output_path, compressed_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f"compressed_videos_{quality}.zip",
                    background=BackgroundTask(cleanup_temp_files, temp_files_to_cleanup)
                )

                response.headers["X-Total-Files"] = str(len(successful_results))
                response.headers["X-Failed-Files"] = str(len(failed_results))
                response.headers["X-Total-Original-Size"] = str(total_original_size)
                response.headers["X-Total-Compressed-Size"] = str(total_compressed_size)
                response.headers["X-Compression-Ratio"] = f"{(1 - total_compressed_size/total_original_size)*100:.1f}%"
                
                return response
                
            except Exception as e:
                cleanup_temp_files(temp_files_to_cleanup)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create ZIP file: {str(e)}"
                ) from e
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video compression failed: {str(e)}"
        ) from e


@router.post("/compress/audio")
async def compress_audio(
    input_paths: List[str] = Body(...),
    bitrate: str = Body("128k"),  # "64k", "128k", "192k", "256k"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Compress audio files and return as download
    
    Bitrate options:
    - "64k": Aggressive compression (70-85% reduction)
    - "128k": Balanced compression (50-70% reduction)
    - "192k": Light compression (30-50% reduction)
    - "256k": Minimal compression (10-30% reduction)

    Parameters:
    -----------
        input_paths(List[str]): paths to input audio files
        bitrate(str): target audio bitrate
    """
    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input files provided"
        )
    
    if len(input_paths) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many files (max 50)"
        )

    # Validate bitrate
    valid_bitrates = ["64k", "96k", "128k", "160k", "192k", "256k", "320k"]
    if bitrate not in valid_bitrates:
        bitrate = "128k"

    input_format = Path(input_paths[0]).suffix.lstrip('.').lower()
    is_single_file = len(input_paths) == 1

    compression_repo = CompressionRepository()

    try:
        if is_single_file:
            output_path, compressed_size = await compression_repo.compress_audio(
                input_paths[0], bitrate, 300
            )
            results = [(input_paths[0], output_path, compressed_size, True)]
        else:
            results = await compression_repo.compress_audios_batch(
                input_paths, bitrate, 300
            )

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]
        
        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All audio compressions failed"
            )
        
        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_compressed_size = sum(r[2] for r in successful_results)

        if is_single_file and successful_results:
            input_path, output_path, compressed_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}_compressed.{input_format}"

            media_types = {
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'ogg': 'audio/ogg',
                'flac': 'audio/flac',
                'm4a': 'audio/mp4',
                'aac': 'audio/aac',
                'opus': 'audio/opus',
                'wma': 'audio/x-ms-wma'
            }
            
            media_type = media_types.get(input_format, 'audio/mpeg')

            response = FileResponse(
                path=output_path,
                media_type=media_type,
                filename=download_filename,
                background=BackgroundTask(cleanup_temp_file, output_path)
            )
            
            response.headers["X-Total-Files"] = "1"
            response.headers["X-Failed-Files"] = str(len(failed_results))
            response.headers["X-Total-Original-Size"] = str(total_original_size)
            response.headers["X-Total-Compressed-Size"] = str(total_compressed_size)
            response.headers["X-Compression-Ratio"] = f"{(1 - total_compressed_size/total_original_size)*100:.1f}%"
            response.headers["X-Bitrate"] = bitrate
            
            return response
        
        else:
            # Multiple files - create ZIP
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, _, _ in successful_results:
                        original_filename = Path(input_path).stem
                        compressed_filename = f"{original_filename}_compressed.{input_format}"
                        zipf.write(output_path, compressed_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f"compressed_audio_{bitrate}.zip",
                    background=BackgroundTask(cleanup_temp_files, temp_files_to_cleanup)
                )

                response.headers["X-Total-Files"] = str(len(successful_results))
                response.headers["X-Failed-Files"] = str(len(failed_results))
                response.headers["X-Total-Original-Size"] = str(total_original_size)
                response.headers["X-Total-Compressed-Size"] = str(total_compressed_size)
                response.headers["X-Compression-Ratio"] = f"{(1 - total_compressed_size/total_original_size)*100:.1f}%"
                response.headers["X-Bitrate"] = bitrate
                
                return response
                
            except Exception as e:
                cleanup_temp_files(temp_files_to_cleanup)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create ZIP file: {str(e)}"
                ) from e
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio compression failed: {str(e)}"
        ) from e