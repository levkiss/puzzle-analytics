"""Asset mappings for Waves blockchain and Puzzle Swap ecosystem."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class AssetInfo:
    """Information about a blockchain asset."""

    id: str
    symbol: str
    name: str
    decimals: int
    description: str = ""
    issuer: Optional[str] = None
    verified: bool = False
    asset_type: str = "token"  # 'token', 'stable', 'wrapped', 'nft'
    tags: List[str] = None
    coingecko_id: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AssetMapping:
    """Centralized asset mapping for Waves ecosystem."""

    # Native Waves Asset
    WAVES_ID = "WAVES"

    # Core Puzzle Assets
    PUZZLE_TOKEN_ID = "HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS"

    # Major Assets on Waves
    MAJOR_ASSETS = {
        WAVES_ID: AssetInfo(
            id=WAVES_ID,
            symbol="WAVES",
            name="Waves",
            decimals=8,
            description="Native Waves blockchain token",
            verified=True,
            asset_type="token",
            tags=["native", "major", "payment"],
            coingecko_id="waves",
        ),
        PUZZLE_TOKEN_ID: AssetInfo(
            id=PUZZLE_TOKEN_ID,
            symbol="PUZZLE",
            name="Puzzle",
            decimals=8,
            description="Puzzle Swap governance and utility token",
            issuer="3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS",
            verified=True,
            asset_type="token",
            tags=["puzzle", "governance", "defi", "major"],
            coingecko_id="puzzle",
        ),
        "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p": AssetInfo(
            id="DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p",
            symbol="USDN",
            name="Neutrino USD",
            decimals=6,
            description="Neutrino USD stablecoin",
            issuer="3PC9BfRwJWWiw9AREE2B3eWzCks3CYtg4yo",
            verified=True,
            asset_type="stable",
            tags=["stable", "major", "usd"],
            coingecko_id="neutrino",
        ),
        "34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ": AssetInfo(
            id="34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ",
            symbol="USDT",
            name="Tether USD",
            decimals=6,
            description="Tether USD stablecoin",
            issuer="3PLHVWCqA9DJPDbadUofTohnCULLauiDWhS",
            verified=True,
            asset_type="stable",
            tags=["stable", "major", "usd"],
            coingecko_id="tether",
        ),
        "8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS": AssetInfo(
            id="8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS",
            symbol="BTC",
            name="Bitcoin",
            decimals=8,
            description="Wrapped Bitcoin on Waves",
            issuer="3P2uzAzX9XTu1t32GkWw68YFFLwtapWvDds",
            verified=True,
            asset_type="wrapped",
            tags=["wrapped", "major", "btc"],
            coingecko_id="bitcoin",
        ),
        "474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu": AssetInfo(
            id="474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu",
            symbol="ETH",
            name="Ethereum",
            decimals=8,
            description="Wrapped Ethereum on Waves",
            issuer="3P2uzAzX9XTu1t32GkWw68YFFLwtapWvDds",
            verified=True,
            asset_type="wrapped",
            tags=["wrapped", "major", "eth"],
            coingecko_id="ethereum",
        ),
        "6nSpVyNH7yM69eg446wrQR94ipbbcmZMU1ENPwanC97g": AssetInfo(
            id="6nSpVyNH7yM69eg446wrQR94ipbbcmZMU1ENPwanC97g",
            symbol="USDC",
            name="USD Coin",
            decimals=6,
            description="USD Coin stablecoin",
            issuer="3PLHVWCqA9DJPDbadUofTohnCULLauiDWhS",
            verified=True,
            asset_type="stable",
            tags=["stable", "major", "usd"],
            coingecko_id="usd-coin",
        ),
    }

    # DeFi Protocol Tokens
    DEFI_TOKENS = {
        "Ehie5xYpeN8op1Cctc6aGUrqx8jq3jtf1DSjXDbfm7aT": AssetInfo(
            id="Ehie5xYpeN8op1Cctc6aGUrqx8jq3jtf1DSjXDbfm7aT",
            symbol="SWOP",
            name="Swop",
            decimals=8,
            description="Swop.fi governance token",
            issuer="3P2HNUd5VUPLMQkJmctTPEeeHumiPN2GkTb",
            verified=True,
            asset_type="token",
            tags=["defi", "governance", "dex"],
            coingecko_id="swop",
        ),
        "6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ": AssetInfo(
            id="6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ",
            symbol="EGG",
            name="Waves Ducks",
            decimals=8,
            description="Waves Ducks game token",
            issuer="3P9o3ZYwtHkaU1KxsKkFjJqJKS3dLHLC9oF",
            verified=True,
            asset_type="token",
            tags=["gaming", "nft"],
            coingecko_id="waves-ducks",
        ),
        "AAHG5gzQeWfqhR9K4rptpyDDoo9SgAEiEsQEP1Rge2zG": AssetInfo(
            id="AAHG5gzQeWfqhR9K4rptpyDDoo9SgAEiEsQEP1Rge2zG",
            symbol="SIGN",
            name="SignatureChain",
            decimals=8,
            description="SignatureChain token",
            issuer="3P274YB5qseSE9DTTL3bpSjosZrYBPDpJ8k",
            verified=True,
            asset_type="token",
            tags=["utility"],
            coingecko_id="signaturechain",
        ),
    }

    # LP Tokens (Liquidity Provider tokens)
    LP_TOKENS = {
        "3P2uzAzX9XTu1t32GkWw68YFFLwtapWvDds_LP": AssetInfo(
            id="3P2uzAzX9XTu1t32GkWw68YFFLwtapWvDds_LP",
            symbol="PUZZLE-USDN-LP",
            name="Puzzle-USDN LP Token",
            decimals=8,
            description="Liquidity provider token for PUZZLE/USDN pool",
            asset_type="token",
            tags=["lp", "puzzle", "defi"],
        ),
        "3PJaBXZu5rNjKJhZLYnHjhKdDhqUGdZgLzs_LP": AssetInfo(
            id="3PJaBXZu5rNjKJhZLYnHjhKdDhqUGdZgLzs_LP",
            symbol="PUZZLE-WAVES-LP",
            name="Puzzle-Waves LP Token",
            decimals=8,
            description="Liquidity provider token for PUZZLE/WAVES pool",
            asset_type="token",
            tags=["lp", "puzzle", "defi"],
        ),
    }

    # Stablecoins
    STABLECOINS = {
        "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p",  # USDN
        "34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ",  # USDT
        "6nSpVyNH7yM69eg446wrQR94ipbbcmZMU1ENPwanC97g",  # USDC
    }

    # Major trading assets
    MAJOR_TRADING_ASSETS = {
        WAVES_ID,
        PUZZLE_TOKEN_ID,
        "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p",  # USDN
        "34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ",  # USDT
        "8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS",  # BTC
        "474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu",  # ETH
    }

    @classmethod
    def get_all_assets(cls) -> Dict[str, AssetInfo]:
        """Get all known assets."""
        all_assets = {}
        all_assets.update(cls.MAJOR_ASSETS)
        all_assets.update(cls.DEFI_TOKENS)
        all_assets.update(cls.LP_TOKENS)
        return all_assets

    @classmethod
    def get_asset_info(cls, asset_id: str) -> Optional[AssetInfo]:
        """Get information about a specific asset."""
        all_assets = cls.get_all_assets()
        return all_assets.get(asset_id)

    @classmethod
    def get_asset_symbol(cls, asset_id: str) -> str:
        """Get asset symbol, fallback to asset ID if unknown."""
        asset_info = cls.get_asset_info(asset_id)
        return asset_info.symbol if asset_info else asset_id[:8] + "..."

    @classmethod
    def get_asset_decimals(cls, asset_id: str) -> int:
        """Get asset decimals, fallback to 8 if unknown."""
        asset_info = cls.get_asset_info(asset_id)
        return asset_info.decimals if asset_info else 8

    @classmethod
    def get_asset_name(cls, asset_id: str) -> str:
        """Get asset name, fallback to symbol if unknown."""
        asset_info = cls.get_asset_info(asset_id)
        if asset_info:
            return asset_info.name
        return cls.get_asset_symbol(asset_id)

    @classmethod
    def is_stablecoin(cls, asset_id: str) -> bool:
        """Check if asset is a stablecoin."""
        return asset_id in cls.STABLECOINS

    @classmethod
    def is_major_asset(cls, asset_id: str) -> bool:
        """Check if asset is a major trading asset."""
        return asset_id in cls.MAJOR_TRADING_ASSETS

    @classmethod
    def is_verified(cls, asset_id: str) -> bool:
        """Check if asset is verified."""
        asset_info = cls.get_asset_info(asset_id)
        return asset_info.verified if asset_info else False

    @classmethod
    def get_assets_by_type(cls, asset_type: str) -> Dict[str, AssetInfo]:
        """Get all assets of a specific type."""
        all_assets = cls.get_all_assets()
        return {
            asset_id: info
            for asset_id, info in all_assets.items()
            if info.asset_type == asset_type
        }

    @classmethod
    def get_assets_by_tag(cls, tag: str) -> Dict[str, AssetInfo]:
        """Get all assets with a specific tag."""
        all_assets = cls.get_all_assets()
        return {
            asset_id: info for asset_id, info in all_assets.items() if tag in info.tags
        }

    @classmethod
    def get_stablecoins(cls) -> Dict[str, AssetInfo]:
        """Get all stablecoin assets."""
        return cls.get_assets_by_type("stable")

    @classmethod
    def get_defi_tokens(cls) -> Dict[str, AssetInfo]:
        """Get all DeFi protocol tokens."""
        return cls.get_assets_by_tag("defi")

    @classmethod
    def get_lp_tokens(cls) -> Dict[str, AssetInfo]:
        """Get all LP tokens."""
        return cls.get_assets_by_tag("lp")

    @classmethod
    def get_puzzle_related_assets(cls) -> Dict[str, AssetInfo]:
        """Get all Puzzle-related assets."""
        return cls.get_assets_by_tag("puzzle")

    @classmethod
    def normalize_amount(cls, asset_id: str, raw_amount: int) -> Decimal:
        """Normalize raw blockchain amount to decimal representation."""
        decimals = cls.get_asset_decimals(asset_id)
        return Decimal(raw_amount) / Decimal(10**decimals)

    @classmethod
    def denormalize_amount(cls, asset_id: str, decimal_amount: Decimal) -> int:
        """Convert decimal amount to raw blockchain representation."""
        decimals = cls.get_asset_decimals(asset_id)
        return int(decimal_amount * Decimal(10**decimals))

    @classmethod
    def format_amount(
        cls, asset_id: str, amount: Decimal, include_symbol: bool = True
    ) -> str:
        """Format amount with appropriate precision and symbol."""
        asset_info = cls.get_asset_info(asset_id)

        if asset_info:
            # Use appropriate precision based on asset type
            if asset_info.asset_type == "stable":
                precision = 2
            elif asset_id == cls.WAVES_ID:
                precision = 4
            else:
                precision = 6
        else:
            precision = 8

        formatted = f"{amount:.{precision}f}".rstrip("0").rstrip(".")

        if include_symbol:
            symbol = cls.get_asset_symbol(asset_id)
            return f"{formatted} {symbol}"

        return formatted

    @classmethod
    def get_coingecko_id(cls, asset_id: str) -> Optional[str]:
        """Get CoinGecko ID for price data."""
        asset_info = cls.get_asset_info(asset_id)
        return asset_info.coingecko_id if asset_info else None


# Compatibility exports for backward compatibility
WAVES_ID = AssetMapping.WAVES_ID
PUZZLE_TOKEN_ID = AssetMapping.PUZZLE_TOKEN_ID

# Major stablecoin IDs
USDN_ID = "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p"
USDT_ID = "34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ"
USDC_ID = "6nSpVyNH7yM69eg446wrQR94ipbbcmZMU1ENPwanC97g"

# Asset decimals mapping for quick access
ASSET_DECIMALS = {
    asset_id: info.decimals for asset_id, info in AssetMapping.get_all_assets().items()
}

# Asset names mapping for quick access
ASSET_NAMES = {
    asset_id: info.name for asset_id, info in AssetMapping.get_all_assets().items()
}

# Major assets list for quick access
MAJOR_ASSETS = list(AssetMapping.MAJOR_TRADING_ASSETS)
