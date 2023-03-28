from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src import settings

##############################################
# BLOCK FOR COMMON INTERACTION WITH DATABASE #
##############################################

# create async engine for interaction with database
engine = create_async_engine(
    settings.REAL_DATABASE_URL,
    future=True,
    echo=True,
    pool_recycle=1800,
    execution_options={"isolation_level": "AUTOCOMMIT"},
)

# create session for the interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
