# Puzzle Swap ETL - Mapping System Documentation

This document describes the comprehensive mapping system implemented for the Puzzle Swap ETL pipeline. The mapping system provides centralized management of addresses, assets, and smart contract functions in the Puzzle Swap and Waves ecosystem.

## Overview

The mapping system consists of three main components:

1. **AddressMapping** - Manages blockchain addresses (pools, staking contracts, protocols)
2. **AssetMapping** - Handles asset information and amount normalization
3. **FunctionMapping** - Categorizes smart contract functions and interactions

## Architecture

```
src/puzzle_swap_etl/mappings/
├── __init__.py          # Package exports
├── addresses.py         # Address mappings and utilities
├── assets.py           # Asset mappings and utilities
└── functions.py        # Function mappings and utilities
```

## AddressMapping

### Features
- **Comprehensive Coverage**: Pool addresses, staking contracts, protocol addresses
- **Categorization**: Type-based grouping (pool, staking, protocol, oracle, governance)
- **Tagging System**: Flexible tagging for filtering (major, stable, puzzle, etc.)
- **Metadata**: Names, descriptions, activity status

### Key Addresses
- **PUZZLE Token**: `HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS`
- **Staking Contract**: `3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS`
- **Oracle Contract**: `3P8d1E1BLKoD52y3bQJ1bDTd2TD1gpaLn9t`
- **Governance**: `3P6J84oH51DzY6xk2mT5TheXRbrCwBMxonp`

### Major Pools
- WAVES/USDN Pool: `3PFQjjDMiZKQZdu5JqTHD7HwgSXyp9Rw9By`
- WAVES/USDT Pool: `3P73HDkPqG15nLXevjCbmXtazHYTZbpPoPw`
- PUZZLE/WAVES Pool: `3PJaBXZu5rNjKJhZLYnHjhKdDhqUGdZgLzs`
- PUZZLE/USDN Pool: `3P2uzAzX9XTu1t32GkWw68YFFLwtapWvDds`

### Usage Examples
```python
from puzzle_swap_etl.mappings import AddressMapping

# Check if address is Puzzle-related
is_puzzle = AddressMapping.is_puzzle_related(address)

# Get address information
info = AddressMapping.get_address_info(address)
print(f"{info.name}: {info.description}")

# Filter by type or tag
pools = AddressMapping.get_addresses_by_type("pool")
major_pools = AddressMapping.get_addresses_by_tag("major")
```

## AssetMapping

### Features
- **Asset Information**: Symbol, name, decimals, issuer, verification status
- **Amount Normalization**: Convert between raw blockchain amounts and decimal representation
- **Categorization**: Token types (token, stable, wrapped, nft)
- **Formatting**: Display-friendly amount formatting
- **Price Integration**: CoinGecko ID mapping for price data

### Major Assets
- **WAVES**: Native blockchain token
- **PUZZLE**: `HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS`
- **USDN**: `DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p`
- **USDT**: `34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ`
- **BTC**: `8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS`
- **ETH**: `474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu`

### Usage Examples
```python
from puzzle_swap_etl.mappings import AssetMapping
from decimal import Decimal

# Get asset information
asset_info = AssetMapping.get_asset_info(asset_id)

# Normalize amounts
raw_amount = 100000000  # 1 PUZZLE (8 decimals)
normalized = AssetMapping.normalize_amount(asset_id, raw_amount)

# Format for display
formatted = AssetMapping.format_amount(asset_id, normalized)

# Check properties
is_stable = AssetMapping.is_stablecoin(asset_id)
is_verified = AssetMapping.is_verified(asset_id)
```

## FunctionMapping

### Features
- **Comprehensive Coverage**: Swap, staking, liquidity, governance, oracle functions
- **Categorization**: Function categories (swap, staking, liquidity, governance, view, admin)
- **Parameter Mapping**: Input/output parameter definitions
- **Transaction Analysis**: Extract and categorize functions from invoke transactions
- **Integration**: Cross-reference with address and asset mappings

### Function Categories

#### Swap Functions
- `swap` - Basic token swap
- `swapWithReferral` - Swap with referral program
- `multiSwap` - Multi-hop routing
- `exactOutput` - Exact output swaps

