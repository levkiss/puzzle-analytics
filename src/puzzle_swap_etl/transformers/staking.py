"""Staking event transformer for Puzzle Swap staking data."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from puzzle_swap_etl.mappings import AddressMapping, AssetMapping, FunctionMapping
from puzzle_swap_etl.models import StakingEventData, WavesTransaction
from puzzle_swap_etl.utils import LoggerMixin


class StakingTransformer(LoggerMixin):
    """Transforms raw blockchain transactions into staking events."""

    def __init__(self) -> None:
        """Initialize staking transformer."""
        self.puzzle_decimals = 8

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

    def _is_staking_transaction(self, transaction: WavesTransaction) -> bool:
        """Check if transaction is a staking event."""
        if transaction.type != 16:  # InvokeScript
            return False

        # Check if transaction involves staking addresses
        if transaction.sender in AddressMapping.get_staking_addresses():
            return True

        # Check if dApp is a staking contract
        invoke_data = transaction.raw_data
        if isinstance(invoke_data, dict):
            d_app = invoke_data.get("dApp")
            if d_app and d_app in AddressMapping.get_staking_addresses():
                return True

            # Check function name
            function_name = FunctionMapping.extract_function_from_invoke(invoke_data)
            if function_name and FunctionMapping.is_staking_function(function_name):
                return True

        return False

    def _extract_staking_data(
        self, transaction: WavesTransaction
    ) -> Optional[StakingEventData]:
        """Extract staking data from transaction."""
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
            if not function_name or not FunctionMapping.is_staking_function(
                function_name
            ):
                return None

            # Determine event type based on function
            event_type = self._determine_event_type(function_name)
            if not event_type:
                return None

            # Extract staking details
            staking_details = self._parse_staking_details(
                invoke_data, transaction, event_type
            )
            if not staking_details:
                return None

            # Create staking event data
            event_id = f"{transaction.id}_{event_type}_{staking_details['amount']}"

            return StakingEventData(
                id=event_id,
                transaction_id=transaction.id,
                height=transaction.height,
                timestamp=transaction.timestamp_dt,
                staker_address=transaction.sender,
                event_type=event_type,
                amount=staking_details["amount"],
                amount_usd=staking_details.get("amount_usd"),
            )

        except Exception as e:
            self.logger.error(
                f"Error extracting staking data from {transaction.id}: {e}"
            )
            return None

    def _determine_event_type(self, function_name: str) -> Optional[str]:
        """Determine staking event type from function name."""
        function_mapping = {
            "stake": "stake",
            "unstake": "unstake",
            "withdraw": "unstake",
            "claim": "claim",
            "claimRewards": "claim",
            "compound": "compound",
            "emergencyWithdraw": "emergency_withdraw",
        }
        return function_mapping.get(function_name)

    def _parse_staking_details(
        self, invoke_data: Dict, transaction: WavesTransaction, event_type: str
    ) -> Optional[Dict]:
        """Parse staking details from invoke transaction."""
        try:
            amount = Decimal(0)

            if event_type in ["stake"]:
                # For staking, amount comes from payments
                payments = invoke_data.get("payment", [])
                if payments:
                    payment = payments[0]
                    asset_id = payment.get("assetId") or AssetMapping.WAVES_ID
                    if asset_id == AssetMapping.PUZZLE_TOKEN_ID:
                        amount_raw = payment.get("amount", 0)
                        amount = AssetMapping.normalize_amount(asset_id, amount_raw)

            elif event_type in ["unstake", "claim", "compound"]:
                # For unstaking/claiming, amount comes from transfers
                state_changes = invoke_data.get("stateChanges", {})
                transfers = state_changes.get("transfers", [])

                for transfer in transfers:
                    if transfer.get("address") == transaction.sender:
                        asset_id = transfer.get("asset") or AssetMapping.WAVES_ID
                        if asset_id == AssetMapping.PUZZLE_TOKEN_ID:
                            amount_raw = transfer.get("amount", 0)
                            amount = AssetMapping.normalize_amount(asset_id, amount_raw)
                            break

            # Calculate USD value
            amount_usd = self._calculate_usd_value(AssetMapping.PUZZLE_TOKEN_ID, amount)

            return {
                "amount": amount,
                "amount_usd": amount_usd,
            }

        except Exception as e:
            self.logger.error(f"Error parsing staking details: {e}")
            return None

    def _extract_staking_from_data_entries(
        self, transaction: Dict[str, Any]
    ) -> List[StakingEventData]:
        """Extract staking events from data entries.

        Args:
            transaction: Raw transaction

        Returns:
            List of staking events extracted from data entries
        """
        events = []

        try:
            data_entries = transaction.get("stateChanges", {}).get("data", [])
            tx_id = transaction["id"]
            height = transaction["height"]
            timestamp = datetime.fromtimestamp(transaction["timestamp"] / 1000)

            for entry in data_entries:
                key = entry.get("key", "")
                value = entry.get("value", 0)

                # Look for staking-related data entries
                if "_staked" in key and value > 0:
                    # Extract staker address from key
                    staker_address = key.split("_")[0]
                    amount = Decimal(value) / (10**self.puzzle_decimals)

                    # Create event ID
                    event_id = f"{tx_id}_stake_update_{staker_address}_{value}"

                    event = StakingEventData(
                        id=event_id,
                        transaction_id=tx_id,
                        height=height,
                        timestamp=timestamp,
                        staker_address=staker_address,
                        event_type="stake_update",
                        amount=amount,
                    )
                    events.append(event)

        except (KeyError, ValueError, TypeError) as e:
            self.logger.warning(
                "Failed to extract staking from data entries",
                transaction_id=transaction.get("id"),
                error=str(e),
            )

        return events

    def transform_transactions(
        self, transactions: List[WavesTransaction]
    ) -> List[StakingEventData]:
        """Transform list of transactions into staking events.

        Args:
            transactions: List of WavesTransaction objects

        Returns:
            List of staking events
        """
        context = self.log_operation(
            "transform_staking_events",
            transaction_count=len(transactions),
        )

        events = []

        try:
            for transaction in transactions:
                # Try to extract from invoke functions
                event = self._extract_staking_data(transaction)
                if event:
                    events.append(event)

                # Also try to extract from data entries using raw_data
                if transaction.raw_data:
                    data_events = self._extract_staking_from_data_entries(
                        transaction.raw_data
                    )
                    events.extend(data_events)

            self.log_success(
                context,
                events_extracted=len(events),
                success_rate=(
                    f"{len(events)/len(transactions)*100:.1f}%"
                    if transactions
                    else "0%"
                ),
            )

            return events

        except Exception as e:
            self.log_error(context, e)
            raise

    def calculate_usd_values(
        self,
        events: List[StakingEventData],
        puzzle_price: Decimal,
    ) -> List[StakingEventData]:
        """Calculate USD values for staking events.

        Args:
            events: List of staking events
            puzzle_price: Puzzle token price in USD

        Returns:
            Updated staking events with USD values
        """
        context = self.log_operation(
            "calculate_staking_usd_values",
            event_count=len(events),
        )

        try:
            updated_events = []

            for event in events:
                # Calculate USD value
                if puzzle_price and event.amount:
                    event.amount_usd = event.amount * puzzle_price

                updated_events.append(event)

            self.log_success(
                context,
                events_with_usd=len([e for e in updated_events if e.amount_usd]),
            )

            return updated_events

        except Exception as e:
            self.log_error(context, e)
            raise

    def aggregate_staking_stats(
        self,
        events: List[StakingEventData],
        timestamp: datetime,
    ) -> Dict[str, Any]:
        """Aggregate staking statistics from events.

        Args:
            events: List of staking events
            timestamp: Timestamp for the statistics

        Returns:
            Aggregated staking statistics
        """
        context = self.log_operation(
            "aggregate_staking_stats",
            event_count=len(events),
        )

        try:
            # Calculate total staked amount
            staker_balances = {}

            for event in events:
                staker = event.staker_address
                if staker not in staker_balances:
                    staker_balances[staker] = Decimal(0)

                if event.event_type == "stake":
                    staker_balances[staker] += event.amount
                elif event.event_type == "unstake":
                    staker_balances[staker] -= event.amount
                elif event.event_type == "stake_update":
                    # This represents the current staked amount
                    staker_balances[staker] = event.amount

            # Filter out zero or negative balances
            active_stakers = {k: v for k, v in staker_balances.items() if v > 0}

            total_staked = sum(active_stakers.values())
            unique_stakers = len(active_stakers)

            stats = {
                "timestamp": timestamp,
                "total_staked": total_staked,
                "unique_stakers": unique_stakers,
                "staker_balances": active_stakers,
            }

            self.log_success(
                context,
                total_staked=float(total_staked),
                unique_stakers=unique_stakers,
            )

            return stats

        except Exception as e:
            self.log_error(context, e)
            raise
