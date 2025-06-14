from decimal import Decimal
from structlog import BoundLogger
from payments.models.account import Account, Transaction
from payments.services.base import AbstractService
from payments.database.account import Account as DBAccount
from fastapi import HTTPException
from payments.uow import UOW


async def get_account(
    uow: UOW,
    user_id: int,
    logger: BoundLogger,
) -> DBAccount:
    """
    Helper function to retrieve or create an account for a given user ID.
    This function is used internally by the AccountService methods.

    :param uow: Unit of Work instance to interact with the database.
    :param user_id: The ID of the user whose account is to be retrieved or created.
    :return: Account object for the specified user.
    """
    account = await uow.account_repo.get_account(user_id)
    if not account:
        logger.info("Account not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="Account not found")
    return account


class AccountService(AbstractService):
    """
    Service for managing account-related operations.
    Inherits from AbstractService to ensure consistent service structure.
    """

    async def get_account(self, user_id: int) -> Account:
        """
        Retrieve account information for a given user ID. If the account does not exist,
        it will create a new account for the user.

        :param user_id: The ID of the user whose account information is to be retrieved.
        :return: Account information for the specified user.
        """
        logger = self.logger.bind(user_id=user_id, action="get_account")

        logger.info("Retrieving account information")

        account = await get_account(self.uow, user_id, logger)
        logger.info("Account retrieved successfully")

        balance = await self.uow.account_repo.get_balance(user_id)
        logger.info("Balance retrieved", balance=balance)

        return Account(
            user_id=account.user_id,
            balance=balance,
        )

    async def deposit(self, user_id: int, amount: Decimal) -> Transaction:
        """
        Deposit an amount into the user's account.
        :param user_id: The ID of the user whose account is to be credited.
        :param amount: The amount to be deposited.
        :return: Updated account information after the deposit.
        """
        logger = self.logger.bind(user_id=user_id, amount=amount, action="deposit")

        if amount <= 0:
            logger.error("Deposit amount must be positive")
            raise HTTPException(
                status_code=400, detail="Deposit amount must be positive"
            )

        logger.info("Depositing amount into account")

        account = await get_account(self.uow, user_id, logger)

        transaction = await self.uow.account_repo.deposit(user_id, amount)
        if not transaction:
            logger.error("Failed to deposit amount into account")
            raise HTTPException(
                status_code=500, detail="Failed to deposit amount into account"
            )
        logger.info("Deposit successful", transaction_id=transaction.id)

        return Transaction(
            id=transaction.id,
            account_id=account.user_id,
            amount=amount,
            description=transaction.description,
            direction="deposit",
        )

    async def withdraw(self, user_id: int, amount: Decimal) -> Transaction:
        """
        Withdraw an amount from the user's account.
        :param user_id: The ID of the user whose account is to be debited.
        :param amount: The amount to be withdrawn.
        :return: Updated account information after the withdrawal.
        """

        logger = self.logger.bind(user_id=user_id, amount=amount, action="withdraw")

        if amount <= 0:
            logger.error("Withdrawal amount must be positive")
            raise HTTPException(
                status_code=400, detail="Withdrawal amount must be positive"
            )

        logger.info("Withdrawing amount from account")

        account = await get_account(self.uow, user_id, logger)

        try:
            transaction = await self.uow.account_repo.withdraw_with_lock(
                user_id, amount
            )
        except ValueError as e:
            logger.error("Insufficient funds for withdrawal", error=str(e))
            raise HTTPException(
                status_code=400, detail="Insufficient funds for withdrawal"
            )
        logger.info("Withdrawal successful", transaction_id=transaction.id)

        return Transaction(
            id=transaction.id,
            account_id=account.user_id,
            amount=amount,
            description=transaction.description,
            direction="withdraw",
        )

    async def get_transactions(self, user_id: int) -> list[Transaction]:
        """
        Retrieve all transactions for a given user ID.
        :param user_id: The ID of the user whose transactions are to be retrieved.
        :return: List of transactions for the specified user.
        """
        logger = self.logger.bind(user_id=user_id, action="get_transactions")

        logger.info("Checking if account exists for user")
        await get_account(self.uow, user_id, logger)

        logger.info("Retrieving transactions for user")

        transactions = await self.uow.account_repo.get_transactions(user_id)
        if not transactions:
            logger.info("No transactions found for user", user_id=user_id)
            return []

        transactions = list(transactions)  # Ensure transactions is a list
        logger.info("Transactions retrieved successfully", count=len(transactions))

        return [
            Transaction(
                id=transaction.id,
                account_id=transaction.account_id,
                amount=abs(transaction.amount),
                description=transaction.description,
                direction="withdraw" if transaction.amount < 0 else "deposit",
            )
            for transaction in transactions
        ]

    async def create_account(self, user_id: int) -> Account:
        """
        Create a new account for the user if it does not already exist.
        :param user_id: The ID of the user for whom the account is to be created.
        :return: Newly created account information.
        """
        logger = self.logger.bind(user_id=user_id, action="create_account")

        account = await self.uow.account_repo.get_account(user_id)
        if account:
            logger.info("Account already exists", user_id=user_id)
            raise HTTPException(status_code=400, detail="Account already exists")
        logger.info("Creating new account for user")

        account = await self.uow.account_repo.create_account(user_id)
        logger.info("Account created successfully", user_id=account.user_id)
        return Account(
            user_id=account.user_id,
            balance=await self.uow.account_repo.get_balance(user_id),
        )
