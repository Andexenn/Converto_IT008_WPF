from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DECIMAL, ForeignKey, Double, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Database.connection import Base

if TYPE_CHECKING:
    from wallet import Wallet

class WalletTransaction(Base):
    __tablename__ = "WALLET_TRANSACTION"

    WalletTransactionID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    WalletID: Mapped[int] = mapped_column(BigInteger, ForeignKey("WALLET.WalletID", ondelete="CASCADE"))
    Amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    BalanceAfter: Mapped[float] = mapped_column(Double)
    # pylint: disable=not-callable
    CreatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationship
    wallet:Mapped["Wallet"] = relationship(back_populates="transactions")

