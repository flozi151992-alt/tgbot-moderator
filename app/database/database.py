"""
Database connection and session management.
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.database.models import Base

# Global variables
engine = None
async_session_maker = None

async def init_database():
    """Initialize database connection and create tables."""
    global engine, async_session_maker
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database.url,
        poolclass=NullPool,
        echo=False
    )
    
    # Create async session maker
    async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create tables using ORM (recommended approach)
    async with engine.begin() as conn:
        # Only create tables if they don't exist (don't drop existing data)
        await conn.run_sync(Base.metadata.create_all)
    
    # Clear any cached prepared statements
    if hasattr(engine.sync_engine, 'dispose'):
        engine.sync_engine.dispose()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def close_database():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()