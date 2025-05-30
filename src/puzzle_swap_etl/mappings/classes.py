"""Mapping wrapper classes for consistent ETL pipeline interface."""

from typing import Dict, List, Optional

from .addresses import (
    ALL_IMPORTANT_ADDRESSES,
    CORE_PROTOCOL_ADDRESSES,
    LENDING_ADDRESSES,
    STAKING_ADDRESSES,
    get_address_name,
    get_address_type,
    is_fee_collector,
    is_lending_address,
    is_protocol_address,
    is_staking_address,
)
from .functions import LENDING_FUNCTIONS, STAKING_FUNCTIONS, SWAP_FUNCTIONS


class AddressMapping:
    """Centralized address mapping for Puzzle ecosystem."""

    @classmethod
    def get_all_addresses(cls) -> Dict[str, Dict[str, str]]:
        """Get all known addresses with their metadata."""
        addresses = {}
        for address in ALL_IMPORTANT_ADDRESSES:
            addresses[address] = {
                "address": address,
                "name": get_address_name(address),
                "type": get_address_type(address),
            }
        return addresses

    @classmethod
    def get_address_info(cls, address: str) -> Optional[Dict[str, str]]:
        """Get information about a specific address."""
        if address in ALL_IMPORTANT_ADDRESSES:
            return {
                "address": address,
                "name": get_address_name(address),
                "type": get_address_type(address),
            }
        return None

    @classmethod
    def get_address_name(cls, address: str) -> str:
        """Get human-readable name for an address."""
        return get_address_name(address)

    @classmethod
    def get_address_type(cls, address: str) -> str:
        """Get the type/category of an address."""
        return get_address_type(address)

    @classmethod
    def is_protocol_address(cls, address: str) -> bool:
        """Check if address belongs to a protocol."""
        return is_protocol_address(address)

    @classmethod
    def is_staking_address(cls, address: str) -> bool:
        """Check if address is a staking contract."""
        return is_staking_address(address)

    @classmethod
    def is_lending_address(cls, address: str) -> bool:
        """Check if address is a lending contract."""
        return is_lending_address(address)

    @classmethod
    def is_fee_collector(cls, address: str) -> bool:
        """Check if address is a protocol fee collector."""
        return is_fee_collector(address)

    @classmethod
    def get_staking_addresses(cls) -> List[str]:
        """Get all staking addresses."""
        return STAKING_ADDRESSES.copy()

    @classmethod
    def get_lending_addresses(cls) -> List[str]:
        """Get all lending addresses."""
        return LENDING_ADDRESSES.copy()

    @classmethod
    def get_core_addresses(cls) -> List[str]:
        """Get core protocol addresses."""
        return CORE_PROTOCOL_ADDRESSES.copy()

    @classmethod
    def get_all_important_addresses(cls) -> List[str]:
        """Get all important addresses for monitoring."""
        return ALL_IMPORTANT_ADDRESSES.copy()

    @classmethod
    def get_pool_addresses(cls) -> List[str]:
        """Get all pool addresses."""
        pool_addresses = []
        for address, info in cls.get_all_addresses().items():
            if info["type"] == "pool":
                pool_addresses.append(address)
        return pool_addresses


class FunctionMapping:
    """Centralized function mapping for smart contract functions."""

    @classmethod
    def get_swap_functions(cls) -> List[str]:
        """Get all swap functions."""
        return SWAP_FUNCTIONS.copy()

    @classmethod
    def get_staking_functions(cls) -> List[str]:
        """Get all staking functions."""
        return STAKING_FUNCTIONS.copy()

    @classmethod
    def get_lending_functions(cls) -> List[str]:
        """Get all lending functions."""
        return LENDING_FUNCTIONS.copy()

    @classmethod
    def is_swap_function(cls, function_name: str) -> bool:
        """Check if function is swap-related."""
        return function_name in SWAP_FUNCTIONS

    @classmethod
    def is_staking_function(cls, function_name: str) -> bool:
        """Check if function is staking-related."""
        return function_name in STAKING_FUNCTIONS

    @classmethod
    def is_lending_function(cls, function_name: str) -> bool:
        """Check if function is lending-related."""
        return function_name in LENDING_FUNCTIONS


class AssetMapping:
    """Centralized asset mapping for Waves blockchain assets."""

    @classmethod
    def get_all_assets(cls) -> Dict[str, Dict[str, str]]:
        """Get all known assets with their metadata."""
        from .assets import ASSET_DECIMALS, ASSET_NAMES, ASSET_SYMBOLS

        assets = {}
        for asset_id in ASSET_NAMES.keys():
            assets[asset_id] = {
                "id": asset_id,
                "name": ASSET_NAMES.get(asset_id, "Unknown"),
                "symbol": ASSET_SYMBOLS.get(asset_id, "UNK"),
                "decimals": ASSET_DECIMALS.get(asset_id, 8),
                "description": f"Asset {asset_id[:8]}...",
            }
        return assets

    @classmethod
    def get_asset_info(cls, asset_id: str) -> Optional[Dict[str, str]]:
        """Get information about a specific asset."""
        from .assets import ASSET_DECIMALS, ASSET_NAMES, ASSET_SYMBOLS

        if asset_id in ASSET_NAMES:
            return {
                "id": asset_id,
                "name": ASSET_NAMES.get(asset_id, "Unknown"),
                "symbol": ASSET_SYMBOLS.get(asset_id, "UNK"),
                "decimals": ASSET_DECIMALS.get(asset_id, 8),
                "description": f"Asset {asset_id[:8]}...",
            }
        return None
