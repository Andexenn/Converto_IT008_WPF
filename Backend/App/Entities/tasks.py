"""
Tasks entity
"""

from sqlalchemy import BigInteger, String 
from sqlalchemy.orm import Mapped, mapped_column 

from Database.connection import Base 

class Tasks(Base):
    __tablename__ = 'TASKS'

    TaskID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger)
    ServiceTypeID: Mapped[int] = mapped_column(BigInteger)

    OriginalFileName: Mapped[str] = mapped_column(String(255))
    OriginalFileSize: Mapped[int] = mapped_column(BigInteger)
    OriginalPath: Mapped[str] = mapped_column(String(255))

    OutputFileName: Mapped[str] = mapped_column(String(255))
    OutputFileSize: Mapped[int] = mapped_column(BigInteger)
    OutputPath: Mapped[str] = mapped_column(String(255))

    TaskStatus: Mapped[str] = mapped_column(String(50))
    # Values: 'Failed', 'Pending', 'Completed'

    InputFormat: Mapped[str] = mapped_column(String(50))
    OutputFormat: Mapped[str] = mapped_column(String(50))

    CompressionLevel: Mapped[str] = mapped_column(String(100))