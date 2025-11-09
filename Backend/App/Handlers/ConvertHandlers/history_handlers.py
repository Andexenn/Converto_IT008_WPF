from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.ConvertRepositories.conversion_repositories import ConversionRepository
from Schemas.conversion import ConversionHistoryWithServiceResponse

router = APIRouter()

@router.get("/history", response_model=list[ConversionHistoryWithServiceResponse])
async def get_my_conversion_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's conversion history"""
    conversion_repo = ConversionRepository(db)
    histories = await conversion_repo.get_user_conversion_history(
        user_id=current_user.UserID,
        limit=limit
    )
    
    return [
        ConversionHistoryWithServiceResponse(
            ConversionHistoryID=h.ConversionHistoryID,
            UserID=h.UserID,
            ServiceID=h.ServiceID,
            CreatedAt=h.CreatedAt,
            ServiceName=h.service.ServiceName,
            InputFormat=h.service.InputFormat,
            OutputFormat=h.service.OutputFormat,
            Cost=h.service.Price
        )
        for h in histories
    ]

