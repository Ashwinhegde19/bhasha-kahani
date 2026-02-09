from uuid import uuid4
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()


def normalize_database_url(raw_url: str) -> tuple[str, dict]:
    """
    Convert Postgres URLs into asyncpg-compatible URL/connect args.
    asyncpg does not accept 'sslmode'; map it to the 'ssl' connect arg.
    """
    url = raw_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    split_url = urlsplit(url)
    if not split_url.query:
        return url, {}

    query_pairs = parse_qsl(split_url.query, keep_blank_values=True)
    filtered_pairs = []
    connect_args = {}

    for key, value in query_pairs:
        if key.lower() == "sslmode":
            mode = value.strip().lower()
            if mode in {"disable", "false", "0"}:
                connect_args["ssl"] = False
            else:
                connect_args["ssl"] = "require"
            continue
        filtered_pairs.append((key, value))

    normalized_query = urlencode(filtered_pairs)
    normalized_url = urlunsplit(
        (
            split_url.scheme,
            split_url.netloc,
            split_url.path,
            normalized_query,
            split_url.fragment,
        )
    )
    return normalized_url, connect_args


def build_pooler_connect_args(extra_connect_args: dict) -> dict:
    """
    Build asyncpg options compatible with PgBouncer transaction pooling.
    """
    return {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        # Prevent statement name collisions across pooled backend sessions.
        "prepared_statement_name_func": lambda: f"__asyncpg_stmt_{uuid4()}__",
        **extra_connect_args,
    }


DATABASE_URL, parsed_connect_args = normalize_database_url(settings.database_url)

# Detect if using Supabase connection pooler (port 6543 = transaction mode)
# Transaction mode poolers don't support prepared statements
is_pooler = ":6543" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL

if is_pooler:
    connect_args = build_pooler_connect_args(parsed_connect_args)
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
        connect_args=connect_args,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args=parsed_connect_args or None,
    )

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
