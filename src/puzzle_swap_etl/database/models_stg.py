"""STG schema models for raw blockchain data."""

from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class StgBase(DeclarativeBase):
    """Base class for staging schema models."""

    pass


class StgTransaction(StgBase):
    """Raw blockchain transaction data in staging."""

    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_stg_transactions_height", "height"),
        Index("ix_stg_transactions_timestamp", "timestamp"),
        Index("ix_stg_transactions_sender", "sender"),
        Index("ix_stg_transactions_type", "type"),
        Index("ix_stg_transactions_processed", "processed"),
        Index("ix_stg_transactions_etl_batch_id", "etl_batch_id"),
        {"schema": "stg"},
    )

    id = Column(String(44), primary_key=True)
    height = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    sender = Column(String(35), nullable=False)
    type = Column(Integer, nullable=False)
    fee = Column(Numeric(20, 8))
    application_status = Column(String(20))
    raw_data = Column(JSONB, nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ETL metadata
    etl_batch_id = Column(String(50))
    etl_loaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class StgPriceData(StgBase):
    """Raw price data from external APIs."""

    __tablename__ = "price_data"
    __table_args__ = (
        Index("ix_stg_price_data_asset_id", "asset_id"),
        Index("ix_stg_price_data_fetched_at", "fetched_at"),
        Index("ix_stg_price_data_source", "source"),
        {"schema": "stg"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(44), nullable=False)
    price_usd = Column(Numeric(20, 8), nullable=False)
    source = Column(String(50), nullable=False)  # 'aggregator', 'coingecko', etc.
    raw_response = Column(JSONB, nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

    # ETL metadata
    etl_batch_id = Column(String(50))
    etl_loaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class StgAssetInfo(StgBase):
    """Raw asset information from blockchain."""

    __tablename__ = "asset_info"
    __table_args__ = (
        Index("ix_stg_asset_info_symbol", "symbol"),
        Index("ix_stg_asset_info_issuer", "issuer"),
        {"schema": "stg"},
    )

    id = Column(String(44), primary_key=True)
    name = Column(String(100))
    symbol = Column(String(20))
    decimals = Column(Integer)
    description = Column(Text)
    issuer = Column(String(35))
    total_supply = Column(Numeric(30, 8))
    reissuable = Column(Boolean)
    raw_data = Column(JSONB, nullable=False)

    # ETL metadata
    etl_batch_id = Column(String(50))
    etl_loaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class StgPoolInfo(StgBase):
    """Raw pool information from Puzzle Swap API."""

    __tablename__ = "pool_info"
    __table_args__ = (
        Index("ix_stg_pool_info_asset_a_id", "asset_a_id"),
        Index("ix_stg_pool_info_asset_b_id", "asset_b_id"),
        {"schema": "stg"},
    )

    address = Column(String(35), primary_key=True)
    asset_a_id = Column(String(44), nullable=False)
    asset_b_id = Column(String(44), nullable=False)
    name = Column(String(100))
    fee_rate = Column(Numeric(10, 8))
    active = Column(Boolean)
    raw_data = Column(JSONB, nullable=False)

    # ETL metadata
    etl_batch_id = Column(String(50))
    etl_loaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
