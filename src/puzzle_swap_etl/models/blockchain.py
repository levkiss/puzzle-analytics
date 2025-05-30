"""Pydantic models for blockchain data structures."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WavesTransaction(BaseModel):
    """Waves blockchain transaction model."""

    id: str = Field(..., description="Transaction ID")
    height: int = Field(..., description="Block height")
    timestamp: int = Field(..., description="Transaction timestamp in milliseconds")
    sender: str = Field(..., description="Transaction sender address")
    type: int = Field(..., description="Transaction type")
    fee: Optional[int] = Field(None, description="Transaction fee in wavelets")
    application_status: Optional[str] = Field(None, description="Application status")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw transaction data")

    @property
    def timestamp_dt(self) -> datetime:
        """Get timestamp as datetime object."""
        return datetime.fromtimestamp(self.timestamp / 1000)


class InvokeTransaction(WavesTransaction):
    """Invoke script transaction model."""

    d_app: str = Field(..., alias="dApp", description="dApp address")
    call: Dict[str, Any] = Field(..., description="Function call data")
    payment: List[Dict[str, Any]] = Field(default_factory=list, description="Payments")
    state_changes: Dict[str, Any] = Field(
        default_factory=dict, alias="stateChanges", description="State changes"
    )


class TransferData(BaseModel):
    """Transfer data model."""

    address: str = Field(..., description="Transfer address")
    asset: Optional[str] = Field(None, description="Asset ID (None for WAVES)")
    amount: int = Field(..., description="Transfer amount")


class SwapData(BaseModel):
    """Swap transaction data model."""

    id: str = Field(..., description="Swap ID")
    transaction_id: str = Field(..., description="Transaction ID")
    height: int = Field(..., description="Block height")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    pool_address: str = Field(..., description="Pool address")
    trader_address: str = Field(..., description="Trader address")
    asset_in_id: str = Field(..., description="Input asset ID")
    asset_out_id: str = Field(..., description="Output asset ID")
    amount_in: Decimal = Field(..., description="Input amount")
    amount_out: Decimal = Field(..., description="Output amount")
    amount_in_usd: Optional[Decimal] = Field(None, description="Input amount in USD")
    amount_out_usd: Optional[Decimal] = Field(None, description="Output amount in USD")
    volume_usd: Optional[Decimal] = Field(None, description="Total volume in USD")
    pool_fee: Optional[Decimal] = Field(None, description="Pool fee")
    protocol_fee: Optional[Decimal] = Field(None, description="Protocol fee")


class StakingEventData(BaseModel):
    """Staking event data model."""

    id: str = Field(..., description="Event ID")
    transaction_id: str = Field(..., description="Transaction ID")
    height: int = Field(..., description="Block height")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    staker_address: str = Field(..., description="Staker address")
    event_type: str = Field(..., description="Event type (stake/unstake)")
    amount: Decimal = Field(..., description="Staking amount")
    amount_usd: Optional[Decimal] = Field(None, description="Amount in USD")


class AssetInfo(BaseModel):
    """Asset information model."""

    id: str = Field(..., description="Asset ID")
    name: str = Field(..., description="Asset name")
    symbol: Optional[str] = Field(None, description="Asset symbol")
    decimals: int = Field(..., description="Asset decimals")
    description: Optional[str] = Field(None, description="Asset description")


class PoolInfo(BaseModel):
    """Pool information model."""

    address: str = Field(..., description="Pool address")
    asset_a_id: str = Field(..., description="First asset ID")
    asset_b_id: str = Field(..., description="Second asset ID")
    name: Optional[str] = Field(None, description="Pool name")
    fee_rate: Optional[Decimal] = Field(None, description="Pool fee rate")
    active: bool = Field(default=True, description="Pool active status")


class PriceData(BaseModel):
    """Price data model."""

    asset_id: str = Field(..., description="Asset ID")
    price: Decimal = Field(..., description="Price in USD")
    timestamp: datetime = Field(..., description="Price timestamp")
    source: str = Field(..., description="Price source")
