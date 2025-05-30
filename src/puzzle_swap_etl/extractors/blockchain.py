"""Blockchain data extractor for Waves blockchain."""

import json
from typing import Any, Dict, List, Optional, Tuple

import aiofiles

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.mappings import AddressMapping, FunctionMapping
from puzzle_swap_etl.utils import HTTPClient, LoggerMixin


class BlockchainExtractor(LoggerMixin):
    """Extracts transaction data from the Waves blockchain."""

    def __init__(self) -> None:
        """Initialize blockchain extractor."""
        self.http_client: Optional[HTTPClient] = None

    async def __aenter__(self) -> "BlockchainExtractor":
        """Async context manager entry."""
        self.http_client = HTTPClient()
        await self.http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.http_client:
            await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    def _extract_invokes(
        self,
        invokes: List[Dict[str, Any]],
        target_address: str,
        sender: str,
        height: int,
        timestamp: int,
        tx_id: str,
        collector: List[Dict[str, Any]],
        vip_functions: Optional[List[str]] = None,
    ) -> None:
        """Extract invoke transactions recursively.

        Args:
            invokes: List of invoke transactions
            target_address: Target contract address
            sender: Transaction sender
            height: Block height
            timestamp: Transaction timestamp
            tx_id: Transaction ID
            collector: List to collect matching transactions
            vip_functions: Important function names to always include
        """
        vip_functions = vip_functions or []

        for invoke in invokes:
            invoke["sender"] = sender
            invoke["height"] = height
            invoke["timestamp"] = timestamp
            invoke["type"] = 16
            invoke["id"] = tx_id

            try:
                if (
                    invoke["dApp"] == target_address
                    or invoke["call"]["function"] in vip_functions
                ):
                    collector.append(invoke)
            except KeyError as e:
                self.logger.error(
                    "Invalid invoke structure", invoke=invoke, error=str(e)
                )
                continue

            # Recursively process nested invokes
            nested_invokes = invoke.get("stateChanges", {}).get("invokes", [])
            if nested_invokes:
                self._extract_invokes(
                    nested_invokes,
                    target_address,
                    invoke["dApp"],
                    height,
                    timestamp,
                    tx_id,
                    collector,
                    vip_functions,
                )

    def _find_relevant_transactions(
        self,
        transaction: Dict[str, Any],
        target_address: str,
        vip_functions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Find transactions relevant to the target address.

        Args:
            transaction: Raw transaction data
            target_address: Target contract address
            vip_functions: Important function names to always include

        Returns:
            List of relevant transactions
        """
        relevant_txs = []
        vip_functions = vip_functions or []

        # Skip failed transactions
        if transaction.get("applicationStatus") != "succeeded":
            return []

        # Handle type 18 (MetaMask) transactions
        if transaction["type"] == 18:
            payload = transaction["payload"]
            payload.update(
                {
                    "id": transaction["id"],
                    "timestamp": transaction["timestamp"],
                    "height": transaction["height"],
                    "sender": transaction["sender"],
                    "applicationStatus": transaction.get("applicationStatus", ""),
                    "type": 16 if payload["type"] == "invocation" else 4,
                }
            )
            transaction = payload

        # Handle invoke transactions (type 16)
        if transaction["type"] == 16:
            if (
                transaction["dApp"] == target_address
                or transaction["call"]["function"] in vip_functions
            ):
                relevant_txs.append(transaction)

            # Extract nested invokes
            nested_invokes = transaction.get("stateChanges", {}).get("invokes", [])
            if nested_invokes:
                self._extract_invokes(
                    nested_invokes,
                    target_address,
                    transaction["dApp"],
                    transaction["height"],
                    transaction["timestamp"],
                    transaction["id"],
                    relevant_txs,
                    vip_functions,
                )

        return relevant_txs

    async def fetch_transactions_batch(
        self,
        address: str,
        limit: int = 1000,
        after: Optional[str] = None,
        last_processed_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """Fetch a batch of transactions for an address.

        Args:
            address: Waves address
            limit: Maximum transactions per batch
            after: Transaction ID to start after
            last_processed_id: Last processed transaction ID

        Returns:
            Tuple of (transactions, has_more)
        """
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")

        context = self.log_operation(
            "fetch_transactions_batch",
            address=address,
            limit=limit,
            after=after,
        )

        try:
            transactions = await self.http_client.get_waves_transactions(
                address=address,
                limit=limit,
                after=after,
            )

            # Filter out already processed transactions
            if last_processed_id:
                filtered_txs = []
                for tx in transactions:
                    if tx["id"] == last_processed_id:
                        break
                    filtered_txs.append(tx)
                transactions = filtered_txs

            has_more = len(transactions) == limit

            self.log_success(
                context,
                transactions_count=len(transactions),
                has_more=has_more,
            )

            return transactions, has_more

        except Exception as e:
            self.log_error(context, e)
            raise

    async def fetch_all_transactions(
        self,
        address: str,
        function_name: str = "",
        last_processed_id: str = "",
        vip_functions: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch all transactions for an address.

        Args:
            address: Waves address
            function_name: Filter by function name
            last_processed_id: Last processed transaction ID
            vip_functions: Important function names to always include

        Returns:
            Tuple of (transactions, file_count) where file_count > 0
            indicates transactions were saved to files due to memory limits
        """
        context = self.log_operation(
            "fetch_all_transactions",
            address=address,
            function_name=function_name,
        )

        try:
            all_transactions = []
            last_tx_id = ""
            has_more = True
            file_count = 0
            total_count = 0

            while has_more:
                batch, has_more = await self.fetch_transactions_batch(
                    address=address,
                    after=last_tx_id,
                    last_processed_id=last_processed_id,
                )

                if not batch:
                    break

                # Process transactions to find relevant ones
                relevant_txs = []
                for tx in batch:
                    found_txs = self._find_relevant_transactions(
                        tx, address, vip_functions
                    )
                    relevant_txs.extend(found_txs)

                all_transactions.extend(relevant_txs)
                total_count += len(relevant_txs)
                last_tx_id = batch[-1]["id"]

                # Check memory limits
                if len(all_transactions) > settings.max_transactions_in_memory:
                    await self._save_transactions_to_file(
                        all_transactions, address, file_count
                    )
                    file_count += 1
                    all_transactions.clear()

                self.logger.info(
                    "Processed batch",
                    batch_size=len(batch),
                    relevant_count=len(relevant_txs),
                    total_count=total_count,
                )

            # Save remaining transactions if using files
            if file_count > 0 and all_transactions:
                await self._save_transactions_to_file(
                    all_transactions, address, file_count
                )
                file_count += 1
                all_transactions.clear()

            # Reverse for chronological order
            if not file_count:
                all_transactions.reverse()

            self.log_success(
                context,
                total_transactions=total_count,
                file_count=file_count,
            )

            return all_transactions, file_count

        except Exception as e:
            self.log_error(context, e)
            raise

    async def _save_transactions_to_file(
        self,
        transactions: List[Dict[str, Any]],
        address: str,
        file_index: int,
    ) -> None:
        """Save transactions to a temporary file.

        Args:
            transactions: List of transactions
            address: Address identifier
            file_index: File index number
        """
        filename = f"tmp/{address}_{file_index}"

        async with aiofiles.open(filename, "w") as f:
            await f.write(json.dumps(transactions))

        self.logger.info(
            "Saved transactions to file",
            filename=filename,
            count=len(transactions),
        )

    async def load_transactions_from_files(
        self,
        address: str,
        file_count: int,
    ) -> List[Dict[str, Any]]:
        """Load transactions from temporary files.

        Args:
            address: Address identifier
            file_count: Number of files to load

        Returns:
            List of all transactions in chronological order
        """
        all_transactions = []

        # Load files in reverse order (oldest first)
        for i in range(file_count - 1, -1, -1):
            filename = f"tmp/{address}_{i}"

            try:
                async with aiofiles.open(filename, "r") as f:
                    content = await f.read()
                    transactions = json.loads(content)
                    transactions.reverse()  # Reverse for chronological order
                    all_transactions.extend(transactions)

                # Clean up file
                import os

                if os.path.exists(filename):
                    os.remove(filename)

            except Exception as e:
                self.logger.error(
                    "Failed to load transactions file",
                    filename=filename,
                    error=str(e),
                )

        return all_transactions

    async def get_asset_info(self, asset_id: str) -> Dict[str, Any]:
        """Get asset information from blockchain.

        Args:
            asset_id: Asset ID

        Returns:
            Asset information
        """
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")

        return await self.http_client.get_asset_info(asset_id)

    async def get_address_data(
        self, address: str, key_pattern: str = ""
    ) -> List[Dict[str, Any]]:
        """Get address data from blockchain.

        Args:
            address: Waves address
            key_pattern: Key pattern to filter

        Returns:
            List of address data entries
        """
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")

        return await self.http_client.get_address_data(address, key_pattern)
