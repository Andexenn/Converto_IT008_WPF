"""
User preferences entity
"""

from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column 

from Database.connection import Base 

class UserPreferences(Base):
    __tablename__ = 'USERPREFERENCES'

    PreferenceID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger)

    DefaultOutputFolder: Mapped[str] = mapped_column(String(255))
    Language: Mapped[str] = mapped_column(String(100))

    CreatedAt:Mapped[datetime] = mapped_column(DateTime)
    UpdatedAt:Mapped[datetime] = mapped_column(DateTime)
