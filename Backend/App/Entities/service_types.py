"""
service type entity
"""

from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from Entities.tasks import Tasks

class ServiceTypes(Base):
    __tablename__ = "SERVICETYPES"

    __table_args__ = {'extend_existing': True}

    ServiceTypeID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ServiceName: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Values: 'Convert', 'Compress', 'Background removal'
    ServiceDescription: Mapped[Optional[str]] = mapped_column(String(500))

    Tasks: Mapped[List["Tasks"]] = relationship("Entities.tasks.Tasks" ,back_populates="TaskType", lazy="selectin", cascade="all, delete-orphan")


