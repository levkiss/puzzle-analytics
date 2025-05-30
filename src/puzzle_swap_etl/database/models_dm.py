"""DM schema models for data marts and aggregated analytics."""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DmBase(DeclarativeBase):
    """Base class for DM schema models."""

    pass


class DmTradingMetricsDaily(DmBase):
    """Daily trading metrics aggregation."""

    __tablename__ = "trading_metrics_daily"
    __table_args__ = (
        Index("ix_dm_trading_metrics_daily_date", "date", unique=True),
        Index("ix_dm_trading_metrics_daily_total_volume_usd", "total_volume_usd"),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Volume metrics
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_traders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Pool metrics
    active_pools: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Average metrics
    avg_swap_size_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    median_swap_size_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Top assets by volume
    top_asset_by_volume_id: Mapped[Optional[str]] = mapped_column(String(44))
    top_asset_by_volume_symbol: Mapped[Optional[str]] = mapped_column(String(20))
    top_asset_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DmStakingMetricsDaily(DmBase):
    """Daily staking metrics aggregation."""

    __tablename__ = "staking_metrics_daily"
    __table_args__ = (
        Index("ix_dm_staking_metrics_daily_date", "date", unique=True),
        Index("ix_dm_staking_metrics_daily_total_staked", "total_staked"),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Staking metrics
    total_staked: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )
    total_staked_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    unique_stakers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Daily activity
    new_stakes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unstakes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Amounts
    total_staked_amount: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )
    total_unstaked_amount: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )
    total_claimed_amount: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )

    # Net flow
    net_staking_flow: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )
    net_staking_flow_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DmPoolMetrics(DmBase):
    """Pool performance metrics."""

    __tablename__ = "pool_metrics"
    __table_args__ = (
        Index("ix_dm_pool_metrics_pool_address", "pool_address"),
        Index("ix_dm_pool_metrics_period", "period_type", "period_start", "period_end"),
        Index("ix_dm_pool_metrics_volume", "total_volume_usd"),
        Index(
            "ix_dm_pool_metrics_unique",
            "pool_address",
            "period_type",
            "period_start",
            unique=True,
        ),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pool_address: Mapped[str] = mapped_column(String(35), nullable=False)
    asset_a_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_b_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_a_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_b_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    pool_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Time period
    period_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'daily', 'weekly', 'monthly'
    period_start: Mapped[date_type] = mapped_column(Date, nullable=False)
    period_end: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Volume metrics
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_traders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Fee metrics
    total_fees_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    avg_fee_per_swap: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Performance metrics
    avg_swap_size_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    largest_swap_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Rankings
    volume_rank: Mapped[Optional[int]] = mapped_column(Integer)
    swap_count_rank: Mapped[Optional[int]] = mapped_column(Integer)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DmTraderMetrics(DmBase):
    """Trader performance metrics."""

    __tablename__ = "trader_metrics"
    __table_args__ = (
        Index("ix_dm_trader_metrics_trader_address", "trader_address"),
        Index(
            "ix_dm_trader_metrics_period", "period_type", "period_start", "period_end"
        ),
        Index("ix_dm_trader_metrics_volume", "total_volume_usd"),
        Index(
            "ix_dm_trader_metrics_unique",
            "trader_address",
            "period_type",
            "period_start",
            unique=True,
        ),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trader_address: Mapped[str] = mapped_column(String(35), nullable=False)

    # Time period
    period_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'daily', 'weekly', 'monthly', 'all_time'
    period_start: Mapped[Optional[date_type]] = mapped_column(Date)
    period_end: Mapped[Optional[date_type]] = mapped_column(Date)

    # Trading metrics
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_pools_traded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_assets_traded: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Performance metrics
    avg_swap_size_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    largest_swap_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    total_fees_paid_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )

    # Activity metrics
    first_trade_date: Mapped[Optional[date_type]] = mapped_column(Date)
    last_trade_date: Mapped[Optional[date_type]] = mapped_column(Date)
    trading_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rankings
    volume_rank: Mapped[Optional[int]] = mapped_column(Integer)
    swap_count_rank: Mapped[Optional[int]] = mapped_column(Integer)

    # Classification
    trader_tier: Mapped[str] = mapped_column(
        String(20), default="bronze", nullable=False
    )  # bronze, silver, gold, platinum
    is_whale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DmAssetMetrics(DmBase):
    """Asset trading metrics."""

    __tablename__ = "asset_metrics"
    __table_args__ = (
        Index("ix_dm_asset_metrics_asset_id", "asset_id"),
        Index(
            "ix_dm_asset_metrics_period", "period_type", "period_start", "period_end"
        ),
        Index("ix_dm_asset_metrics_volume", "total_volume_usd"),
        Index(
            "ix_dm_asset_metrics_unique",
            "asset_id",
            "period_type",
            "period_start",
            unique=True,
        ),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Time period
    period_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 'daily', 'weekly', 'monthly'
    period_start: Mapped[date_type] = mapped_column(Date, nullable=False)
    period_end: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Trading metrics
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_traders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_pools: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Price metrics
    avg_price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    min_price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    max_price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    price_volatility: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))

    # Volume distribution
    volume_as_input_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    volume_as_output_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )

    # Rankings
    volume_rank: Mapped[Optional[int]] = mapped_column(Integer)
    trader_count_rank: Mapped[Optional[int]] = mapped_column(Integer)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DmKpiSummary(DmBase):
    """Key Performance Indicators summary."""

    __tablename__ = "kpi_summary"
    __table_args__ = (
        Index("ix_dm_kpi_summary_date", "date", unique=True),
        Index("ix_dm_kpi_summary_total_volume_usd_24h", "total_volume_usd_24h"),
        {"schema": "dm"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Trading KPIs
    total_volume_usd_24h: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_volume_usd_7d: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_volume_usd_30d: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps_24h: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_traders_24h: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Staking KPIs
    total_staked: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=0, nullable=False
    )
    total_staked_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    unique_stakers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    staking_apy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Platform KPIs
    total_pools: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_pools_24h: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_assets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Growth metrics
    volume_growth_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    trader_growth_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    staking_growth_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
