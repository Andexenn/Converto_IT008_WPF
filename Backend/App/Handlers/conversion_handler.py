"""
Conversion handler module
"""

import io
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

@router.post("/convert_to/{out_format}/{filepath}", response_model=ConversionResponse)
async def convert_handler(
    out_format: str,
    filepath: str, # type: ignore
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StreamingResponse | None:
    """
    Mount a function to an endpoint, use to convert fileformat

    Parameter:
    ----------
    out_format(str): output format of the target file
    filepath(str): the path from the file in the local
    current_user(User): the user want to use the service
    db(Session): a session working with the database
    """
    # TODO: check current user

    filepath = r"D:\Downloads\1.webp"
    in_format: str = filepath.rsplit('.', maxsplit=1)[-1]

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
        converted_bytes = await ConversionRepository().convert(file_content, out_format)
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

    # TODO: db log history
    conversion_repo = ConversionHistoryRepository(db)

    _, _ = await conversion_repo.record_conversion(
        user_id=current_user.UserID,
        input_format=in_format,
        output_format=out_format,
        original_filename=filepath.stem + f".{in_format}",
        converted_filename=filepath.stem + f".{out_format}",
        file_size_bytes=file_content,
        converted_file_bytes=converted_bytes
    )

    return StreamingResponse(
        io.BytesIO(converted_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={new_filename}",
            "Content-Length": str(len(file_content))
        }
    )
