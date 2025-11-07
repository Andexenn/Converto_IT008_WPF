from sqlalchemy import column, BigInteger, String, DateTime, LargeBinary 
from sqlalchemy.orm import relationship, mapped_column, Mapped
from Database.connection import Base 
from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from conversion_history import ConversionHistory
    from wallet import Wallet

class User(Base):
    __tablename__ = "USER"

    UserID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    FirstName: Mapped[str] = mapped_column(String(255))
    LastName: Mapped[str] = mapped_column(String(255))
    Address: Mapped[str] = mapped_column(String(500))
    PhoneNumber: Mapped[str] = mapped_column(String(20))
    DateOfBirth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    City: Mapped[str] = mapped_column(String(100))
    Image: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    Email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    HashedPassword: Mapped[str] = mapped_column(String(255))

    #Relationship
    wallet: Mapped["Wallet"] = relationship(back_populates="user", cascade="all, delete-orphan")
    conversion_histories: Mapped[List["ConversionHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")






