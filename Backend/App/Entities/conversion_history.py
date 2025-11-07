from sqlalchemy import DateTime, BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from App.Database.connection import Base 
from datetime import datetime

class ConversionHistory(Base):
    __tablename__ = "conversion_history"

    ConversionHistoryID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.UserID", ondelete="CASCADE"))
    ServiceID: Mapped[int] = mapped_column(BigInteger, ForeignKey("service.ServiceID", ondelete="CASCADE"))
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=datetime.now)
    
