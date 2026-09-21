import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from payment_webhook_relay_idempotency_platform.config.config import settings

class Base(DeclarativeBase):
    pass

DATABASE_URL = settings.database_url
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False,autoflush=False,bind=engine)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def test_connection():
    async with engine.connect() as conn:
        print("Connected to db")


if __name__ == "__main__":
    asyncio.run(test_connection())