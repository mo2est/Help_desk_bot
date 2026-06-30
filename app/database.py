from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

engine = None
async_session_factory = None


async def init_db(database_url: str) -> None:
    global engine, async_session_factory
    engine = create_async_engine(database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


def get_session_factory() -> async_sessionmaker:
    return async_session_factory
