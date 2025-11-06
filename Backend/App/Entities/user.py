from sqlalchemy import Column, BigInteger, String, DateTime, LargeBinary 
from sqlalchemy.orm import relationship
from App.Database.connection import Base 

class User(Base):
    __tablename__ = "USER"

    UserID = Column(BigInteger, primary_key=True, autoincrement=True)
    FirstName = Column(String(255))
    LastName = Column(String(255))
    Address = Column(String(500))
    PhoneNumber = Column(String(20))
    DateOfBirth = Column(DateTime, nullable=True)
    City = Column(String(100))
    Image = Column(LargeBinary, nullable=True)
    Email = Column(String(255), unique=True, nullable=False, index=True)
    HashedPassword = Column(String(255), nullable=False)

    #Relationship
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    conversion_histories = relationship("ConversionHistory", back_populates="user", cascade="all, delete-orphan")





