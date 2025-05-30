"""Database loader module for saving processed data to PostgreSQL."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from puzzle_swap_etl.database import db_manager
from puzzle_swap_etl.database.models_ods import (
    OdsAsset,
    OdsAssetPrice,
    OdsPool,
    OdsProtocolAllocation,
    OdsStakingEvent,
    OdsSwap,
    OdsSwapPair,
)
from puzzle_swap_etl.database.models_stg import (
    StgAssetInfo,
    StgPoolInfo,
    StgPriceData,
    StgTransaction,
)
from puzzle_swap_etl.models import AssetInfo, PoolInfo, StakingEventData, SwapData
from puzzle_swap_etl.utils import LoggerMixin


class DatabaseLoader(LoggerMixin):
    """Loads processed data into PostgreSQL database using 3-layer architecture."""

    async def save_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Save raw transactions to STG schema.

        Args:
            transactions: List of raw transaction data
        """
        context = self.log_operation(
            "save_transactions",
            transaction_count=len(transactions),
        )

        try:
            async with db_manager.get_session() as session:
                for tx_data in transactions:
                    # Save to STG schema (raw data)
                    stmt = insert(StgTransaction).values(
                        id=tx_data["id"],
                        height=tx_data["height"],
                        timestamp=datetime.fromtimestamp(tx_data["timestamp"] / 1000),
                        sender=tx_data["sender"],
                        type=tx_data["type"],
                        fee=(
                            Decimal(tx_data.get("fee", 0)) / (10**8)
                            if tx_data.get("fee")
                            else None
                        ),
                        application_status=tx_data.get("applicationStatus"),
                        raw_data=tx_data,
                        processed=False,
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_swaps(self, swaps: List[SwapData]) -> None:
        """Save swap data to ODS schema.

        Args:
            swaps: List of swap data
        """
        context = self.log_operation(
            "save_swaps",
            swap_count=len(swaps),
        )

        try:
            async with db_manager.get_session() as session:
                for swap_data in swaps:
                    # Save to ODS schema (processed data)
                    stmt = insert(OdsSwap).values(
                        id=swap_data.id,
                        transaction_id=swap_data.transaction_id,
                        height=swap_data.height,
                        timestamp=swap_data.timestamp,
                        pool_address=swap_data.pool_address,
                        trader_address=swap_data.trader_address,
                        asset_in_id=swap_data.asset_in_id,
                        asset_out_id=swap_data.asset_out_id,
                        amount_in=swap_data.amount_in,
                        amount_out=swap_data.amount_out,
                        amount_in_usd=swap_data.amount_in_usd,
                        amount_out_usd=swap_data.amount_out_usd,
                        volume_usd=swap_data.volume_usd,
                        pool_fee=swap_data.pool_fee,
                        protocol_fee=swap_data.protocol_fee,
                        owner_fee=getattr(swap_data, "owner_fee", None),
                        swap_fee_rate=getattr(swap_data, "swap_fee_rate", None),
                        price_impact=getattr(swap_data, "price_impact", None),
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_staking_events(self, events: List[StakingEventData]) -> None:
        """Save staking events to ODS schema.

        Args:
            events: List of staking events
        """
        context = self.log_operation(
            "save_staking_events",
            event_count=len(events),
        )

        try:
            async with db_manager.get_session() as session:
                for event_data in events:
                    # Save to ODS schema (processed data)
                    stmt = insert(OdsStakingEvent).values(
                        id=event_data.id,
                        transaction_id=event_data.transaction_id,
                        height=event_data.height,
                        timestamp=event_data.timestamp,
                        staker_address=event_data.staker_address,
                        event_type=event_data.event_type,
                        amount=event_data.amount,
                        amount_raw=getattr(
                            event_data, "amount_raw", event_data.amount * 100000000
                        ),  # Convert to raw amount
                        amount_usd=event_data.amount_usd,
                        total_staked_after=getattr(
                            event_data, "total_staked_after", None
                        ),
                        reward_amount=getattr(event_data, "reward_amount", None),
                        etl_batch_id=getattr(
                            event_data, "etl_batch_id", "default_batch"
                        ),
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_assets(self, assets: List[AssetInfo]) -> None:
        """Save asset information to STG schema.

        Args:
            assets: List of asset information
        """
        context = self.log_operation(
            "save_assets",
            asset_count=len(assets),
        )

        try:
            async with db_manager.get_session() as session:
                for asset_data in assets:
                    # Save to STG schema (raw data)
                    stmt = insert(StgAssetInfo).values(
                        id=asset_data.id,
                        name=asset_data.name,
                        symbol=getattr(asset_data, "symbol", None),
                        decimals=asset_data.decimals,
                        description=getattr(asset_data, "description", None),
                        issuer=getattr(asset_data, "issuer", None),
                        total_supply=getattr(asset_data, "total_supply", None),
                        reissuable=getattr(asset_data, "reissuable", None),
                        raw_data=(
                            asset_data.dict() if hasattr(asset_data, "dict") else {}
                        ),
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_pools(self, pools: List[PoolInfo]) -> None:
        """Save pool information to STG schema.

        Args:
            pools: List of pool information
        """
        context = self.log_operation(
            "save_pools",
            pool_count=len(pools),
        )

        try:
            async with db_manager.get_session() as session:
                for pool_data in pools:
                    # Save to STG schema (raw data)
                    stmt = insert(StgPoolInfo).values(
                        address=pool_data.address,
                        asset_a_id=pool_data.asset_a_id,
                        asset_b_id=pool_data.asset_b_id,
                        name=getattr(pool_data, "name", None),
                        fee_rate=getattr(pool_data, "fee_rate", None),
                        active=getattr(pool_data, "active", True),
                        raw_data=pool_data.dict() if hasattr(pool_data, "dict") else {},
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["address"])
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_price_data(self, price_data: List[Dict[str, Any]]) -> None:
        """Save price data to STG schema.

        Args:
            price_data: List of price data
        """
        context = self.log_operation(
            "save_price_data",
            price_count=len(price_data),
        )

        try:
            async with db_manager.get_session() as session:
                for price_info in price_data:
                    # Save to STG schema (raw data)
                    stmt = insert(StgPriceData).values(
                        asset_id=price_info["asset_id"],
                        price_usd=price_info["price_usd"],
                        source=price_info["source"],
                        raw_response=price_info.get("raw_response", {}),
                        fetched_at=price_info["fetched_at"],
                    )
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_swap_pairs(self, pairs: List[Dict[str, Any]]) -> None:
        """Save swap pair information to ODS schema.

        Args:
            pairs: List of swap pair data
        """
        context = self.log_operation(
            "save_swap_pairs",
            pair_count=len(pairs),
        )

        try:
            async with db_manager.get_session() as session:
                for pair_data in pairs:
                    stmt = insert(OdsSwapPair).values(
                        asset_a_id=pair_data["asset_a_id"],
                        asset_b_id=pair_data["asset_b_id"],
                        pool_address=pair_data["pool_address"],
                        pair_name=pair_data.get("pair_name"),
                        fee_rate=pair_data.get("fee_rate"),
                        active=pair_data.get("active", True),
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["asset_a_id", "asset_b_id", "pool_address"],
                        set_=dict(
                            pair_name=stmt.excluded.pair_name,
                            fee_rate=stmt.excluded.fee_rate,
                            active=stmt.excluded.active,
                            updated_at=func.now(),
                        ),
                    )
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_protocol_allocations(
        self, allocations: List[Dict[str, Any]]
    ) -> None:
        """Save protocol allocation data to ODS schema.

        Args:
            allocations: List of protocol allocation data
        """
        context = self.log_operation(
            "save_protocol_allocations",
            allocation_count=len(allocations),
        )

        try:
            async with db_manager.get_session() as session:
                for allocation_data in allocations:
                    stmt = insert(OdsProtocolAllocation).values(
                        protocol_address=allocation_data["protocol_address"],
                        protocol_name=allocation_data["protocol_name"],
                        protocol_type=allocation_data["protocol_type"],
                        asset_id=allocation_data["asset_id"],
                        amount=Decimal(str(allocation_data["amount"])),
                        amount_usd=(
                            Decimal(str(allocation_data["amount_usd"]))
                            if allocation_data.get("amount_usd")
                            else None
                        ),
                        timestamp=allocation_data["timestamp"],
                    )
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def mark_transactions_processed(self, transaction_ids: List[str]) -> None:
        """Mark transactions as processed in STG schema.

        Args:
            transaction_ids: List of transaction IDs to mark as processed
        """
        context = self.log_operation(
            "mark_transactions_processed",
            transaction_count=len(transaction_ids),
        )

        try:
            async with db_manager.get_session() as session:
                stmt = (
                    update(StgTransaction)
                    .where(StgTransaction.id.in_(transaction_ids))
                    .values(processed=True)
                )
                await session.execute(stmt)
                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_processed_assets_to_ods(self, assets: List[AssetInfo]) -> None:
        """Save processed asset information to ODS schema.

        Args:
            assets: List of processed asset information
        """
        context = self.log_operation(
            "save_processed_assets_to_ods",
            asset_count=len(assets),
        )

        try:
            async with db_manager.get_session() as session:
                for asset_data in assets:
                    # Save to ODS schema (processed data)
                    stmt = insert(OdsAsset).values(
                        id=asset_data.id,
                        name=asset_data.name,
                        symbol=getattr(asset_data, "symbol", asset_data.name[:10]),
                        decimals=asset_data.decimals,
                        description=getattr(asset_data, "description", None),
                        issuer=getattr(asset_data, "issuer", None),
                        total_supply=getattr(asset_data, "total_supply", None),
                        reissuable=getattr(asset_data, "reissuable", False),
                        asset_type=getattr(asset_data, "asset_type", "token"),
                        is_verified=getattr(asset_data, "is_verified", False),
                        etl_batch_id="default_batch",
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["id"],
                        set_=dict(
                            name=stmt.excluded.name,
                            symbol=stmt.excluded.symbol,
                            description=stmt.excluded.description,
                            issuer=stmt.excluded.issuer,
                            total_supply=stmt.excluded.total_supply,
                            reissuable=stmt.excluded.reissuable,
                            asset_type=stmt.excluded.asset_type,
                            is_verified=stmt.excluded.is_verified,
                            updated_at=func.now(),
                        ),
                    )
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def save_processed_pools_to_ods(self, pools: List[PoolInfo]) -> None:
        """Save processed pool information to ODS schema.

        Args:
            pools: List of processed pool information
        """
        context = self.log_operation(
            "save_processed_pools_to_ods",
            pool_count=len(pools),
        )

        try:
            async with db_manager.get_session() as session:
                for pool_data in pools:
                    # Save to ODS schema (processed data)
                    stmt = insert(OdsPool).values(
                        address=pool_data.address,
                        asset_a_id=pool_data.asset_a_id,
                        asset_b_id=pool_data.asset_b_id,
                        name=getattr(
                            pool_data,
                            "name",
                            f"{pool_data.asset_a_id}/{pool_data.asset_b_id}",
                        ),
                        fee_rate=getattr(pool_data, "fee_rate", Decimal("0.003")),
                        active=getattr(pool_data, "active", True),
                        total_volume_usd=Decimal("0"),
                        total_swaps=0,
                        etl_batch_id="default_batch",
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["address"],
                        set_=dict(
                            name=stmt.excluded.name,
                            fee_rate=stmt.excluded.fee_rate,
                            active=stmt.excluded.active,
                            total_volume_usd=stmt.excluded.total_volume_usd,
                            total_swaps=stmt.excluded.total_swaps,
                            etl_batch_id=stmt.excluded.etl_batch_id,
                            updated_at=func.now(),
                        ),
                    )
                    await session.execute(stmt)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def calculate_and_save_aggregated_data(self) -> None:
        """Calculate aggregated statistics from STG data and save to ODS schema."""
        context = self.log_operation("calculate_and_save_aggregated_data")

        try:
            async with db_manager.get_session() as session:
                # Calculate swap pair statistics
                await self._calculate_swap_pair_stats(session)

                # Calculate asset price aggregations
                await self._calculate_asset_price_stats(session)

                # Calculate protocol allocation stats
                await self._calculate_protocol_allocation_stats(session)

                await session.commit()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _calculate_swap_pair_stats(self, session: AsyncSession) -> None:
        """Calculate swap pair statistics from swap data."""
        # Get all unique swap pairs from ODS swaps
        result = await session.execute(
            select(
                OdsSwap.asset_in_id,
                OdsSwap.asset_out_id,
                OdsSwap.pool_address,
                func.count().label("total_swaps"),
                func.sum(OdsSwap.volume_usd).label("total_volume_usd"),
                func.max(OdsSwap.timestamp).label("last_swap_time"),
            )
            .where(OdsSwap.volume_usd.is_not(None))
            .group_by(OdsSwap.asset_in_id, OdsSwap.asset_out_id, OdsSwap.pool_address)
        )

        for row in result:
            # Normalize asset pair order (smaller asset ID first)
            asset_a_id = min(row.asset_in_id, row.asset_out_id)
            asset_b_id = max(row.asset_in_id, row.asset_out_id)

            # Upsert swap pair statistics
            stmt = insert(OdsSwapPair).values(
                asset_a_id=asset_a_id,
                asset_b_id=asset_b_id,
                pool_address=row.pool_address,
                pair_name=f"{asset_a_id[:8]}/{asset_b_id[:8]}",
                total_volume_usd=row.total_volume_usd or Decimal("0"),
                swap_count=row.total_swaps,
                fee_rate=Decimal("0.003"),  # Default fee rate
                is_active=True,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["asset_a_id", "asset_b_id", "pool_address"],
                set_=dict(
                    swap_count=stmt.excluded.swap_count,
                    total_volume_usd=stmt.excluded.total_volume_usd,
                    updated_at=func.now(),
                ),
            )
            await session.execute(stmt)

    async def _calculate_asset_price_stats(self, session: AsyncSession) -> None:
        """Calculate asset price statistics from price data."""
        # Get latest prices for each asset
        result = await session.execute(
            select(
                StgPriceData.asset_id,
                func.avg(StgPriceData.price_usd).label("avg_price"),
                func.max(StgPriceData.fetched_at).label("last_update"),
            ).group_by(StgPriceData.asset_id)
        )

        for row in result:
            # Upsert asset price statistics
            stmt = insert(OdsAssetPrice).values(
                asset_id=row.asset_id,
                timestamp=row.last_update,
                price_usd=row.avg_price or Decimal("0"),
                source="aggregated",
                volume_24h=Decimal("0"),  # Would need additional calculation
                market_cap=None,
            )
            # Note: OdsAssetPrice uses auto-increment ID, so we can't use on_conflict_do_update easily
            # We'll just insert new records for now
            await session.execute(stmt)

    async def _calculate_protocol_allocation_stats(self, session: AsyncSession) -> None:
        """Calculate protocol allocation statistics."""
        # Calculate total staked amounts by staker (simplified version)
        # Since we don't have protocol_address and asset_id in staking events,
        # we'll calculate general staking statistics

        # Get stake events
        stake_result = await session.execute(
            select(
                func.sum(OdsStakingEvent.amount).label("total_staked"),
                func.count(func.distinct(OdsStakingEvent.staker_address)).label(
                    "unique_stakers"
                ),
                func.count().label("stake_events"),
                func.max(OdsStakingEvent.timestamp).label("last_update"),
            ).where(OdsStakingEvent.event_type == "stake")
        )

        # Get unstake events
        unstake_result = await session.execute(
            select(func.sum(OdsStakingEvent.amount).label("total_unstaked")).where(
                OdsStakingEvent.event_type == "unstake"
            )
        )

        stake_row = stake_result.first()
        unstake_row = unstake_result.first()

        if stake_row and stake_row.total_staked and stake_row.total_staked > 0:
            total_staked = stake_row.total_staked - (
                unstake_row.total_unstaked or Decimal("0")
            )

            # Create a general protocol allocation record
            # We'll use a default protocol address since it's not in the staking events
            default_protocol = (
                "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS"  # Puzzle staking address
            )
            default_asset = (
                "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p"  # Puzzle token
            )

            stmt = insert(OdsProtocolAllocation).values(
                protocol_address=default_protocol,
                protocol_name="Puzzle Staking",
                protocol_type="staking",
                asset_id=default_asset,
                amount=total_staked,
                amount_usd=Decimal("0"),  # Would need price calculation
                timestamp=stake_row.last_update,
            )
            # Note: OdsProtocolAllocation uses auto-increment ID, so we'll just insert
            await session.execute(stmt)
