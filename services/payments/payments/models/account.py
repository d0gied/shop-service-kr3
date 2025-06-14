from decimal import Decimal
from pydantic import BaseModel, Field


class Account(BaseModel):
    user_id: int = Field(..., description="Unique identifier for the user")
    balance: Decimal = Field(..., description="Current balance of the account")

class Transaction(BaseModel):
    id: int = Field(..., description="Unique identifier for the transaction")
    account_id: int = Field(
        ..., description="ID of the account associated with the transaction"
    )
    amount: Decimal = Field(..., description="Amount of the transaction")
    description: str | None = Field(
        None, description="Optional description of the transaction"
    )
    direction: str = Field(
        ..., description="Direction of the transaction (e.g., 'withdraw', 'deposit')"
    )
    