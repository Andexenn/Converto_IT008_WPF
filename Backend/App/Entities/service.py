from typing import List
from sqlalchemy import Column, BigInteger, String, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column
from App.Database.connection import Base

from App.Entities.conversion_history import ConversionHistory
class Service(Base):
    __tablename__ = "SERVICE"

    SerivceID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    InputFormat: Mapped[str] = mapped_column(String(50))
    OutputFormat: Mapped[str] = mapped_column(String(50))
    ServiceName: Mapped[str] = mapped_column(String(150))
    Price: Mapped[float] = mapped_column(DECIMAL(10, 2))

    #relationship
    conversion_histories: Mapped[List["ConversionHistory"]] = relationship(back_populates="service")