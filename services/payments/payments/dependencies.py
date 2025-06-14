from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger
from payments.database import get_engine, get_session_maker
from typing import Annotated, AsyncGenerator
from common.logging import get_logger
from uuid import uuid4

from payments.uow import UOW
from payments.services.account import AccountService


async def logger_dep() -> BoundLogger:
    request_id: str = str(uuid4())
    return get_logger(__name__).bind(
        request_id=request_id,
    )


LoggerDep = Annotated[BoundLogger, Depends(logger_dep)]


async def db_session_dep(logger: LoggerDep) -> AsyncGenerator[AsyncSession, None]:
    maker = get_session_maker(get_engine())

    async with maker() as session:
        logger.debug("session_open")
        try:
            yield session
        except:
            logger.debug("session_rollback")
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("session_close")


DBSessionDep = Annotated[AsyncSession, Depends(db_session_dep)]


async def uow_dep(
    session: DBSessionDep,
    logger: LoggerDep,
) -> UOW:
    """
    Dependency to provide a Unit of Work instance with a session and logger.
    """
    return UOW(session=session, logger=logger)


UOWDep = Annotated[UOW, Depends(uow_dep)]


async def account_service_dep(
    uow: UOWDep,
) -> AccountService:
    """
    Dependency to provide an instance of AccountService.
    """
    return AccountService(uow=uow, logger=uow.logger)


AccountServiceDep = Annotated[AccountService, Depends(account_service_dep)]
