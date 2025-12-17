import os 
import zipfile 
import tempfile 
from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.remove_background_repository import RemoveBackgroundRepository
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

@router.post('/remove_background')
async def remove_background_handler(
    input_paths: List[str] = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Remove background of the image
    """

    if not input_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed when remove background"
        )
    
    if len(input_paths) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fail because send too much files"
        )
    
    is_single_file = len(input_paths) == 1
    input_format = Path(input_paths[0]).suffix.lstrip('.').upper()
    
    try:
        remove_background_repo = RemoveBackgroundRepository(db, current_user.UserID)

        if is_single_file:
            output_path, converted_file_size = await remove_background_repo.remove_background(input_paths[0])
            results = [(input_paths[0], output_path, converted_file_size, True)]
        else:
            results = await remove_background_repo.remove_backgrounds_batch(input_paths)

        successful_results = [r for r in results if r[3]]
        failed_results = [r for r in results if not r[3]]

        if not successful_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="All the conversions failed"
            )
        total_original_size = sum(os.path.getsize(r[0]) for r in successful_results)
        total_converted_size = sum(r[2] for r in successful_results)

        output_format = input_format

        if is_single_file and successful_results:
            input_path, output_path, converted_size, _ = successful_results[0]
            original_name = Path(input_path).stem
            download_filename = f"{original_name}_removedbg.{output_format.lower()}"
            
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
                        converted_filename = f"{original_filename}_removedbg.{output_format.lower()}"
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