from sqlalchemy import String, BigInteger, DECIMAL, ForeignKey, Double, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from App.Database.connection import Base 
from datetime import datetime

from App.Entities.wallet import Wallet
class WalletTransaction(Base):
    __tablename__ = "WALLET_TRANSACTION"

    WalletTransactionID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    WalletID: Mapped[int] = mapped_column(BigInteger, ForeignKey("WALLET.WalletID", ondelete="CASCADE"))
    Amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    BalanceAfter: Mapped[float] = mapped_column(Double)
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=datetime.now)

    # relationship
    wallet:Mapped["Wallet"] = relationship(back_populates="transactions")




