from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = settings.database_url
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Detect if using Supabase connection pooler (port 6543 = transaction mode)
# Transaction mode poolers don't support prepared statements
is_pooler = ":6543/" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL

engine_kwargs = dict(
    echo=False,
    future=True,
)

if is_pooler:
    # Supabase pooler (transaction mode): disable prepared statements, use NullPool
    # since the external pooler manages connections
    engine_kwargs.update(
        poolclass=NullPool,
        connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0},
    )
else:
    # Direct connection: use SQLAlchemy connection pooling
    engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
