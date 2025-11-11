"""
conversion_history_repository module
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Tuple
from fastapi import HTTPException, status
from decimal import Decimal

from Services.conversion_history_service import IConversionHistoryService
from Schemas.conversion import ConversionResponse
from Entities.conversion_history import ConversionHistory
from Entities.service import Service

class ConversionHistoryRepository(IConversionHistoryService):
    """
    Implement ConversionHistoryRepository from IConversionHistoryService
    """
    def __init__(self, db: Session):
        self.db = db

    async def get_or_create_service(self, input_format: str, output_format: str) -> Service:
        try:
            service = self.db.query(Service).filter(
                Service.InputFormat == input_format.upper(),
                Service.OutputFormat == output_format.upper()
            ).first()

            if service:
                return service

            service_name = f"{input_format.upper()} to {output_format.upper()} Conversion"

            new_service = Service(
                InputFormat = input_format,
                OutputFormat = output_format,
                ServiceName = service_name,
                Price = Decimal("0.00")
            )

            self.db.add(new_service)
            self.db.flush()
            self.db.refresh(new_service)

            return new_service

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get or create service: {str(e)}"
            ) from e

    async def record_conversion(
        self,
        user_id: int,
        input_format: str,
        output_format: str,
        original_filename: str,
        converted_filename: str,
        file_size_bytes: bytes,
        converted_file_bytes: bytes
    ) -> Tuple[ConversionResponse, bytes]:
        try:
            # Get or create service
            service = await self.get_or_create_service(input_format, output_format)

            # Create conversion history
            new_history = ConversionHistory(
                UserID=user_id,
                ServiceID=service.ServiceID
            )

            self.db.add(new_history)
            self.db.commit()
            self.db.refresh(new_history)

            # Build response
            response = ConversionResponse(
                success=True,
                message="File converted successfully",
                original_filename=original_filename,
                converted_filename=converted_filename,
                file_size_bytes=file_size_bytes,
                service_name=service.ServiceName,
                created_at=new_history.CreatedAt,
                cost=Decimal(service.Price),
                conversion_history_id=new_history.ConversionHistoryID
            )

            return response, converted_file_bytes

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record conversion: {str(e)}"
            ) from e


    async def get_user_conversion_history(self, user_id: int, limit: int = 50) -> List[ConversionHistory]:
        try:
            histories = self.db.query(ConversionHistory).options(
                joinedload(ConversionHistory.service)
            ).filter(
                ConversionHistory.UserID == user_id
            ).order_by(
                ConversionHistory.CreatedAt.desc()  # Fix: remove () from desc
            ).limit(limit).all()

            return histories
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user conversion history: {str(e)}"
            ) from e

