"""
File Type entity
"""

from datetime import datetime

from sqlalchemy import BigInteger, String 
from sqlalchemy.orm import Mapped, mapped_column

from Database.connection import Base 

class FileTypes(Base):
    __tablename__ = 'FILETYPES'

    FileTypeID: Mapped[str] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    CategoryName: Mapped[str] = mapped_column(String(255))
    # Values: 'Image', 'Video', Audio', 'Office', 'PDF'
    FileExtension: Mapped[str] = mapped_column(String(255))
    
