"""ODS schema models for cleaned and validated data."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class OdsBase(DeclarativeBase):
    """Base class for ODS schema models."""

    pass


class OdsTransaction(OdsBase):
    """Cleaned and validated transaction data."""

    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_ods_transactions_height", "height"),
        Index("ix_ods_transactions_timestamp", "timestamp"),
        Index("ix_ods_transactions_sender", "sender"),
        Index("ix_ods_transactions_type", "type"),
        Index("ix_ods_transactions_is_puzzle_related", "is_puzzle_related"),
        Index("ix_ods_transactions_function_name", "function_name"),
        Index("ix_ods_transactions_etl_batch_id", "etl_batch_id"),
        {"schema": "ods"},
    )

    id: Mapped[str] = mapped_column(String(44), primary_key=True)
    height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sender: Mapped[str] = mapped_column(String(35), nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    application_status: Mapped[str] = mapped_column(String(20), nullable=False)

    # Cleaned and enriched data
    is_puzzle_related: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    function_name: Mapped[Optional[str]] = mapped_column(String(50))
    contract_address: Mapped[Optional[str]] = mapped_column(String(35))

    # Data quality flags
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(
        String(50), default="waves_blockchain", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsSwap(OdsBase):
    """Cleaned and validated swap transaction data."""

    __tablename__ = "swaps"
    __table_args__ = (
        Index("ix_ods_swaps_timestamp", "timestamp"),
        Index("ix_ods_swaps_pool_address", "pool_address"),
        Index("ix_ods_swaps_trader_address", "trader_address"),
        Index("ix_ods_swaps_asset_in_id", "asset_in_id"),
        Index("ix_ods_swaps_asset_out_id", "asset_out_id"),
        Index("ix_ods_swaps_volume_usd", "volume_usd"),
        Index("ix_ods_swaps_etl_batch_id", "etl_batch_id"),
        {"schema": "ods"},
    )

    id: Mapped[str] = mapped_column(String(150), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(44), nullable=False)
    height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pool_address: Mapped[str] = mapped_column(String(35), nullable=False)
    trader_address: Mapped[str] = mapped_column(String(35), nullable=False)

    # Asset information
    asset_in_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_out_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_in_symbol: Mapped[Optional[str]] = mapped_column(String(20))
    asset_out_symbol: Mapped[Optional[str]] = mapped_column(String(20))

    # Amounts (normalized to proper decimals)
    amount_in: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    amount_out: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    amount_in_raw: Mapped[Decimal] = mapped_column(
        Numeric(30, 0), nullable=False
    )  # Raw blockchain amount
    amount_out_raw: Mapped[Decimal] = mapped_column(
        Numeric(30, 0), nullable=False
    )  # Raw blockchain amount

    # USD values
    amount_in_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    amount_out_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Fees
    pool_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    protocol_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Price information
    price_impact: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(30, 8))

    # Data quality
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(
        String(50), default="waves_blockchain", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsStakingEvent(OdsBase):
    """Cleaned and validated staking events."""

    __tablename__ = "staking_events"
    __table_args__ = (
        Index("ix_ods_staking_events_timestamp", "timestamp"),
        Index("ix_ods_staking_events_staker_address", "staker_address"),
        Index("ix_ods_staking_events_event_type", "event_type"),
        Index("ix_ods_staking_events_etl_batch_id", "etl_batch_id"),
        {"schema": "ods"},
    )

    id: Mapped[str] = mapped_column(String(150), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(44), nullable=False)
    height: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staker_address: Mapped[str] = mapped_column(String(35), nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'stake', 'unstake', 'claim', 'stake_update'

    # Amounts
    amount: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    amount_raw: Mapped[Decimal] = mapped_column(
        Numeric(30, 0), nullable=False
    )  # Raw blockchain amount
    amount_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Additional context
    total_staked_after: Mapped[Optional[Decimal]] = mapped_column(Numeric(30, 8))
    reward_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(30, 8))

    # Data quality
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(
        String(50), default="waves_blockchain", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsAsset(OdsBase):
    """Cleaned and validated asset information."""

    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_ods_assets_symbol", "symbol"),
        Index("ix_ods_assets_asset_type", "asset_type"),
        Index("ix_ods_assets_is_verified", "is_verified"),
        Index("ix_ods_assets_etl_batch_id", "etl_batch_id"),
        {"schema": "ods"},
    )

    id: Mapped[str] = mapped_column(String(44), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    issuer: Mapped[Optional[str]] = mapped_column(String(35))
    total_supply: Mapped[Optional[Decimal]] = mapped_column(Numeric(30, 8))
    reissuable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Classification
    asset_type: Mapped[str] = mapped_column(
        String(20), default="token", nullable=False
    )  # 'token', 'nft', 'stable'
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Data quality
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(
        String(50), default="waves_blockchain", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsPool(OdsBase):
    """Cleaned and validated pool information."""

    __tablename__ = "pools"
    __table_args__ = (
        Index("ix_ods_pools_asset_a_id", "asset_a_id"),
        Index("ix_ods_pools_asset_b_id", "asset_b_id"),
        Index("ix_ods_pools_active", "active"),
        Index("ix_ods_pools_total_volume_usd", "total_volume_usd"),
        Index("ix_ods_pools_etl_batch_id", "etl_batch_id"),
        {"schema": "ods"},
    )

    address: Mapped[str] = mapped_column(String(35), primary_key=True)
    asset_a_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_b_id: Mapped[str] = mapped_column(String(44), nullable=False)
    asset_a_symbol: Mapped[Optional[str]] = mapped_column(String(20))
    asset_b_symbol: Mapped[Optional[str]] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fee_rate: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Pool metrics
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    total_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Data quality
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)

    # ETL metadata
    etl_batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_system: Mapped[str] = mapped_column(
        String(50), default="puzzle_api", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsSwapPair(OdsBase):
    """Aggregated swap pair statistics."""

    __tablename__ = "swap_pairs"
    __table_args__ = (
        Index("ix_ods_swap_pairs_asset_a_id", "asset_a_id"),
        Index("ix_ods_swap_pairs_asset_b_id", "asset_b_id"),
        Index("ix_ods_swap_pairs_total_volume_usd", "total_volume_usd"),
        Index("ix_ods_swap_pairs_is_active", "is_active"),
        {"schema": "ods"},
    )

    asset_a_id: Mapped[str] = mapped_column(String(44), primary_key=True)
    asset_b_id: Mapped[str] = mapped_column(String(44), primary_key=True)
    pool_address: Mapped[str] = mapped_column(String(35), primary_key=True)

    pair_name: Mapped[str] = mapped_column(String(50), nullable=False)
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=0, nullable=False
    )
    swap_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fee_rate: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ETL metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OdsAssetPrice(OdsBase):
    """Asset price information."""

    __tablename__ = "asset_prices"
    __table_args__ = (
        Index("ix_ods_asset_prices_asset_id", "asset_id"),
        Index("ix_ods_asset_prices_timestamp", "timestamp"),
        Index("ix_ods_asset_prices_source", "source"),
        {"schema": "ods"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[str] = mapped_column(String(44), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    # Price metadata
    volume_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    market_cap: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    price_change_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # ETL metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OdsProtocolAllocation(OdsBase):
    """Protocol allocation information."""

    __tablename__ = "protocol_allocations"
    __table_args__ = (
        Index("ix_ods_protocol_allocations_protocol_address", "protocol_address"),
        Index("ix_ods_protocol_allocations_asset_id", "asset_id"),
        Index("ix_ods_protocol_allocations_timestamp", "timestamp"),
        {"schema": "ods"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_address: Mapped[str] = mapped_column(String(35), nullable=False)
    protocol_name: Mapped[str] = mapped_column(String(100), nullable=False)
    protocol_type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(44), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    amount_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ETL metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OdsLendingInfo(OdsBase):
    """Lending protocol information."""

    __tablename__ = "lending_info"
    __table_args__ = (
        Index("ix_ods_lending_info_protocol_address", "protocol_address"),
        Index("ix_ods_lending_info_asset_id", "asset_id"),
        Index("ix_ods_lending_info_timestamp", "timestamp"),
        {"schema": "ods"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_address: Mapped[str] = mapped_column(String(35), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(44), nullable=False)
    total_supplied: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    total_borrowed: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    supply_rate: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    borrow_rate: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    utilization_rate: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ETL metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
