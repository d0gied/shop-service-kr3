from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger

from payments.repositories.account import AccountRepository


class UOW:
    def __init__(self, session: AsyncSession, logger: BoundLogger) -> None:
        self.session = session
        self.logger = logger.bind(unit_of_work=self.__class__.__name__)

        self.account_repo = AccountRepository(session=session, logger=self.logger)
