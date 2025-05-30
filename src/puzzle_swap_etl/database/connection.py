"""Database connection and session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.utils import LoggerMixin


class DatabaseManager(LoggerMixin):
    """Database connection manager with 3-layer architecture support."""

    def __init__(self) -> None:
        """Initialize database manager."""
        self.engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=settings.debug,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session as async context manager.

        Yields:
            AsyncSession: Database session
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_schemas(self) -> None:
        """Create database schemas for 3-layer architecture."""
        schemas = ["stg", "ods", "dm"]

        async with self.get_session() as session:
            for schema in schemas:
                try:
                    await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                    self.logger.info(f"Schema '{schema}' created or already exists")
                except Exception as e:
                    self.logger.error(f"Failed to create schema '{schema}': {str(e)}")
                    raise

            await session.commit()
            self.logger.info("All schemas created successfully")

    async def create_tables(self) -> None:
        """Create all database tables."""
        from puzzle_swap_etl.database.models_dm import DmBase
        from puzzle_swap_etl.database.models_ods import OdsBase
        from puzzle_swap_etl.database.models_stg import StgBase

        # First create schemas
        await self.create_schemas()

        # Then create tables for each layer
        async with self.engine.begin() as conn:
            await conn.run_sync(StgBase.metadata.create_all)
            await conn.run_sync(OdsBase.metadata.create_all)
            await conn.run_sync(DmBase.metadata.create_all)

        self.logger.info("Database tables created successfully")

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        from puzzle_swap_etl.database.models_dm import DmBase
        from puzzle_swap_etl.database.models_ods import OdsBase
        from puzzle_swap_etl.database.models_stg import StgBase

        async with self.engine.begin() as conn:
            await conn.run_sync(DmBase.metadata.drop_all)
            await conn.run_sync(OdsBase.metadata.drop_all)
            await conn.run_sync(StgBase.metadata.drop_all)

        self.logger.info("Database tables dropped successfully")

    async def check_connection(self) -> bool:
        """Check database connection."""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                self.logger.info("Database connection successful")
                return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            return False

    async def get_table_counts(self) -> dict:
        """Get row counts for all tables."""
        counts = {}

        tables = [
            # STG layer
            ("stg", "transactions"),
            ("stg", "asset_info"),
            ("stg", "pool_info"),
            ("stg", "price_data"),
            # ODS layer
            ("ods", "transactions"),
            ("ods", "swaps"),
            ("ods", "staking_events"),
            ("ods", "assets"),
            ("ods", "pools"),
            ("ods", "swap_pairs"),
            ("ods", "asset_prices"),
            ("ods", "protocol_allocations"),
            ("ods", "lending_info"),
        ]

        async with self.get_session() as session:
            for schema, table in tables:
                try:
                    result = await session.execute(
                        text(f"SELECT COUNT(*) FROM {schema}.{table}")
                    )
                    count = result.scalar()
                    counts[f"{schema}.{table}"] = count
                except Exception as e:
                    self.logger.warning(
                        f"Failed to get count for {schema}.{table}: {e}"
                    )
                    counts[f"{schema}.{table}"] = "Error"

        return counts

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()
        self.logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()
