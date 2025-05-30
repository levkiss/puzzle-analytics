"""Tests for mapping modules."""

from decimal import Decimal

import pytest

from puzzle_swap_etl.mappings import AddressMapping, AssetMapping, FunctionMapping


class TestAddressMappings:
    """Test address mapping functions."""

    def test_get_address_info(self):
        """Test address info retrieval."""
        # Test staking address
        info = AddressMapping.get_address_info("3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS")
        assert info is not None
        assert info.type == "staking"
        assert "staking" in info.name.lower()

        # Test unknown address
        assert AddressMapping.get_address_info("unknown_address") is None

    def test_get_address_type(self):
        """Test address type detection."""
        # Test staking address
        assert (
            AddressMapping.get_address_type("3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS")
            == "staking"
        )

        # Test unknown address
        assert AddressMapping.get_address_type("unknown_address") is None

    def test_is_puzzle_related(self):
        """Test puzzle-related address detection."""
        assert (
            AddressMapping.is_puzzle_related("3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS")
            is True
        )
        assert AddressMapping.is_puzzle_related("unknown_address") is False

    def test_get_pool_addresses(self):
        """Test pool address retrieval."""
        pools = AddressMapping.get_pool_addresses()
        assert len(pools) > 0
        assert "3PFQjjDMiZKQZdu5JqTHD7HwgSXyp9Rw9By" in pools  # WAVES/USDN pool

    def test_get_addresses_by_type(self):
        """Test filtering addresses by type."""
        pools = AddressMapping.get_addresses_by_type("pool")
        staking = AddressMapping.get_addresses_by_type("staking")

        assert len(pools) > 0
        assert len(staking) > 0

        # Check that all returned addresses have correct type
        for addr, info in pools.items():
            assert info.type == "pool"

    def test_get_addresses_by_tag(self):
        """Test filtering addresses by tag."""
        major_addresses = AddressMapping.get_addresses_by_tag("major")
        puzzle_addresses = AddressMapping.get_addresses_by_tag("puzzle")

        assert len(major_addresses) > 0
        assert len(puzzle_addresses) > 0


class TestAssetMappings:
    """Test asset mapping functions."""

    def test_get_asset_info(self):
        """Test asset info retrieval."""
        # Test WAVES
        waves_info = AssetMapping.get_asset_info("WAVES")
        assert waves_info is not None
        assert waves_info.symbol == "WAVES"
        assert waves_info.decimals == 8

        # Test Puzzle token
        puzzle_info = AssetMapping.get_asset_info(
            "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"
        )
        assert puzzle_info is not None
        assert puzzle_info.symbol == "PUZZLE"

        # Test unknown asset
        assert AssetMapping.get_asset_info("unknown_asset") is None

    def test_get_asset_symbol(self):
        """Test asset symbol lookup."""
        assert AssetMapping.get_asset_symbol("WAVES") == "WAVES"
        assert (
            AssetMapping.get_asset_symbol(
                "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"
            )
            == "PUZZLE"
        )
        # Unknown asset should return truncated ID (first 8 chars + "...")
        assert AssetMapping.get_asset_symbol("unknown_asset") == "unknown_..."

    def test_get_asset_decimals(self):
        """Test asset decimals lookup."""
        assert AssetMapping.get_asset_decimals("WAVES") == 8
        assert (
            AssetMapping.get_asset_decimals(
                "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"
            )
            == 8
        )
        assert (
            AssetMapping.get_asset_decimals(
                "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p"
            )
            == 6
        )  # USDN
        assert AssetMapping.get_asset_decimals("unknown_asset") == 8  # Default

    def test_is_stablecoin(self):
        """Test stablecoin detection."""
        assert (
            AssetMapping.is_stablecoin("DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p")
            is True
        )  # USDN
        assert (
            AssetMapping.is_stablecoin("34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ")
            is True
        )  # USDT
        assert AssetMapping.is_stablecoin("WAVES") is False
        assert (
            AssetMapping.is_stablecoin("HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS")
            is False
        )

    def test_normalize_amount(self):
        """Test amount normalization."""
        # Test WAVES (8 decimals)
        normalized = AssetMapping.normalize_amount("WAVES", 100000000)
        assert normalized == Decimal("1.0")

        # Test USDN (6 decimals)
        normalized = AssetMapping.normalize_amount(
            "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p", 1000000
        )
        assert normalized == Decimal("1.0")

    def test_format_amount(self):
        """Test amount formatting."""
        # Test formatting with symbol
        formatted = AssetMapping.format_amount(
            "WAVES", Decimal("1.5"), include_symbol=True
        )
        assert "1.5" in formatted
        assert "WAVES" in formatted

        # Test formatting without symbol
        formatted = AssetMapping.format_amount(
            "WAVES", Decimal("1.5"), include_symbol=False
        )
        assert "1.5" in formatted
        assert "WAVES" not in formatted

    def test_get_assets_by_type(self):
        """Test filtering assets by type."""
        stablecoins = AssetMapping.get_assets_by_type("stable")
        tokens = AssetMapping.get_assets_by_type("token")

        assert len(stablecoins) > 0
        assert len(tokens) > 0

        # Check that all returned assets have correct type
        for asset_id, info in stablecoins.items():
            assert info.asset_type == "stable"