#### Staking Functions
- `stake` - Stake PUZZLE tokens
- `unstake` - Unstake tokens
- `claimRewards` - Claim staking rewards
- `compound` - Auto-compound rewards
- `emergencyWithdraw` - Emergency withdrawal

#### Liquidity Functions
- `addLiquidity` - Add liquidity to pools
- `removeLiquidity` - Remove liquidity
- `addLiquidityETH` - Add liquidity with WAVES
- `removeLiquidityETH` - Remove liquidity to WAVES

#### View Functions
- `getReserves` - Get pool reserves
- `getAmountOut` - Calculate swap output
- `getUserStake` - Get user staking info
- `getPoolInfo` - Get pool information

### Usage Examples
```python
from puzzle_swap_etl.mappings import FunctionMapping

# Get function information
function_info = FunctionMapping.get_function_info("swap")

# Check function types
is_swap = FunctionMapping.is_swap_function("swap")
is_staking = FunctionMapping.is_staking_function("stake")

# Extract from transaction
function_name = FunctionMapping.extract_function_from_invoke(invoke_data)

# Categorize transaction
category = FunctionMapping.categorize_transaction(function_name)
```

## Integration with ETL Pipeline

### Transformers
The mapping system is integrated into the transformation layer:

```python
# In SwapTransformer
def _is_swap_transaction(self, transaction):
    # Check if involves known pool addresses
    if transaction.sender in AddressMapping.get_pool_addresses():
        return True
    
    # Check function name
    function_name = FunctionMapping.extract_function_from_invoke(transaction.raw_data)
    return FunctionMapping.is_swap_function(function_name)

# In StakingTransformer  
def _parse_staking_details(self, invoke_data, transaction, event_type):
    # Normalize amounts using asset mapping
    amount = AssetMapping.normalize_amount(asset_id, raw_amount)
    return {"amount": amount, "amount_usd": usd_value}
```

### Data Quality
- **Validation**: Verify addresses and assets against known mappings
- **Enrichment**: Add metadata (names, descriptions, categories)
- **Normalization**: Consistent amount handling across different assets
- **Classification**: Automatic transaction categorization

## Maintenance and Updates

### Adding New Mappings

1. **New Pool Address**:
```python
"3PNewPoolAddress": AddressInfo(
    address="3PNewPoolAddress",
    name="NEW/WAVES Pool",
    type="pool",
    description="NEW token trading pool",
    tags=["pool", "new-token"]
)
```

2. **New Asset**:
```python
"NewAssetId": AssetInfo(
    id="NewAssetId",
    symbol="NEW",
    name="New Token",
    decimals=8,
    description="New protocol token",
    verified=True,
    asset_type="token",
    tags=["defi", "new"]
)
```

3. **New Function**:
```python
"newFunction": FunctionInfo(
    name="newFunction",
    contract_type="swap",
    description="New swap function",
    parameters=["param1", "param2"],
    category="swap",
    tags=["trading", "new"]
)
```

### Best Practices

1. **Consistency**: Use consistent naming and categorization
2. **Documentation**: Include clear descriptions and tags
3. **Verification**: Mark verified/trusted assets and addresses
4. **Testing**: Test new mappings with the test script
5. **Validation**: Ensure cross-mapping relationships are correct

## Testing

Run the mapping tests to verify functionality:

```bash
poetry run python -c "
from src.puzzle_swap_etl.mappings import AddressMapping, AssetMapping, FunctionMapping

# Test basic functionality
print('Addresses:', len(AddressMapping.get_all_addresses()))
print('Assets:', len(AssetMapping.get_all_assets()))
print('Functions:', len(FunctionMapping.get_all_functions()))
"
```

## Performance Considerations

- **Caching**: Mappings are loaded once and cached in memory
- **Lookup Speed**: O(1) dictionary lookups for most operations
- **Memory Usage**: Minimal overhead for mapping data
- **Lazy Loading**: Only load mappings when needed

## Future Enhancements

1. **Dynamic Loading**: Load mappings from external sources (APIs, databases)
2. **Versioning**: Track mapping changes over time
3. **Validation**: Automated validation against blockchain data
4. **Analytics**: Usage statistics and mapping effectiveness metrics
5. **Community**: Community-driven mapping contributions

---

For more information, see the main [README.md](README.md) and [API documentation](docs/api.md). 