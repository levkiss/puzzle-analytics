"""Swap transaction transformer for Puzzle Swap trading data."""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from puzzle_swap_etl.mappings import AddressMapping, AssetMapping, FunctionMapping
from puzzle_swap_etl.models import SwapData, WavesTransaction
from puzzle_swap_etl.utils import LoggerMixin


class SwapTransformer(LoggerMixin):
    """Transforms raw blockchain transactions into swap data."""

    def __init__(self) -> None:
        """Initialize swap transformer."""
        self.puzzle_decimals = 8

    def _normalize_asset_id(self, asset_id: Optional[str]) -> str:
        """Normalize asset ID (convert None to WAVES).

        Args:
            asset_id: Asset ID or None

        Returns:
            Normalized asset ID
        """
        return asset_id or "WAVES"

    def _calculate_usd_value(self, asset_id: str, amount: Decimal) -> Optional[Decimal]:
        """Calculate USD value for an asset amount.

        Args:
            asset_id: Asset ID
            amount: Amount in normalized decimal format

        Returns:
            USD value or None if price not available
        """
        # For now, return None as we don't have price data integration yet
        # This will be implemented when price data source is added
        return None

    def _is_swap_transaction(self, transaction: WavesTransaction) -> bool:
        """Check if transaction is a swap."""
        if transaction.type != 16:  # InvokeScript
            return False

        # Check if transaction involves known pool addresses
        if transaction.sender in AddressMapping.get_pool_addresses():
            return True

        # Check if dApp is a known pool
        invoke_data = transaction.raw_data
        if isinstance(invoke_data, dict):
            d_app = invoke_data.get("dApp")
            if d_app and d_app in AddressMapping.get_pool_addresses():
                return True

            # Check function name
            function_name = FunctionMapping.extract_function_from_invoke(invoke_data)
            if function_name and FunctionMapping.is_swap_function(function_name):
                return True

        return False

    def _extract_swap_data(self, transaction: WavesTransaction) -> Optional[SwapData]:
        """Extract swap data from transaction."""
        try:
            invoke_data = transaction.raw_data
            if not isinstance(invoke_data, dict):
                return None

            # Extract basic information
            d_app = invoke_data.get("dApp")
            if not d_app:
                return None

            # Get function name
            function_name = FunctionMapping.extract_function_from_invoke(invoke_data)
            if not function_name or not FunctionMapping.is_swap_function(function_name):
                return None

            # Extract swap details from state changes or payments
            swap_details = self._parse_swap_details(invoke_data, transaction)
            if not swap_details:
                return None

            # Create swap data
            swap_id = f"{transaction.id}_{swap_details['asset_in_id']}_{swap_details['asset_out_id']}"

            return SwapData(
                id=swap_id,
                transaction_id=transaction.id,
                height=transaction.height,
                timestamp=transaction.timestamp,
                pool_address=d_app,
                trader_address=transaction.sender,
                asset_in_id=swap_details["asset_in_id"],
                asset_out_id=swap_details["asset_out_id"],
                amount_in=swap_details["amount_in"],
                amount_out=swap_details["amount_out"],
                amount_in_usd=swap_details.get("amount_in_usd"),
                amount_out_usd=swap_details.get("amount_out_usd"),
                volume_usd=swap_details.get("volume_usd"),
                pool_fee=swap_details.get("pool_fee"),
                protocol_fee=swap_details.get("protocol_fee"),
            )

        except Exception as e:
            self.logger.error(f"Error extracting swap data from {transaction.id}: {e}")
            return None

    def _parse_swap_details(
        self, invoke_data: Dict, transaction: WavesTransaction
    ) -> Optional[Dict]:
        """Parse swap details from invoke transaction."""
        try:
            # Extract from payments (input)
            payments = invoke_data.get("payment", [])
            if not payments:
                return None

            # Get input payment
            input_payment = payments[0] if payments else {}
            asset_in_id = input_payment.get("assetId") or AssetMapping.WAVES_ID
            amount_in_raw = input_payment.get("amount", 0)

            # Normalize input amount
            amount_in = AssetMapping.normalize_amount(asset_in_id, amount_in_raw)

            # Extract output from state changes
            state_changes = invoke_data.get("stateChanges", {})
            transfers = state_changes.get("transfers", [])

            # Find output transfer to sender
            output_transfer = None
            for transfer in transfers:
                if transfer.get("address") == transaction.sender:
                    output_transfer = transfer
                    break

            if not output_transfer:
                return None

            asset_out_id = output_transfer.get("asset") or AssetMapping.WAVES_ID
            amount_out_raw = output_transfer.get("amount", 0)

            # Normalize output amount
            amount_out = AssetMapping.normalize_amount(asset_out_id, amount_out_raw)

            # Calculate USD values if possible
            amount_in_usd = self._calculate_usd_value(asset_in_id, amount_in)
            amount_out_usd = self._calculate_usd_value(asset_out_id, amount_out)
            volume_usd = (
                max(amount_in_usd or 0, amount_out_usd or 0)
                if (amount_in_usd or amount_out_usd)
                else None
            )

            # Extract fees
            pool_fee = self._extract_pool_fee(state_changes)
            protocol_fee = self._extract_protocol_fee(state_changes)

            return {
                "asset_in_id": asset_in_id,
                "asset_out_id": asset_out_id,
                "amount_in": amount_in,
                "amount_out": amount_out,
                "amount_in_usd": amount_in_usd,
                "amount_out_usd": amount_out_usd,
                "volume_usd": volume_usd,
                "pool_fee": pool_fee,
                "protocol_fee": protocol_fee,
            }

        except Exception as e:
            self.logger.error(f"Error parsing swap details: {e}")
            return None

    def _extract_pool_fee(self, transaction: Dict[str, Any]) -> Optional[Decimal]:
        """Extract pool fee from transaction.

        Args:
            transaction: Raw transaction

        Returns:
            Pool fee amount or None
        """
        try:
            # Look for fee-related data entries
            data_entries = transaction.get("stateChanges", {}).get("data", [])
            for entry in data_entries:
                if "fee" in entry.get("key", "").lower():
                    return Decimal(entry["value"])
            return None
        except (KeyError, ValueError, TypeError):
            return None

    def _extract_protocol_fee(self, transaction: Dict[str, Any]) -> Optional[Decimal]:
        """Extract protocol fee from transaction.

        Args:
            transaction: Raw transaction

        Returns:
            Protocol fee amount or None
        """
        try:
            # Look for protocol fee transfers
            transfers = transaction.get("stateChanges", {}).get("transfers", [])
            protocol_addresses = [
                "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS",  # Main protocol fee collector
                "3P4kBiU4wr2yV1S5gMfu3MdkVvy7kxXHsKe",  # Alternative collector
            ]

            for transfer in transfers:
                if transfer["address"] in protocol_addresses:
                    return Decimal(transfer["amount"])
            return None
        except (KeyError, ValueError, TypeError):
            return None

    def transform_transactions(
        self, transactions: List[WavesTransaction]
    ) -> List[SwapData]:
        """Transform list of transactions into swap data.

        Args:
            transactions: List of raw transactions

        Returns:
            List of swap data
        """
        context = self.log_operation(
            "transform_swaps",
            transaction_count=len(transactions),
        )

        swaps = []

        try:
            for transaction in transactions:
                if self._is_swap_transaction(transaction):
                    swap_data = self._extract_swap_data(transaction)
                    if swap_data:
                        swaps.append(swap_data)

            self.log_success(
                context,
                swaps_extracted=len(swaps),
                success_rate=(
                    f"{len(swaps)/len(transactions)*100:.1f}%" if transactions else "0%"
                ),
            )

            return swaps

        except Exception as e:
            self.log_error(context, e)
            raise

    def calculate_usd_values(
        self,
        swaps: List[SwapData],
        price_data: Dict[str, Decimal],
        asset_decimals: Dict[str, int],
    ) -> List[SwapData]:
        """Calculate USD values for swaps.

        Args:
            swaps: List of swap data
            price_data: Asset prices in USD
            asset_decimals: Asset decimal places

        Returns:
            Updated swap data with USD values
        """
        context = self.log_operation(
            "calculate_usd_values",
            swap_count=len(swaps),
        )

        try:
            updated_swaps = []

            for swap in swaps:
                # Normalize amounts based on decimals
                in_decimals = asset_decimals.get(swap.asset_in_id, 8)
                out_decimals = asset_decimals.get(swap.asset_out_id, 8)

                normalized_amount_in = swap.amount_in / (10**in_decimals)
                normalized_amount_out = swap.amount_out / (10**out_decimals)

                # Calculate USD values
                in_price = price_data.get(swap.asset_in_id, Decimal(0))
                out_price = price_data.get(swap.asset_out_id, Decimal(0))

                amount_in_usd = normalized_amount_in * in_price if in_price else None
                amount_out_usd = (
                    normalized_amount_out * out_price if out_price else None
                )

                # Volume is the average of input and output USD values
                if amount_in_usd and amount_out_usd:
                    volume_usd = (amount_in_usd + amount_out_usd) / 2
                elif amount_in_usd:
                    volume_usd = amount_in_usd
                elif amount_out_usd:
                    volume_usd = amount_out_usd
                else:
                    volume_usd = None

                # Update swap data
                swap.amount_in_usd = amount_in_usd
                swap.amount_out_usd = amount_out_usd
                swap.volume_usd = volume_usd

                updated_swaps.append(swap)

            self.log_success(
                context,
                swaps_with_usd=len([s for s in updated_swaps if s.volume_usd]),
            )

            return updated_swaps

        except Exception as e:
            self.log_error(context, e)
            raise
