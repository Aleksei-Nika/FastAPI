from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os 

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), 'office_lunch.db')}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession: 
    async with AsyncSessionLocal() as session:
        try: 
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally: 
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
