"""
Conversion handler module with file streaming
"""

import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.conversion_repository import ConversionRepository
from Repositories.conversion_history_repository import ConversionHistoryRepository

router = APIRouter()

def cleanup_temp_file(filepath: str):
    """Delete temporary file after response is sent"""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
    except Exception as e:
        print(f"Failed to delete temp file {filepath}: {str(e)}")

@router.post("/convert_to/image/")
async def convert_image_handler(
    input_path: str,
    output_format: str,  # Just the format like "png", "jpg", etc.
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert image and return the converted file as download

    Parameters:
    ----------
    - input_path(str): the path of the input file
    - output_format(str): desired output format (e.g., "png", "jpg")
    """

    input_format = Path(input_path).suffix.lstrip('.').upper()
    output_format_upper = output_format.lstrip('.').upper()
    
    # Create temporary file for output
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=f'.{output_format.lower()}'
    ) as temp_file:
        output_path = temp_file.name

    try:
        # Convert image - returns (temp_file_path, file_size)
        output_path, converted_size = await ConversionRepository().convert_image(
            input_path, output_format
        )
            
    except ValueError as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e

    # Record conversion history
    conversion_history_repo = ConversionHistoryRepository(db)
    try:
        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=output_format_upper,
            original_filename=Path(input_path).name,
            converted_filename=f"{Path(input_path).stem}.{output_format.lower()}",
            file_size_bytes=os.path.getsize(input_path),
            converted_file_bytes=converted_size
        )
    except Exception as e:
        print(f"Failed to record: {str(e)}")

    # Generate download filename
    original_name = Path(input_path).stem
    download_filename = f"{original_name}.{output_format.lower()}"
    
    # Return file as download response
    return FileResponse(
        path=output_path,
        media_type=f"image/{output_format.lower()}",
        filename=download_filename,
        background=BackgroundTask(cleanup_temp_file, output_path)  # Cleanup after sending
    )


@router.post("/convert_to/vid_au")
async def convert_video_audio(
    input_path: str,
    output_format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert audio/video and return as downloadable file

    Parameters:
    -----------
    - input_path(str): the input path from the original file
    - output_format(str): desired output format (e.g., "mp4", "mp3")
    """

    input_format = Path(input_path).suffix.lstrip('.').upper()
    output_format_upper = output_format.lstrip('.').upper()
    
    # Create temporary file for output
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=f'.{output_format.lower()}'
    ) as temp_file:
        output_path = temp_file.name

    try:
        output_path, converted_size = await ConversionRepository().convert_video_audio(
            input_path, output_format, 300
        )
            
    except ValueError as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The request was bad: {str(e)}"
        ) from e
    except Exception as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e

    # Record conversion history
    conversion_history_repo = ConversionHistoryRepository(db)
    try:
        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=output_format_upper,
            original_filename=Path(input_path).name,
            converted_filename=f"{Path(input_path).stem}.{output_format.lower()}",
            file_size_bytes=os.path.getsize(input_path),
            converted_file_bytes=converted_size
        )
    except Exception as e:
        print(f"Failed to record conversion: {str(e)}")

    # Determine media type
    media_type = "video/mp4" if output_format.lower() in ['mp4', 'avi', 'mov', 'mkv', 'webm'] else "audio/mpeg"
    
    # Generate download filename
    original_name = Path(input_path).stem
    download_filename = f"{original_name}.{output_format.lower()}"

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=download_filename,
        background=BackgroundTask(cleanup_temp_file, output_path)
    )


@router.post('/convert_to/gif')
async def convert_gif(
    input_path: str,
    output_format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Convert to/from GIF and return as downloadable file

    Parameters:
    -----------
    - input_path(str): the input path from the original file
    - output_format(str): desired output format
    """

    input_format = Path(input_path).suffix.lstrip('.').upper()
    output_format_upper = output_format.lstrip('.').upper()
    
    # Create temporary file for output
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=f'.{output_format.lower()}'
    ) as temp_file:
        output_path = temp_file.name

    try:
        output_path, converted_size = await ConversionRepository().convert_gif(
            input_path, output_format, 300
        )
            
    except ValueError as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conversion failed: {str(e)}"
        ) from e
    except Exception as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e

    # Record conversion history
    conversion_history_repo = ConversionHistoryRepository(db)
    try:
        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=output_format_upper,
            original_filename=Path(input_path).name,
            converted_filename=f"{Path(input_path).stem}.{output_format.lower()}",
            file_size_bytes=os.path.getsize(input_path),
            converted_file_bytes=os.path.getsize(output_path)
        )
    except Exception as e:
        print(f"Failed to record conversion: {str(e)}")

    # Determine media type
    if output_format.lower() == 'gif':
        media_type = "image/gif"
    elif output_format.lower() in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
        media_type = "video/mp4"
    else:
        media_type = "image/png"
    
    # Generate download filename
    original_name = Path(input_path).stem
    download_filename = f"{original_name}.{output_format.lower()}"

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=download_filename,
        background=BackgroundTask(cleanup_temp_file, output_path)
    )


@router.post('/convert_to/pdf')
async def convert_pdf(
    input_path: str,
    output_format: str,
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

    input_format = Path(input_path).suffix.lstrip('.').upper()
    output_format_upper = output_format.lstrip('.').upper()
    
    # Create temporary file for output
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=f'.{output_format.lower()}'
    ) as temp_file:
        output_path = temp_file.name

    try:
        output_path, converted_size = await ConversionRepository().convert_pdf_office(
            input_path, output_format, 300
        )
            
    except ValueError as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conversion failed: {str(e)}"
        ) from e
    except Exception as e:
        cleanup_temp_file(output_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e

    # Record conversion history
    conversion_history_repo = ConversionHistoryRepository(db)
    try:
        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=output_format_upper,
            original_filename=Path(input_path).name,
            converted_filename=f"{Path(input_path).stem}.{output_format.lower()}",
            file_size_bytes=os.path.getsize(input_path),
            converted_file_bytes=os.path.getsize(output_path)
        )
    except Exception as e:
        print(f"Failed to record conversion: {str(e)}")

    # Determine media type
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
    
    # Generate download filename
    original_name = Path(input_path).stem
    download_filename = f"{original_name}.{output_format.lower()}"

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=download_filename,
        background=BackgroundTask(cleanup_temp_file, output_path)
    )