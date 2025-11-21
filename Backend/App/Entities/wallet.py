"""
wallet entity
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import BigInteger, DECIMAL, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from Database.connection import Base

if TYPE_CHECKING:
    from user import User
    from wallet_transaction import WalletTransaction

class Wallet(Base):
    __tablename__ = "WALLET"

    WalletID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("USER.UserID", ondelete="CASCADE"))
    Balance: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    CurrencyCode: Mapped[str] = mapped_column(String(50), default="USD")

    #relationship
    user: Mapped["User"] = relationship(back_populates="wallet")
    transactions: Mapped[List["WalletTransaction"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")
