"""
service type entity
"""

from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from Entities.tasks import Tasks

class ServiceTypes(Base):
    __tablename__ = "SERVICETYPES"

    ServiceTypeID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ServiceName: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Values: 'Convert', 'Compress', 'Background removal'
    ServiceDescription: Mapped[Optional[str]] = mapped_column(String(500))

    Tasks: Mapped[List["Tasks"]] = relationship(back_populates="TaskType", lazy="selectin", cascade="all, delete-orphan")


