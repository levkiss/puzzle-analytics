"""HTTP utilities for blockchain API interactions."""

import asyncio
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientTimeout

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.utils.logging import LoggerMixin


class HTTPClient(LoggerMixin):
    """HTTP client for blockchain API interactions."""

    def __init__(self, timeout: int = 30) -> None:
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_json(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Make GET request and return JSON response.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            JSON response data

        Raises:
            aiohttp.ClientError: On HTTP errors
        """
        if not self.session:
            raise RuntimeError("HTTP client not initialized")

        context = self.log_operation("http_get", url=url)

        try:
            async with self.session.get(url, **kwargs) as response:
                response.raise_for_status()
                data = await response.json()
                self.log_success(context, status=response.status)
                return data
        except Exception as e:
            self.log_error(context, e)
            raise

    async def get_waves_transactions(
        self, address: str, limit: int = 1000, after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get transactions for a Waves address.

        Args:
            address: Waves address
            limit: Maximum number of transactions
            after: Transaction ID to start after

        Returns:
            List of transaction data
        """
        for node_url in settings.waves_node_urls:
            try:
                url = f"{node_url}transactions/address/{address}/limit/{limit}"
                if after:
                    url += f"?after={after}"

                data = await self.get_json(url)
                return data[0] if isinstance(data, list) and data else []

            except Exception as e:
                self.logger.warning(
                    "Failed to fetch from node, trying next",
                    node_url=node_url,
                    error=str(e),
                )
                continue

        raise RuntimeError("All Waves nodes failed")

    async def get_address_data(
        self, address: str, key_pattern: str = ""
    ) -> List[Dict[str, Any]]:
        """Get address data from Waves node.

        Args:
            address: Waves address
            key_pattern: Key pattern to filter

        Returns:
            List of address data entries
        """
        for node_url in settings.waves_node_urls:
            try:
                url = f"{node_url}addresses/data/{address}"
                if key_pattern:
                    url += f"?matches={key_pattern}"

                return await self.get_json(url)

            except Exception as e:
                self.logger.warning(
                    "Failed to fetch address data from node, trying next",
                    node_url=node_url,
                    error=str(e),
                )
                continue

        raise RuntimeError("All Waves nodes failed")

    async def get_asset_info(self, asset_id: str) -> Dict[str, Any]:
        """Get asset information.

        Args:
            asset_id: Asset ID

        Returns:
            Asset information
        """
        if asset_id == "WAVES":
            return {
                "assetId": "WAVES",
                "name": "Waves",
                "decimals": 8,
                "description": "Waves native token",
            }

        for node_url in settings.waves_node_urls:
            try:
                url = f"{node_url}assets/details/{asset_id}"
                return await self.get_json(url)

            except Exception as e:
                self.logger.warning(
                    "Failed to fetch asset info from node, trying next",
                    node_url=node_url,
                    error=str(e),
                )
                continue

        raise RuntimeError("All Waves nodes failed")

    async def get_aggregator_prices(self) -> Dict[str, Any]:
        """Get prices from Puzzle aggregator.

        Returns:
            Price data from aggregator
        """
        url = f"{settings.aggregator_url}aggregator/getPrices"
        return await self.get_json(url)

    async def get_pools_data(self) -> Dict[str, Any]:
        """Get pools data from aggregator.

        Returns:
            Pools data from aggregator
        """
        url = f"{settings.aggregator_url}getPoolsData"
        return await self.get_json(url)


async def retry_async(
    func: Any, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0
) -> Any:
    """Retry async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier

    Returns:
        Function result

    Raises:
        Exception: Last exception if all retries failed
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(delay * (backoff**attempt))
            else:
                break

    raise last_exception
