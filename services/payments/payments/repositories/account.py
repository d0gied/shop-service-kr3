from decimal import Decimal
from typing import Iterable
from venv import logger
from sqlalchemy import select, func, text

from payments.database.account import Account, Transaction
from payments.repositories.base import AbstractRepository

from sqlalchemy.exc import OperationalError


class AccountRepository(AbstractRepository):
    async def get_account(self, user_id: int) -> Account | None:
        """
        Retrieve an account by user ID.
        """
        return await self.session.get(Account, user_id)

    async def create_account(self, user_id: int) -> Account:
        """
        Create a new account for the given user ID.
        """
        logger = self.logger.bind(user_id=user_id)

        account = Account(user_id=user_id)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        logger.debug("Account created", account_id=account.user_id)

        return account

    async def get_balance(self, user_id: int) -> Decimal:
        """
        Retrieve the balance of the account for the given user ID.
        """
        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            ).where(Transaction.account_id == user_id),
        )
        balance = result.scalar_one()

        return balance

    async def withdraw_with_lock(
        self,
        account_id: int,
        amount: Decimal,
        description: str | None = None,
    ) -> Transaction:
        """
        Add a transaction to the account.
        """
        logger = self.logger.bind(
            account_id=account_id,
            amount=amount,
            description=description,
            direction="withdraw_with_lock",
        )

        self.session.begin()

        await self.session.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": account_id}
        )

        balance = await self.get_balance(account_id)
        if balance < amount:
            await self.session.rollback()
            logger.debug("Insufficient funds for withdrawal")
            raise ValueError("Insufficient funds.")

        transaction = Transaction(
            account_id=account_id, amount=-amount, description=description
        )
        self.session.add(transaction)
        await self.session.commit()

        await self.session.refresh(transaction)

        logger.debug("Transaction completed", transaction_id=transaction.id)

        return transaction

    async def withdraw(
        self, account_id: int, amount: Decimal, description: str | None = None
    ) -> Transaction:
        """
        Withdraw an amount from the account.
        This method uses a serializable isolation level to ensure that the transaction
        is isolated from other transactions.
        If the balance is insufficient, it raises a ValueError.
        If a serialization failure occurs, it raises a RuntimeError.
        """
        logger = self.logger.bind(
            account_id=account_id,
            amount=amount,
            description=description,
            direction="withdraw",
        )

        self.session.begin()
        try:
            await self.session.execute(
                text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            )

            balance = await self.get_balance(account_id)
            if balance < amount:
                raise ValueError("Insufficient funds.")

            transaction = Transaction(
                account_id=account_id,
                amount=-amount,
                description=description,
            )
            self.session.add(transaction)
            await self.session.commit()

        except OperationalError as e:
            await self.session.rollback()
            raise RuntimeError("Serialization failure, retry transaction.") from e
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError("An error occurred during the transaction.") from e
        else:
            await self.session.refresh(transaction)
            logger.debug(
                "Transaction completed",
                transaction_id=transaction.id,
            )
            return transaction

    async def deposit(
        self,
        account_id: int,
        amount: Decimal,
        description: str | None = None,
    ) -> Transaction:
        """
        Deposit an amount into the account.
        """
        logger = self.logger.bind(
            account_id=account_id,
            amount=amount,
            description=description,
            direction="deposit",
        )

        self.session.begin()
        transaction = Transaction(
            account_id=account_id, amount=amount, description=description
        )
        self.session.add(transaction)
        await self.session.commit()

        await self.session.refresh(transaction)
        logger.debug("Transaction completed", transaction_id=transaction.id)

        return transaction

    async def get_transactions(self, account_id: int) -> Iterable[Transaction]:
        """
        Retrieve all transactions for the given account ID.
        """
        result = await self.session.execute(
            select(Transaction).where(Transaction.account_id == account_id)
        )
        transactions = result.scalars().all()

        return transactions
