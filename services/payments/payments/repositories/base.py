from abc import ABC, abstractmethod
from dataclasses import dataclass
from venv import logger
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger


@dataclass
class AbstractRepository(ABC):
    session: AsyncSession
    logger: BoundLogger

    def __post_init__(self):
        self.logger = self.logger.bind(repository=self.__class__.__name__)
