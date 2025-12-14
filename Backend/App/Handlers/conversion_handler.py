"""
Conversion handler module with file streaming
"""

import os
import tempfile
import zipfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.conversion_repository import ConversionRepository
router = APIRouter()

def cleanup_temp_file(filepath: str):
    """Delete temporary file after response is sent"""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
    except Exception as e:
        print(f"Failed to delete temp file {filepath}: {str(e)}")

def cleanup_temp_files(filepaths: List[str]):
    """Delete all temporary files after reponse is sent"""
    for filepath in filepaths:
        cleanup_temp_file(filepath)


@router.post("/convert_to/image/")
async def convert_image_handler(
    input_paths: List[str] = Body(..., alias="input_paths"),
    output_format: str = Body(..., alias="output_format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert image(s) - works for single or multiple files

    Parameters:
    ----------
    - input_paths(List[str]): list of input file paths (can be 1 or many)
    - output_format(str): desired output format (e.g., "png", "jpg")

    Returns:
    --------
    - Single file: Returns the converted file directly
    - Multiple files: Returns ZIP file with all converted files

    Example Requests:
    ----------------
    # Single image
    POST /convert/image
    {
        "input_paths": ["/path/to/image.bmp"],
        "output_format": "png"
    }

    # Multiple images
    POST /convert/image
    {
        "input_paths": [
            "/path/to/image1.bmp",
            "/path/to/image2.tiff",
            "/path/to/image3.webp"
        ],
        "output_format": "jpg"
    }
    """

    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed when convert images"
        )

    if len(input_paths) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fail because send too much files"
        )


    is_single_file = len(input_paths) == 1
    input_format = Path(input_paths[0]).suffix.lstrip('.').upper()
    output_format_upper = output_format.lstrip('.').upper()

    try:
        conversion_repo = ConversionRepository(db, current_user.UserID)

        if is_single_file:
            output_path, converted_file_size = await conversion_repo.convert_image(input_paths[0], output_format)
            results = [(input_paths[0], output_path, converted_file_size, True)]
        else:
            results = await conversion_repo.convert_images_batch(input_paths, output_format)

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]

        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All the conversions failed"
            )

        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)


        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}.{output_format.lower()}"

            response = FileResponse(
                path=output_path,
                media_type=f"image/{output_format.lower()}",
                filename=download_filename,
                background=BackgroundTask(cleanup_temp_file, output_path)
            )

            # Add statistics headers
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
                    for input_path, output_path, converted_size, success in successful_results:
                        original_filename = Path(input_path).stem
                        converted_filename = f"{original_filename}.{output_format.lower()}"
                        zipf.write(output_path, converted_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f'converted_images_{output_format.lower()}.zip',
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
            detail=f"Conversion failed: {str(e)}"
        ) from e

@router.post("/convert_to/video_audio")
async def convert_video_audio(
    input_paths: List[str] = Body(..., alias="input_paths"),
    output_format: str = Body(..., alias="output_format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert video/audio file(s) - works for single or multiple files

    Parameters:
    ----------
    - input_paths(List[str]): list of input file paths (can be 1 or many)
    - output_format(str): desired output format (e.g., "mp4", "mp3")

    Returns:
    --------
    - Single file: Returns the converted file directly
    - Multiple files: Returns ZIP file with all converted files

    Example:
    --------
    # Single video
    POST /convert/video_audio
    {
        "input_paths": ["/path/to/video.avi"],
        "output_format": "mp4"
    }

    # Multiple audio files
    POST /convert/video_audio
    {
        "input_paths": [
            "/path/to/audio1.wav",
            "/path/to/audio2.flac",
            "/path/to/audio3.ogg"
        ],
        "output_format": "mp3"
    }
    """

    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input paths provided"
        )

    if len(input_paths) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 video/audio files per request"
        )

    is_single_file = len(input_paths) == 1
    output_format_upper = output_format.lstrip('.').upper()

    try:
        conversion_repo = ConversionRepository(db, current_user.UserID)

        if is_single_file:
            # Single file - use direct method
            output_path, converted_size = await conversion_repo.convert_video_audio(
                input_paths[0], output_format, 300
            )
            results = [(input_paths[0], output_path, converted_size, True)]
        else:
            # Multiple files - use batch method with multiprocessing
            results = await conversion_repo.convert_video_audio_batch(
                input_paths, output_format, 300
            )

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]

        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All conversions failed"
            )



        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)

        # SINGLE FILE: Return file directly
        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}.{output_format.lower()}"

            # Determine media type
            media_type = "video/mp4" if output_format.lower() in ['mp4', 'avi', 'mov', 'mkv', 'webm'] else "audio/mpeg"

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

        # MULTIPLE FILES: Create and return ZIP
        else:
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, converted_size, success in successful_results:
                        original_filename = Path(input_path).stem
                        converted_filename = f"{original_filename}.{output_format.lower()}"
                        zipf.write(output_path, converted_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f'converted_files_{output_format.lower()}.zip',
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
            detail=f"Conversion failed: {str(e)}"
        ) from e


