from functools import lru_cache
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from payments.config import DatabaseSettings


@lru_cache
def get_engine(settings: DatabaseSettings = DatabaseSettings()) -> AsyncEngine:
    return create_async_engine(
        settings.database_url.encoded_string(),
        echo=settings.echo,
    )


@lru_cache
def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    """
    Base class for all database models.
    """

    pass


async def create_all_tables(engine: AsyncEngine) -> None:
    """
    Create all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
