"""Database initialization and schema management."""

import asyncio
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.database.connection import db_manager
from puzzle_swap_etl.database.models_dm import DmBase
from puzzle_swap_etl.database.models_ods import OdsBase
from puzzle_swap_etl.database.models_stg import StgBase
from puzzle_swap_etl.utils import LoggerMixin


class DatabaseInitializer(LoggerMixin):
    """Database initialization and schema management."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        """Initialize database initializer."""
        self.engine: AsyncEngine = db_manager.engine

    async def initialize_database(self) -> None:
        """Initialize database with all schemas and tables."""
        self.logger.info("Creating database tables...")

        try:
            # Create all schemas and tables
            await self._create_schemas()
            await self._create_staging_tables()
            await self._create_ods_tables()
            await self._create_dm_tables()

            self.logger.info("Database tables created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create database tables: {e}")
            raise

    async def create_tables(self) -> None:
        """Create all database tables."""
        await self.initialize_database()

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            self.logger.info("Dropping database tables...")

            async with self.engine.begin() as conn:
                await conn.run_sync(DmBase.metadata.drop_all)
                await conn.run_sync(OdsBase.metadata.drop_all)
                await conn.run_sync(StgBase.metadata.drop_all)

            self.logger.info("Database tables dropped successfully")

        except Exception as e:
            self.logger.error(f"Failed to drop database tables: {e}")
            raise
        finally:
            await self.engine.dispose()

    async def reset_database(self) -> None:
        """Reset database by dropping and recreating all tables."""
        try:
            self.logger.info("Resetting database...")
            await self.drop_tables()
            await self.create_tables()
            self.logger.info("Database reset completed")
        except Exception as e:
            self.logger.error(f"Failed to reset database: {e}")
            raise

    async def _create_schemas(self) -> None:
        """Create database schemas."""
        self.logger.info("Creating database schemas...")

        async with self.engine.begin() as conn:
            # Create schemas
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS stg"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS ods"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS dm"))

            # Grant permissions
            await conn.execute(
                text(f"GRANT ALL PRIVILEGES ON SCHEMA stg TO {settings.database_user}")
            )
            await conn.execute(
                text(f"GRANT ALL PRIVILEGES ON SCHEMA ods TO {settings.database_user}")
            )
            await conn.execute(
                text(f"GRANT ALL PRIVILEGES ON SCHEMA dm TO {settings.database_user}")
            )

    async def _create_staging_tables(self) -> None:
        """Create staging schema tables."""
        self.logger.info("Creating staging tables...")

        async with self.engine.begin() as conn:
            await conn.run_sync(StgBase.metadata.create_all)

    async def _create_ods_tables(self) -> None:
        """Create ODS schema tables."""
        self.logger.info("Creating ODS tables...")

        async with self.engine.begin() as conn:
            await conn.run_sync(OdsBase.metadata.create_all)

    async def _create_dm_tables(self) -> None:
        """Create DM schema tables."""
        self.logger.info("Creating DM tables...")

        async with self.engine.begin() as conn:
            await conn.run_sync(DmBase.metadata.create_all)

    async def create_initial_dm_data(self) -> None:
        """Create initial data mart aggregations."""
        self.logger.info("Creating initial data mart aggregations...")

        try:
            await self._create_daily_trading_metrics()
            await self._create_daily_staking_metrics()
            await self._create_kpi_summary()

        except Exception as e:
            self.logger.warning(f"Failed to create initial DM data: {e}")

    async def _create_daily_trading_metrics(self) -> None:
        """Create daily trading metrics from ODS data."""
        async with db_manager.get_session() as session:
            await session.execute(
                """
                INSERT INTO dm.trading_metrics_daily (
                    date, total_volume_usd, total_swaps, unique_traders, active_pools,
                    avg_swap_size_usd, etl_batch_id
                )
                SELECT 
                    DATE(timestamp) as date,
                    COALESCE(SUM(volume_usd), 0) as total_volume_usd,
                    COUNT(*) as total_swaps,
                    COUNT(DISTINCT trader_address) as unique_traders,
                    COUNT(DISTINCT pool_address) as active_pools,
                    COALESCE(AVG(volume_usd), 0) as avg_swap_size_usd,
                    'initial_load'
                FROM ods.swaps
                WHERE is_valid = true
                GROUP BY DATE(timestamp)
                ON CONFLICT (date) DO UPDATE SET
                    total_volume_usd = EXCLUDED.total_volume_usd,
                    total_swaps = EXCLUDED.total_swaps,
                    unique_traders = EXCLUDED.unique_traders,
                    active_pools = EXCLUDED.active_pools,
                    avg_swap_size_usd = EXCLUDED.avg_swap_size_usd,
                    updated_at = NOW()
            """
            )
            await session.commit()

    async def _create_daily_staking_metrics(self) -> None:
        """Create daily staking metrics from ODS data."""
        async with db_manager.get_session() as session:
            await session.execute(
                """
                INSERT INTO dm.staking_metrics_daily (
                    date, unique_stakers, new_stakes, unstakes, claims,
                    total_staked_amount, total_unstaked_amount, total_claimed_amount,
                    net_staking_flow, etl_batch_id
                )
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(DISTINCT staker_address) as unique_stakers,
                    COUNT(*) FILTER (WHERE event_type = 'stake') as new_stakes,
                    COUNT(*) FILTER (WHERE event_type = 'unstake') as unstakes,
                    COUNT(*) FILTER (WHERE event_type = 'claim') as claims,
                    COALESCE(SUM(amount) FILTER (WHERE event_type = 'stake'), 0) as total_staked_amount,
                    COALESCE(SUM(amount) FILTER (WHERE event_type = 'unstake'), 0) as total_unstaked_amount,
                    COALESCE(SUM(amount) FILTER (WHERE event_type = 'claim'), 0) as total_claimed_amount,
                    COALESCE(SUM(amount) FILTER (WHERE event_type = 'stake'), 0) - 
                    COALESCE(SUM(amount) FILTER (WHERE event_type = 'unstake'), 0) as net_staking_flow,
                    'initial_load'
                FROM ods.staking_events
                WHERE is_valid = true
                GROUP BY DATE(timestamp)
                ON CONFLICT (date) DO UPDATE SET
                    unique_stakers = EXCLUDED.unique_stakers,
                    new_stakes = EXCLUDED.new_stakes,
                    unstakes = EXCLUDED.unstakes,
                    claims = EXCLUDED.claims,
                    total_staked_amount = EXCLUDED.total_staked_amount,
                    total_unstaked_amount = EXCLUDED.total_unstaked_amount,
                    total_claimed_amount = EXCLUDED.total_claimed_amount,
                    net_staking_flow = EXCLUDED.net_staking_flow,
                    updated_at = NOW()
            """
            )
            await session.commit()

    async def _create_kpi_summary(self) -> None:
        """Create KPI summary from aggregated data."""
        async with db_manager.get_session() as session:
            await session.execute(
                """
                INSERT INTO dm.kpi_summary (
                    date, total_volume_usd_24h, total_swaps_24h, unique_traders_24h,
                    unique_stakers, etl_batch_id
                )
                SELECT 
                    CURRENT_DATE as date,
                    COALESCE(SUM(total_volume_usd), 0) as total_volume_usd_24h,
                    COALESCE(SUM(total_swaps), 0) as total_swaps_24h,
                    COALESCE(SUM(unique_traders), 0) as unique_traders_24h,
                    (SELECT COUNT(DISTINCT staker_address) FROM ods.staking_events WHERE is_valid = true) as unique_stakers,
                    'initial_load'
                FROM dm.trading_metrics_daily
                WHERE date >= CURRENT_DATE - INTERVAL '1 day'
                ON CONFLICT (date) DO UPDATE SET
                    total_volume_usd_24h = EXCLUDED.total_volume_usd_24h,
                    total_swaps_24h = EXCLUDED.total_swaps_24h,
                    unique_traders_24h = EXCLUDED.unique_traders_24h,
                    unique_stakers = EXCLUDED.unique_stakers,
                    updated_at = NOW()
            """
            )
            await session.commit()


async def initialize_database() -> None:
    """Initialize database with all schemas and tables."""
    initializer = DatabaseInitializer()
    await initializer.initialize_database()
    await initializer.migrate_to_new_schema()
    await initializer.create_initial_dm_data()


async def init_database(database_url: Optional[str] = None) -> None:
    """Initialize database schema.

    Args:
        database_url: Database URL override
    """
    initializer = DatabaseInitializer(database_url)
    await initializer.create_tables()


async def reset_database(database_url: Optional[str] = None) -> None:
    """Reset database schema.

    Args:
        database_url: Database URL override
    """
    initializer = DatabaseInitializer(database_url)
    await initializer.reset_database()


if __name__ == "__main__":
    asyncio.run(initialize_database())
