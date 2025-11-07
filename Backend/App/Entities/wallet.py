from sqlalchemy import BigInteger, DECIMAL, DATETIME, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column 
from App.Database.connection import Base 


class Wallet(Base):
    __tablename__ = "wallet"

    WalletID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.UserID", ondelete="CASCADE"))
    Balance: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    CurrencyCode: Mapped[str] = mapped_column(String(50), default="USD")

