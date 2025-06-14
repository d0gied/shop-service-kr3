from abc import ABC, abstractmethod
from dataclasses import dataclass

from payments.uow import UOW
from structlog import BoundLogger


@dataclass
class AbstractService(ABC):
    """
    Abstract base class for services in the payments module.
    Provides a common interface for all services.
    """

    uow: UOW
    logger: BoundLogger

    def __post_init__(self):
        self.logger = self.logger.bind(service=self.__class__.__name__)
