from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.ConvertRepositories.image_converter_repositories import ImageConverterRepositories
from Repositories.ConvertRepositories.conversion_repositories import ConversionRepositories
from Schemas.conversion import ConversionResponse

router = APIRouter()

@router.post("/webp-to-png", response_model=ConversionResponse)
async def convert_webp_to_png(
    file: UploadFile = File(..., description="WEBP to PNG converter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate file
        if not file.filename.lower().endswith('.webp'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only WEBP files are supported"
            )
        
        # Read file
        file_content = await file.read()
        
        # Convert image (pure logic, no database)
        image_converter = ImageConverterRepositories()
        converted_bytes, new_filename = await image_converter.convert_webp_to_png(
            file_content, 
            file.filename
        )
        
        # Record in database (repository handles everything)
        conversion_repo = ConversionRepositories(db)
        response, _ = await conversion_repo.record_conversion(
            user_id=current_user.UserID,
            input_format="WEBP",
            output_format="PNG",
            original_filename=file.filename,
            converted_filename=new_filename,
            file_size_bytes=len(converted_bytes),
            converted_file_bytes=converted_bytes
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )

@router.post("/webp-to-png/download")
async def download_webp_to_png(
    file: UploadFile = File(..., description="WEBP file to convert and download"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convert WEBP to PNG and return the PNG file directly
    Returns actual PNG file for download
    """
    try:
        # Validate file
        if not file.filename.lower().endswith('.webp'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only WEBP files are supported"
            )
        
        # Read file
        file_content = await file.read()
        
        # Convert image
        image_converter = ImageConverterRepositories()
        converted_bytes, new_filename = await image_converter.convert_webp_to_png(
            file_content, 
            file.filename
        )
        
        # Record in database
        conversion_repo = ConversionRepositories(db)
        _, file_bytes = await conversion_repo.record_conversion(
            user_id=current_user.UserID,
            input_format="WEBP",
            output_format="PNG",
            original_filename=file.filename,
            converted_filename=new_filename,
            file_size_bytes=len(converted_bytes),
            converted_file_bytes=converted_bytes
        )
        
        # Return actual PNG file
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={new_filename}",
                "Content-Length": str(len(file_bytes))
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )
