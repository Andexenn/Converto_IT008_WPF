"""
Conversion history handler
"""

from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Database.connection import get_db
from Core.dependencies import get_current_user
from Entities.user import User
from Repositories.conversion_history_repository import ConversionHistoryRepository
from Schemas.conversion import ConversionHistoryWithServiceResponse

router = APIRouter()

@router.get("/history", response_model=list[ConversionHistoryWithServiceResponse])
async def get_my_conversion_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's conversion history
    """
    conversion_repo = ConversionHistoryRepository(db)
    histories = await conversion_repo.get_user_conversion_history(
        user_id=current_user.UserID,
        limit=limit
    )

    return [
        ConversionHistoryWithServiceResponse(
            ConversionHistoryID=h.ConversionHistoryID,
            CreatedAt=h.CreatedAt,
            ServiceName=h.service.ServiceName,
            Cost=Decimal(h.service.Price)
        )
        for h in histories
    ]
