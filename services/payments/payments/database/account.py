from decimal import Decimal
from . import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Numeric


class Account(Base):
    __tablename__ = "accounts"

    user_id: Mapped[int] = mapped_column(primary_key=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )

    description: Mapped[str | None] = mapped_column(nullable=True)
