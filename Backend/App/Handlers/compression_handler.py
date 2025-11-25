"""
Compression handler module with file streaming
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
from Repositories.compression_repository import CompressionRepository
from Repositories.conversion_history_repository import ConversionHistoryRepository

router = APIRouter()

def cleanup_temp_file(filepath: str):
    """Delete temporary file after response is sent"""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
    except Exception as e:
        print(f"Failed to delete temp file {filepath}: {str(e)}")


@router.post("/compress/image")
async def compress_image(
    input_path: str,
    reduce_colors: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Compress image and return the compressed file as download
    
    The output will keep the same format as input (PNG stays PNG, JPEG stays JPEG)

    Parameters:
    ----------
    - input_path(str): the path of the input file
    - reduce_colors(bool): whether to reduce colors for PNG (better compression)
    """

    input_format = Path(input_path).suffix.lstrip('.').upper()
    
    # Create temporary file for output with same extension
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=Path(input_path).suffix
    ) as temp_file:
        output_path = temp_file.name

    try:
        output_path, compressed_size = await CompressionRepository().compress_image(
            input_path, reduce_colors
        )
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError("Compression succeeded but output file not found")
            
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
            detail=f"Compression failed: {str(e)}"
        ) from e

    # Record compression history
    conversion_history_repo = ConversionHistoryRepository(db)
    
    original_size = os.path.getsize(input_path)
    
    try:
        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=input_format,  # Same format
            original_filename=Path(input_path).name,
            converted_filename=f"{Path(input_path).stem}_compressed{Path(input_path).suffix}",
            file_size_bytes=original_size,
            converted_file_bytes=compressed_size
        )
    except Exception as e:
        print(f"Failed to record: {str(e)}")

    # Calculate compression ratio
    compression_ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
    
    # Generate download filename
    original_name = Path(input_path).stem
    download_filename = f"{original_name}_compressed{Path(input_path).suffix}"
    
    # Determine media type based on format
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
    
    # Return file as download response with compression info in headers
    response = FileResponse(
        path=output_path,
        media_type=media_type,
        filename=download_filename,
        background=BackgroundTask(cleanup_temp_file, output_path)
    )
    
    # Add custom headers with compression info
    response.headers["X-Original-Size"] = str(original_size)
    response.headers["X-Compressed-Size"] = str(compressed_size)
    response.headers["X-Compression-Ratio"] = f"{compression_ratio:.2f}%"
    
    return response