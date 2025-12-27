"""
Tasks entity
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Double
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from Entities.user import User
    from Entities.service_types import ServiceTypes

class Tasks(Base):
    __tablename__ = 'TASKS'

    __table_args__ = {'extend_existing': True}

    TaskID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(Integer, ForeignKey("USER.UserID"), nullable=False)
    ServiceTypeID: Mapped[int] = mapped_column(Integer, ForeignKey("SERVICETYPES.ServiceTypeID", ondelete="CASCADE") , nullable=False)

    OriginalFileName: Mapped[str] = mapped_column(String(255))
    OriginalFileSize: Mapped[int] = mapped_column(Integer)
    OriginalFilePath: Mapped[str] = mapped_column(String(255))

    OutputFileName: Mapped[Optional[str]] = mapped_column(String(255))
    OutputFileSize: Mapped[Optional[int]] = mapped_column(Integer)
    OutputFilePath: Mapped[Optional[str]] = mapped_column(String(255))

    TaskStatus: Mapped[bool] = mapped_column(String(50))
    # Values: 'Failed', 'Completed'
    TaskTime: Mapped[int] = mapped_column(Double)

    InputFormat: Mapped[Optional[str]] = mapped_column(String(50))
    OutputFormat: Mapped[Optional[str]] = mapped_column(String(50))

    CompressionLevel: Mapped[Optional[str]] = mapped_column(String(100))

    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable

    #relationship
    User: Mapped["User"] = relationship("Entities.user.User", back_populates="UserTasks")
    TaskType: Mapped["ServiceTypes"] = relationship("Entities.service_types.ServiceTypes", back_populates="Tasks")