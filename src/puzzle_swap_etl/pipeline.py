"""Main ETL pipeline orchestrator for Puzzle Swap data processing."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.extractors import BlockchainExtractor
from puzzle_swap_etl.loaders.database import DatabaseLoader
from puzzle_swap_etl.models import (
    AssetInfo,
    PoolInfo,
    StakingEventData,
    SwapData,
    WavesTransaction,
)
from puzzle_swap_etl.transformers import StakingTransformer, SwapTransformer
from puzzle_swap_etl.utils import HTTPClient, LoggerMixin


class PuzzleSwapETL(LoggerMixin):
    """Main ETL pipeline for Puzzle Swap data processing."""

    def __init__(self) -> None:
        """Initialize ETL pipeline."""
        self.extractor: Optional[BlockchainExtractor] = None
        self.swap_transformer = SwapTransformer()
        self.staking_transformer = StakingTransformer()
        self.loader = DatabaseLoader()
        self.http_client: Optional[HTTPClient] = None

    async def __aenter__(self) -> "PuzzleSwapETL":
        """Async context manager entry."""
        self.extractor = BlockchainExtractor()
        await self.extractor.__aenter__()

        self.http_client = HTTPClient()
        await self.http_client.__aenter__()

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.extractor:
            await self.extractor.__aexit__(exc_type, exc_val, exc_tb)
        if self.http_client:
            await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    async def run_pipeline(
        self,
        addresses: Optional[List[str]] = None,
        last_processed_id: str = "",
    ) -> Dict[str, Any]:
        """Run the complete ETL pipeline.

        Args:
            addresses: List of addresses to process (defaults to main addresses)
            last_processed_id: Last processed transaction ID for incremental updates

        Returns:
            Pipeline execution summary
        """
        context = self.log_operation(
            "run_pipeline",
            addresses=addresses or "default",
        )

        try:
            # Use default addresses if none provided
            if not addresses:
                addresses = [
                    settings.puzzle_staking_address,
                    # Add more important addresses here
                ]

            # Save reference data (assets and pools) at the beginning
            await self._save_reference_data()

            summary = {
                "start_time": datetime.utcnow(),
                "addresses_processed": 0,
                "transactions_extracted": 0,
                "swaps_processed": 0,
                "staking_events_processed": 0,
                "errors": [],
            }

            # Process each address with batch processing
            for address in addresses:
                try:
                    address_summary = await self._process_address_with_batches(
                        address, last_processed_id
                    )
                    summary["addresses_processed"] += 1
                    summary["transactions_extracted"] += address_summary[
                        "transactions_extracted"
                    ]
                    summary["swaps_processed"] += address_summary["swaps_processed"]
                    summary["staking_events_processed"] += address_summary[
                        "staking_events_processed"
                    ]

                    self.logger.info(
                        "Address processing completed",
                        address=address,
                        **address_summary,
                    )
                except Exception as e:
                    error_msg = f"Failed to process {address}: {str(e)}"
                    summary["errors"].append(error_msg)
                    self.logger.error(
                        "Address processing failed", address=address, error=str(e)
                    )

            # Update final aggregated statistics
            await self._update_final_statistics()

            summary["end_time"] = datetime.utcnow()
            summary["duration"] = (
                summary["end_time"] - summary["start_time"]
            ).total_seconds()

            self.log_success(context, **summary)
            return summary

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _process_address_with_batches(
        self, address: str, last_processed_id: str = ""
    ) -> Dict[str, Any]:
        """Process an address with batch processing and real-time data saving.

        Args:
            address: Blockchain address
            last_processed_id: Last processed transaction ID

        Returns:
            Processing summary for this address
        """
        if not self.extractor:
            raise RuntimeError("Extractor not initialized")

        context = self.log_operation(
            "process_address_with_batches",
            address=address,
        )

        summary = {
            "transactions_extracted": 0,
            "swaps_processed": 0,
            "staking_events_processed": 0,
            "batches_processed": 0,
        }

        try:
            # Define important function names for different addresses
            vip_functions = []
            if address == settings.puzzle_staking_address:
                vip_functions = ["stake", "unstake", "claim"]
            else:
                vip_functions = ["swap", "swapWithReferral"]

            last_tx_id = ""
            has_more = True
            batch_number = 0

            while has_more:
                # Fetch batch of transactions
                batch, has_more = await self.extractor.fetch_transactions_batch(
                    address=address,
                    after=last_tx_id,
                    last_processed_id=last_processed_id,
                )

                if not batch:
                    break

                # Process transactions to find relevant ones
                relevant_txs = []
                for tx in batch:
                    found_txs = self.extractor._find_relevant_transactions(
                        tx, address, vip_functions
                    )
                    relevant_txs.extend(found_txs)

                if relevant_txs:
                    # Transform data for this batch
                    swaps, staking_events = await self._transform_data(relevant_txs)

                    # Load data to database immediately
                    await self._load_data(swaps, staking_events, relevant_txs)

                    # Update summary
                    summary["transactions_extracted"] += len(relevant_txs)
                    summary["swaps_processed"] += len(swaps)
                    summary["staking_events_processed"] += len(staking_events)

                    self.logger.info(
                        "Batch processed and saved",
                        batch_number=batch_number,
                        transactions=len(relevant_txs),
                        swaps=len(swaps),
                        staking_events=len(staking_events),
                    )

                last_tx_id = batch[-1]["id"]
                batch_number += 1
                summary["batches_processed"] = batch_number

            self.log_success(context, **summary)
            return summary

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _transform_data(
        self, transactions: List[Dict[str, Any]]
    ) -> tuple[List[SwapData], List[StakingEventData]]:
        """Transform raw transactions into structured data.

        Args:
            transactions: List of raw transactions

        Returns:
            Tuple of (swaps, staking_events)
        """
        context = self.log_operation(
            "transform_data",
            transaction_count=len(transactions),
        )

        try:
            # Convert raw transactions to WavesTransaction objects
            waves_transactions = []
            for tx_dict in transactions:
                try:
                    # Create WavesTransaction object with raw_data
                    waves_tx = WavesTransaction(
                        id=tx_dict["id"],
                        height=tx_dict["height"],
                        timestamp=tx_dict["timestamp"],
                        sender=tx_dict["sender"],
                        type=tx_dict["type"],
                        fee=tx_dict.get("fee"),
                        application_status=tx_dict.get("applicationStatus"),
                    )
                    # Store raw data for detailed processing
                    waves_tx.raw_data = tx_dict
                    waves_transactions.append(waves_tx)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse transaction {tx_dict.get('id', 'unknown')}: {e}"
                    )
                    continue

            # Transform swaps
            swaps = self.swap_transformer.transform_transactions(waves_transactions)

            # Transform staking events
            staking_events = self.staking_transformer.transform_transactions(
                waves_transactions
            )

            # Get price data for USD calculations
            price_data = await self._get_price_data()
            asset_decimals = await self._get_asset_decimals(swaps)

            # Calculate USD values for swaps
            if price_data and asset_decimals:
                swaps = self.swap_transformer.calculate_usd_values(
                    swaps, price_data, asset_decimals
                )

            # Calculate USD values for staking events
            puzzle_price = price_data.get(settings.puzzle_token_id, Decimal(0))
            if puzzle_price:
                staking_events = self.staking_transformer.calculate_usd_values(
                    staking_events, puzzle_price
                )

            self.log_success(
                context,
                swaps_count=len(swaps),
                staking_events_count=len(staking_events),
            )

            return swaps, staking_events

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _load_data(
        self,
        swaps: List[SwapData],
        staking_events: List[StakingEventData],
        transactions: List[Dict[str, Any]],
    ) -> None:
        """Load transformed data to database.

        Args:
            swaps: List of swap data
            staking_events: List of staking events
            transactions: List of raw transactions
        """
        context = self.log_operation(
            "load_data",
            swaps_count=len(swaps),
            staking_events_count=len(staking_events),
            transactions_count=len(transactions),
        )

        try:
            # Save raw transactions
            if transactions:
                await self.loader.save_transactions(transactions)

            # Save swaps
            if swaps:
                await self.loader.save_swaps(swaps)

            # Save staking events
            if staking_events:
                await self.loader.save_staking_events(staking_events)

            # Mark transactions as processed
            transaction_ids = [tx["id"] for tx in transactions]
            if transaction_ids:
                await self.loader.mark_transactions_processed(transaction_ids)

            # Calculate and save aggregated data after loading
            if swaps or staking_events:
                await self.loader.calculate_and_save_aggregated_data()

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _update_statistics(
        self,
        swaps: List[SwapData],
        staking_events: List[StakingEventData],
    ) -> None:
        """Update aggregated statistics.

        Args:
            swaps: List of swap data
            staking_events: List of staking events
        """
        context = self.log_operation("update_statistics")

        try:
            # Calculate staking statistics
            if staking_events:
                staking_stats = self.staking_transformer.aggregate_staking_stats(
                    staking_events, datetime.utcnow()
                )

                # Get Puzzle price for USD calculation (this will also save price data)
                price_data = await self._get_price_data()
                puzzle_price = price_data.get(settings.puzzle_token_id)

                self.logger.info(
                    "Staking statistics calculated",
                    total_staked=float(staking_stats["total_staked"]),
                    unique_stakers=staking_stats["unique_stakers"],
                    puzzle_price_usd=float(puzzle_price) if puzzle_price else None,
                )

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _update_final_statistics(self) -> None:
        """Update final aggregated statistics from database data."""
        context = self.log_operation("update_final_statistics")

        try:
            # This method can be used to calculate final statistics
            # from all the data that has been saved to the database
            # For now, we'll just log that final statistics are being updated

            self.logger.info("Final statistics update completed")
            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _get_price_data(self) -> Dict[str, Decimal]:
        """Get current price data for assets and save to database.

        Returns:
            Dictionary mapping asset IDs to USD prices
        """
        if not self.http_client:
            return {}

        try:
            # Get prices from aggregator
            price_response = await self.http_client.get_aggregator_prices()

            # Convert to our format with better error handling
            prices = {}
            price_data_to_save = []
            current_timestamp = datetime.utcnow()

            for asset_id, price_info in price_response.items():
                try:
                    if isinstance(price_info, dict) and "price" in price_info:
                        price_value = price_info["price"]
                    else:
                        price_value = price_info

                    # Handle different price formats
                    if price_value is not None and str(price_value).strip():
                        # Clean the price string and convert to Decimal
                        price_str = str(price_value).strip()
                        if price_str and price_str != "null" and price_str != "None":
                            price_decimal = Decimal(price_str)
                            prices[asset_id] = price_decimal

                            # Prepare price data for saving
                            price_data_to_save.append(
                                {
                                    "asset_id": asset_id,
                                    "timestamp": current_timestamp,
                                    "price_usd": price_decimal,
                                    "source": "aggregator_api",
                                }
                            )

                except (ValueError, TypeError, Exception) as e:
                    self.logger.warning(
                        "Failed to parse price for asset",
                        asset_id=asset_id,
                        price_info=price_info,
                        error=str(e),
                    )
                    continue

            # Save price data to database
            if price_data_to_save:
                await self.loader.save_price_data(price_data_to_save)
                self.logger.info(
                    "Price data saved to database", price_count=len(price_data_to_save)
                )

            return prices

        except Exception as e:
            self.logger.warning("Failed to get price data", error=str(e))
            return {}

    async def _get_asset_decimals(self, swaps: List[SwapData]) -> Dict[str, int]:
        """Get asset decimal information.

        Args:
            swaps: List of swaps to extract asset IDs from

        Returns:
            Dictionary mapping asset IDs to decimal places
        """
        if not self.extractor:
            return {}

        # Collect unique asset IDs
        asset_ids = set()
        for swap in swaps:
            asset_ids.add(swap.asset_in_id)
            asset_ids.add(swap.asset_out_id)

        decimals = {}
        for asset_id in asset_ids:
            try:
                asset_info = await self.extractor.get_asset_info(asset_id)
                decimals[asset_id] = asset_info.get("decimals", 8)
            except Exception as e:
                self.logger.warning(
                    "Failed to get asset decimals",
                    asset_id=asset_id,
                    error=str(e),
                )
                decimals[asset_id] = 8  # Default to 8 decimals

        return decimals

    async def run_incremental_update(
        self, last_processed_id: str = ""
    ) -> Dict[str, Any]:
        """Run incremental pipeline update.

        Args:
            last_processed_id: Last processed transaction ID

        Returns:
            Update summary
        """
        context = self.log_operation(
            "run_incremental_update",
            last_processed_id=last_processed_id,
        )

        try:
            summary = await self.run_pipeline(last_processed_id=last_processed_id)
            summary["update_type"] = "incremental"

            self.log_success(context, **summary)
            return summary

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _save_reference_data(self) -> None:
        """Save asset and pool reference data from mappings to database."""
        context = self.log_operation("save_reference_data")

        try:
            from puzzle_swap_etl.mappings import AddressMapping, AssetMapping

            # Save asset information to STG
            assets_to_save = []
            all_assets = AssetMapping.get_all_assets()
            for asset_id, asset_info in all_assets.items():
                assets_to_save.append(
                    AssetInfo(
                        id=asset_id,
                        name=asset_info.name,
                        symbol=asset_info.symbol,
                        decimals=asset_info.decimals,
                        description=asset_info.description,
                    )
                )

            if assets_to_save:
                await self.loader.save_assets(assets_to_save)
                # Also save to ODS schema
                await self.loader.save_processed_assets_to_ods(assets_to_save)
                self.logger.info(
                    "Asset reference data saved", asset_count=len(assets_to_save)
                )

            # Save pool information to STG
            pools_to_save = []
            all_addresses = AddressMapping.get_all_addresses()
            for address, address_info in all_addresses.items():
                if address_info["type"] == "pool":
                    # Extract asset IDs from pool name or use defaults
                    # This is a simplified approach - in real implementation you'd fetch from API
                    if (
                        "WAVES" in address_info["name"]
                        and "USDN" in address_info["name"]
                    ):
                        asset_a_id = "WAVES"
                        asset_b_id = (
                            "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p"  # USDN
                        )
                    elif (
                        "PUZZLE" in address_info["name"]
                        and "WAVES" in address_info["name"]
                    ):
                        asset_a_id = (
                            "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"  # PUZZLE
                        )
                        asset_b_id = "WAVES"
                    else:
                        # Default for other pools
                        asset_a_id = "WAVES"
                        asset_b_id = "WAVES"

                    pools_to_save.append(
                        PoolInfo(
                            address=address,
                            asset_a_id=asset_a_id,
                            asset_b_id=asset_b_id,
                            name=address_info["name"],
                            fee_rate=Decimal("0.003"),  # Default 0.3% fee
                            active=True,
                        )
                    )

            if pools_to_save:
                await self.loader.save_pools(pools_to_save)
                # Also save to ODS schema
                await self.loader.save_processed_pools_to_ods(pools_to_save)
                self.logger.info(
                    "Pool reference data saved", pool_count=len(pools_to_save)
                )

            self.log_success(context)

        except Exception as e:
            self.log_error(context, e)
            raise
