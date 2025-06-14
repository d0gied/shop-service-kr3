from fastapi import APIRouter


from decimal import Decimal
from payments.models.account import Account, Transaction
from payments.dependencies import AccountServiceDep

router = APIRouter(
    prefix="/account",
    tags=["account"],
)


@router.get("/{user_id}")
async def get_account(user_id: int, account_service: AccountServiceDep) -> Account:
    """
    Retrieve account information for a given user ID.
    """

    return await account_service.get_account(user_id)


@router.post("/{user_id}/deposit")
async def deposit(
    user_id: int, amount: Decimal, account_service: AccountServiceDep
) -> Transaction:
    """
    Deposit an amount into the user's account.
    """
    return await account_service.deposit(user_id, amount)


@router.post(
    "/{user_id}/withdraw", responses={400: {"description": "Insufficient funds"}}
)
async def withdraw(
    user_id: int, amount: Decimal, account_service: AccountServiceDep
) -> Transaction:
    """
    Withdraw an amount from the user's account.
    """
    return await account_service.withdraw(user_id, amount)


@router.get("/{user_id}/transactions")
async def get_transactions(
    user_id: int, account_service: AccountServiceDep
) -> list[Transaction]:
    """
    Retrieve all transactions for a given user ID.
    """
    return await account_service.get_transactions(user_id)


@router.post(
    "/{user_id}/create_account",
    responses={
        200: {"description": "Account created"},
        400: {"description": "Account already exists"},
    },
)
async def create_account(user_id: int, account_service: AccountServiceDep) -> Account:
    """
    Create a new account for the given user ID.
    """
    return await account_service.create_account(user_id)
