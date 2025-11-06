from sqlalchemy import Column, BigInteger, String, DECIMAL
from sqlalchemy.orm import relationship
from App.Database.connection import Base

class Service(Base):
    __tablename__ = "SERVICE"

    SerivceID = Column(BigInteger, primary_key=True, autoincrement=True)
    InputFormat = Column(String(50), nullable=False)
    OutputFormat = Column(String(50), nullable=False)
    ServiceName = Column(String(150), nullable=False)
    Price = Column(DECIMAL(10, 2), nullable=False)

    #relationship
    conversion_histories = relationship("ConversionHistory", back_populates="service")