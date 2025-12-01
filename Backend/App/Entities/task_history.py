"""
Task history entity
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column 

from Database.connection import Base 

class TaskHistory(Base):
    __tablename__ = 'TASKHISTORY'

    HistoryID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    TaskID: Mapped[int] = mapped_column(BigInteger)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable

