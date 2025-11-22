"""
Conversion handler module
"""

import io
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.conversion_repository import ConversionRepository
from Repositories.conversion_history_repository import ConversionHistoryRepository
from Schemas.conversion import ConversionResponse

router = APIRouter()

@router.post("/convert_to/image/{out_format}", response_model=ConversionResponse)
async def convert_image_handler(
    out_format: str,
    filepath: str, # type: ignore
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StreamingResponse | None:
    """
    Mount a function to an endpoint, used to convert fileformat

    Parameter:
    ----------
    - out_format(str): output format of the target file
    - filepath(str): the path from the file in the local
    - current_user(User): the user want to use the service
    - db(Session): a session working with the database
    """

    print(filepath)

    # FE: kiem tra file co ton tai khong? co dung dinh dang input
    filepath: Path = Path(filepath)

    try:
        with open(filepath, "rb") as fp:
            file_content = fp.read()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(str(e))
        return None

    try:
        # Convert image (pure logic, no database)
        in_format, converted_bytes = await ConversionRepository().convert_image(file_content, out_format)
        new_filename: str = filepath.stem + f".{out_format}"
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e

    conversion_history_repo = ConversionHistoryRepository(db)

    await conversion_history_repo.record_conversion(
        user_id=current_user.UserID,
        input_format=in_format,
        output_format=out_format,
        original_filename=filepath.name,
        converted_filename=filepath.stem + f".{out_format}",
        file_size_bytes=file_content,
        converted_file_bytes=converted_bytes
    )

    return StreamingResponse(
        io.BytesIO(converted_bytes),
        media_type=f"image/{out_format.lower()}",
        headers={
            "Content-Disposition": f"attachment; filename={new_filename}",
            "Content-Length": str(len(converted_bytes))
        }
    )

@router.post("/convert_to/vid_au")
async def convert_video_audio(
    input_path: str,
    output_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Mount a function to an endpoint, convert audio and video

    Parameters:
    -----------
        input_path(str): the input path from the original file
        output_path(str): the output path to the converted file
        current_user(User): the user who use the service
        db(Session): the session with database

    Return:
    --------
        True if convert successfully else False
    """

    input_format = Path(input_path).suffix.lstrip('.').upper()
    output_format = Path(output_path).suffix.lstrip('.').upper()

    try:
        is_success = await ConversionRepository().convert_video_audio(input_path, output_path)

        if not is_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Conversion failed"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The request was bad: {str(e)}"
        ) from e 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        ) from e
    
    conversion_history_repo = ConversionHistoryRepository(db)
    try:
        original_file_size = os.path.getsize(input_path)
        converted_file_size = os.path.getsize(output_path)

        await conversion_history_repo.record_conversion(
            user_id=current_user.UserID,
            input_format=input_format,
            output_format=output_format,
            original_filename=Path(input_path).name,
            converted_filename=Path(output_path).name,
            file_size_bytes=original_file_size,
            converted_file_bytes=converted_file_size
        )
    except Exception as e:
        print(f"Failed to record conversion: {str(e)}")

    return {
        "success": "True",
        "message": "Conversion completed successfully",
        "output_path": output_path
    }
