"""
conversion history entity
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from user import User
    from service_types import ServiceTypes

class ConversionHistory(Base):
    __tablename__ = "CONVERSION_HISTORY"

    ConversionHistoryID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("USER.UserID", ondelete="CASCADE"))
    ServiceID: Mapped[int] = mapped_column(BigInteger, ForeignKey("SERVICETYPES.ServiceTypeID", ondelete="CASCADE"))
    # pylint: disable=not-callable
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    #relationship
    user: Mapped["User"] = relationship(back_populates="conversion_histories")
