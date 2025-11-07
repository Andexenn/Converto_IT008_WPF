from sqlalchemy import String, BigInteger, DECIMAL, ForeignKey, Double, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from App.Database.connection import Base 
from datetime import datetime


class WalletTransaction(Base):
    __tablename__ = "wallet_transaction"

    WalletTransactionID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    WalletID: Mapped[int] = mapped_column(BigInteger, ForeignKey("wallet.WalletID", ondelete="CASCADE"))
    Amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    BalanceAfter: Mapped[float] = mapped_column(Double)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=datetime.now)