@router.post("/convert_to/gif")
async def convert_gifs(
    input_paths: List[str] = Body(..., alias="input_paths"),
    output_format: str = Body(..., alias="output_format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert GIF to/from other formats - works for single or multiple files

    Supports:
    - GIF → Image (PNG, JPG, WebP, etc.)
    - Image → GIF
    - GIF → Video (MP4, WebM, AVI, etc.)
    - Video → GIF

    Parameters:
    ----------
    - input_paths(List[str]): list of input file paths (can be 1 or many)
    - output_format(str): desired output format (e.g., "gif", "mp4", "png")
    """

    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input paths provided"
        )

    if len(input_paths) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 files per request"
        )

    is_single_file = len(input_paths) == 1
    output_format_upper = output_format.lstrip('.').upper()

    try:
        conversion_repo = ConversionRepository(db, current_user.UserID)

        if is_single_file:
            # Single file - use direct method
            output_path, converted_size = await conversion_repo.convert_gif(
                input_paths[0], output_format, 300
            )
            results = [(input_paths[0], output_path, converted_size, True)]
        else:
            # Multiple files - use batch method with multiprocessing
            results = await conversion_repo.convert_gif_batch(
                input_paths, output_format, 300
            )

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]

        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All conversions failed"
            )



        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)

        # SINGLE FILE: Return file directly
        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}.{output_format.lower()}"

            if output_format.lower() == 'gif':
                media_type = "image/gif"
            elif output_format.lower() in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
                media_type = "video/mp4"
            else:
                media_type = "image/png"

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

        # MULTIPLE FILES: Create and return ZIP
        else:
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, converted_size, _ in successful_results:
                        original_filename = Path(input_path).stem
                        converted_filename = f"{original_filename}.{output_format.lower()}"
                        zipf.write(output_path, converted_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f'converted_files_{output_format.lower()}.zip',
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
            detail=f"Conversion failed: {str(e)}"
        ) from e



@router.post('/convert_to/pdf')
async def convert_pdf(
    input_paths: List[str] = Body(..., alias="input_paths"),
    output_format: str = Body(..., alias="output_format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert to/from PDF and return as downloadable file

    Parameters:
    -----------
    - input_path(str): the input path from the original file
    - output_format(str): desired output format (e.g., "pdf", "docx")
    """

    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input paths provided"
        )

    if len(input_paths) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 files per request"
        )

    output_format_upper = output_format.lstrip('.').upper()
    is_single_file = len(input_paths) == 1


    conversion_repo = ConversionRepository(db, current_user.UserID)

    try:
        if is_single_file:
            output_path, file_converted_size = await conversion_repo.convert_pdf_office(
                input_paths[0], output_format, 300
            )
            results = [(input_paths[0], output_path, file_converted_size, True)]
        else:
            results = await conversion_repo.convert_pdf_office_batch(input_paths, output_format, 300)

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]

        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All conversions failed"
            )


        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)

        # SINGLE FILE: Return file directly
        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}.{output_format.lower()}"

            media_types = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'doc': 'application/msword',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'xls': 'application/vnd.ms-excel',
                'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'ppt': 'application/vnd.ms-powerpoint'
            }

            media_type = media_types.get(output_format.lower(), 'application/octet-stream')

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

        # MULTIPLE FILES: Create and return ZIP
        else:
            zip_path = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
            temp_files_to_cleanup = [output_path for _, output_path, _, _ in successful_results]
            temp_files_to_cleanup.append(zip_path)

            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for input_path, output_path, converted_size, _ in successful_results:
                        original_filename = Path(input_path).stem
                        converted_filename = f"{original_filename}.{output_format.lower()}"
                        zipf.write(output_path, converted_filename)

                response = FileResponse(
                    path=zip_path,
                    media_type='application/zip',
                    filename=f'converted_files_{output_format.lower()}.zip',
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
            detail=f"Conversion failed: {str(e)}"
        ) from e