class TestFunctionMappings:
    """Test function mapping functions."""

    def test_get_function_info(self):
        """Test function info retrieval."""
        # Test swap function
        swap_info = FunctionMapping.get_function_info("swap")
        assert swap_info is not None
        assert swap_info.category == "swap"
        assert swap_info.contract_type == "swap"

        # Test unknown function
        assert FunctionMapping.get_function_info("unknown_function") is None

    def test_get_function_category(self):
        """Test function category detection."""
        assert FunctionMapping.get_function_category("swap") == "swap"
        assert FunctionMapping.get_function_category("stake") == "staking"
        assert FunctionMapping.get_function_category("addLiquidity") == "liquidity"
        assert FunctionMapping.get_function_category("unknown_function") is None

    def test_is_swap_function(self):
        """Test swap function detection."""
        assert FunctionMapping.is_swap_function("swap") is True
        assert FunctionMapping.is_swap_function("swapWithReferral") is True
        assert FunctionMapping.is_swap_function("stake") is False

    def test_is_staking_function(self):
        """Test staking function detection."""
        assert FunctionMapping.is_staking_function("stake") is True
        assert FunctionMapping.is_staking_function("unstake") is True
        assert FunctionMapping.is_staking_function("claimRewards") is True
        assert FunctionMapping.is_staking_function("swap") is False

    def test_is_liquidity_function(self):
        """Test liquidity function detection."""
        assert FunctionMapping.is_liquidity_function("addLiquidity") is True
        assert FunctionMapping.is_liquidity_function("removeLiquidity") is True
        assert FunctionMapping.is_liquidity_function("swap") is False

    def test_get_functions_by_category(self):
        """Test filtering functions by category."""
        swap_functions = FunctionMapping.get_functions_by_category("swap")
        staking_functions = FunctionMapping.get_functions_by_category("staking")

        assert len(swap_functions) > 0
        assert len(staking_functions) > 0

        # Check that all returned functions have correct category
        for func_name, info in swap_functions.items():
            assert info.category == "swap"

    def test_categorize_transaction(self):
        """Test transaction categorization."""
        assert FunctionMapping.categorize_transaction("swap") == "swap"
        assert FunctionMapping.categorize_transaction("stake") == "staking"
        assert FunctionMapping.categorize_transaction("addLiquidity") == "liquidity"
        assert FunctionMapping.categorize_transaction("unknown_function") == "general"

    def test_extract_function_from_invoke(self):
        """Test function extraction from invoke data."""
        # Test with valid invoke data
        invoke_data = {"call": {"function": "swap"}}
        function_name = FunctionMapping.extract_function_from_invoke(invoke_data)
        assert function_name == "swap"

        # Test with invalid data
        assert FunctionMapping.extract_function_from_invoke({}) is None
        assert FunctionMapping.extract_function_from_invoke(None) is None


class TestMappingIntegration:
    """Test integration between mapping systems."""

    def test_puzzle_ecosystem_consistency(self):
        """Test consistency across mapping systems."""
        # Test that PUZZLE token is consistently referenced
        puzzle_token_id = "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"

        # Should be in asset mapping
        puzzle_asset = AssetMapping.get_asset_info(puzzle_token_id)
        assert puzzle_asset is not None
        assert puzzle_asset.symbol == "PUZZLE"

        # Should be referenced in address mapping
        assert AddressMapping.PUZZLE_TOKEN_ID == puzzle_token_id

        # Staking address should be consistent
        staking_address = "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS"
        assert AddressMapping.PUZZLE_STAKING_ADDRESS == staking_address

        staking_info = AddressMapping.get_address_info(staking_address)
        assert staking_info is not None
        assert staking_info.type == "staking"

    def test_major_pools_have_assets(self):
        """Test that major pools reference known assets."""
        major_pools = AddressMapping.get_major_pools()

        for pool_addr, pool_info in major_pools.items():
            # Pool should have description mentioning asset pairs
            assert (
                "/" in pool_info.description or "pool" in pool_info.description.lower()
            )

    def test_stablecoin_consistency(self):
        """Test stablecoin identification consistency."""
        stablecoins = AssetMapping.get_stablecoins()

        for asset_id, asset_info in stablecoins.items():
            # Should be marked as stablecoin
            assert AssetMapping.is_stablecoin(asset_id)
            assert asset_info.asset_type == "stable"
            assert "usd" in asset_info.tags or "stable" in asset_info.tags
