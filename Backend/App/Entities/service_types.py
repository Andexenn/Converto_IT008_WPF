"""
service type entity
"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from Database.connection import Base

class ServiceTypes(Base):
    __tablename__ = "SERVICETYPES"

    ServiceTypeID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ServiceName: Mapped[str] = mapped_column(String(50))
    # Values: 'Convert', 'Compress', 'Remove Background'
    ServiceDescription: Mapped[str] = mapped_column(String(500))




