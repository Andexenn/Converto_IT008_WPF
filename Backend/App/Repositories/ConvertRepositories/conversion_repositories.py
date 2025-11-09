from sqlalchemy.orm import Session
from typing import List 
from fastapi import HTTPException, status 
from decimal import Decimal

from Services.ConvertServices.conversion_service import IConversionService
from Schemas.conversion_history import ConversionHistoryResponse
from Entities.conversion_history import ConversionHistory
from Entities.service import Service 

class ConversionRepositories(IConversionService):
    def __init__(self, db: Session):
        self.db = db 

    async def get_or_create_service(self, input_format: str, output_format: str) -> int:
        try:
            service = self.db.query(Service).filter(
                Service.InputFormat == input_format.upper() and Service.OutputFormat == output_format.upper()
            ).first()

            if service:
                return service.ServiceID
            
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

            return new_service.ServiceID

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get or create service: {str(e)}"
            )

    async def create_conversion_history(self, user_id: int, service_id: int) -> ConversionHistoryResponse:
        try:
            new_history = ConversionHistory(
                UserID = user_id,
                ServiceID = service_id
            )

            self.db.add(new_history)
            self.db.flush()
            self.db.refresh(new_history)

            return ConversionHistoryResponse.model_validate(new_history)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create conversion history: {str(e)}"
            )
        
    async def get_user_conversion_history(self, user_id: int, limit: int = 50) -> List[ConversionHistoryResponse]:
        try:
            histories = self.db.query(ConversionHistory).filter(
                ConversionHistory.UserID == user_id).order_by(
                    ConversionHistory.CreatedAt().desc()
                ).limit(limit).all()
            
            return [ConversionHistoryResponse.model_validate(h) for h in histories]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user conversion history: {str(e)}"
            )

