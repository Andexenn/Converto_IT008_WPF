from sqlalchemy import column, BigInteger, String, DateTime, LargeBinary 
from sqlalchemy.orm import relationship, mapped_column, Mapped
from App.Database.connection import Base 
from datetime import datetime

class User(Base):
    __tablename__ = "user"

    UserID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    FirstName: Mapped[str] = mapped_column(String(255))
    LastName: Mapped[str] = mapped_column(String(255))
    Address: Mapped[str] = mapped_column(String(500))
    PhoneNumber: Mapped[str] = mapped_column(String(20))
    DateOfBirth: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    City: Mapped[str] = mapped_column(String(100))
    Image: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    Email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    HashedPassword: Mapped[str] = mapped_column(String(255))

    #Relationship
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    conversion_histories = relationship("ConversionHistory", back_populates="user", cascade="all, delete-orphan")





