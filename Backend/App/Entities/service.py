from typing import List, TYPE_CHECKING
from sqlalchemy import BigInteger, String, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column
from Database.connection import Base

if TYPE_CHECKING:
    from conversion_history import ConversionHistory

class Service(Base):
    __tablename__ = "SERVICE"

    ServiceID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    InputFormat: Mapped[str] = mapped_column(String(50))
    OutputFormat: Mapped[str] = mapped_column(String(50))
    ServiceName: Mapped[str] = mapped_column(String(150))
    Price: Mapped[float] = mapped_column(DECIMAL(10, 2))

    #relationship
    conversion_histories: Mapped[List["ConversionHistory"]] = relationship(back_populates="service")