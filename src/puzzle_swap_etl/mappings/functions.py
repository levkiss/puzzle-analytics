"""Function name mappings for Puzzle ecosystem smart contracts."""

from typing import Dict, List

# Swap-related functions
SWAP_FUNCTIONS = [
    "swap",
    "swapWithReferral",
    "swapToExactAmount",
    "swapFromExactAmount",
]

# Staking-related functions
STAKING_FUNCTIONS = [
    "stake",
    "unstake",
    "claim",
    "claimReward",
    "claimIndexRewards",
    "unstakeIndex",
    "stakeIndex",
]

# Lending-related functions
LENDING_FUNCTIONS = [
    "supply",
    "withdraw",
    "borrow",
    "repay",
    "liquidate",
    "updateInterest",
]

# Pool management functions
POOL_FUNCTIONS = [
    "init",
    "preInit",
    "addLiquidity",
    "removeLiquidity",
    "setRebalancingPlan",
    "rebalance",
    "updateWeights",
]

# Oracle functions
ORACLE_FUNCTIONS = [
    "updatePrice",
    "getPrice",
    "setPriceData",
]

# Governance functions
GOVERNANCE_FUNCTIONS = [
    "vote",
    "propose",
    "execute",
    "delegate",
]

# Fee collection functions
FEE_FUNCTIONS = [
    "topUpReward",
    "collectFees",
    "distributeFees",
]

# All important functions for monitoring
IMPORTANT_FUNCTIONS = (
    SWAP_FUNCTIONS
    + STAKING_FUNCTIONS
    + LENDING_FUNCTIONS
    + POOL_FUNCTIONS
    + ORACLE_FUNCTIONS
    + FEE_FUNCTIONS
)

# Function categories
FUNCTION_CATEGORIES: Dict[str, str] = {
    # Swap functions
    "swap": "swap",
    "swapWithReferral": "swap",
    "swapToExactAmount": "swap",
    "swapFromExactAmount": "swap",
    # Staking functions
    "stake": "staking",
    "unstake": "staking",
    "claim": "staking",
    "claimReward": "staking",
    "claimIndexRewards": "staking",
    "unstakeIndex": "staking",
    "stakeIndex": "staking",
    # Lending functions
    "supply": "lending",
    "withdraw": "lending",
    "borrow": "lending",
    "repay": "lending",
    "liquidate": "lending",
    "updateInterest": "lending",
    # Pool functions
    "init": "pool",
    "preInit": "pool",
    "addLiquidity": "pool",
    "removeLiquidity": "pool",
    "setRebalancingPlan": "pool",
    "rebalance": "pool",
    "updateWeights": "pool",
    # Oracle functions
    "updatePrice": "oracle",
    "getPrice": "oracle",
    "setPriceData": "oracle",
    # Governance functions
    "vote": "governance",
    "propose": "governance",
    "execute": "governance",
    "delegate": "governance",
    # Fee functions
    "topUpReward": "fee",
    "collectFees": "fee",
    "distributeFees": "fee",
}

# Function descriptions
FUNCTION_DESCRIPTIONS: Dict[str, str] = {
    # Swap functions
    "swap": "Execute a token swap",
    "swapWithReferral": "Execute a token swap with referral",
    "swapToExactAmount": "Swap to get exact output amount",
    "swapFromExactAmount": "Swap from exact input amount",
    # Staking functions
    "stake": "Stake tokens for rewards",
    "unstake": "Unstake tokens",
    "claim": "Claim staking rewards",
    "claimReward": "Claim staking rewards",
    "claimIndexRewards": "Claim index-based rewards",
    "unstakeIndex": "Unstake from index",
    "stakeIndex": "Stake to index",
    # Lending functions
    "supply": "Supply tokens to lending pool",
    "withdraw": "Withdraw tokens from lending pool",
    "borrow": "Borrow tokens from lending pool",
    "repay": "Repay borrowed tokens",
    "liquidate": "Liquidate undercollateralized position",
    "updateInterest": "Update interest rates",
    # Pool functions
    "init": "Initialize pool",
    "preInit": "Pre-initialize pool",
    "addLiquidity": "Add liquidity to pool",
    "removeLiquidity": "Remove liquidity from pool",
    "setRebalancingPlan": "Set pool rebalancing plan",
    "rebalance": "Execute pool rebalancing",
    "updateWeights": "Update pool weights",
    # Oracle functions
    "updatePrice": "Update asset price",
    "getPrice": "Get asset price",
    "setPriceData": "Set price data",
    # Governance functions
    "vote": "Vote on proposal",
    "propose": "Create governance proposal",
    "execute": "Execute governance proposal",
    "delegate": "Delegate voting power",
    # Fee functions
    "topUpReward": "Top up reward pool",
    "collectFees": "Collect protocol fees",
    "distributeFees": "Distribute collected fees",
}

# Functions that generate volume
VOLUME_GENERATING_FUNCTIONS = SWAP_FUNCTIONS

# Functions that affect staking
STAKING_AFFECTING_FUNCTIONS = STAKING_FUNCTIONS

# Functions that affect liquidity
LIQUIDITY_AFFECTING_FUNCTIONS = [
    "addLiquidity",
    "removeLiquidity",
    "init",
    "preInit",
]


def get_function_category(function_name: str) -> str:
    """Get the category of a function."""
    return FUNCTION_CATEGORIES.get(function_name, "unknown")


def get_function_description(function_name: str) -> str:
    """Get description of a function."""
    return FUNCTION_DESCRIPTIONS.get(
        function_name, f"Unknown function: {function_name}"
    )


def is_swap_function(function_name: str) -> bool:
    """Check if function is swap-related."""
    return function_name in SWAP_FUNCTIONS


def is_staking_function(function_name: str) -> bool:
    """Check if function is staking-related."""
    return function_name in STAKING_FUNCTIONS


def is_lending_function(function_name: str) -> bool:
    """Check if function is lending-related."""
    return function_name in LENDING_FUNCTIONS


def is_pool_function(function_name: str) -> bool:
    """Check if function is pool-related."""
    return function_name in POOL_FUNCTIONS


def is_volume_generating(function_name: str) -> bool:
    """Check if function generates trading volume."""
    return function_name in VOLUME_GENERATING_FUNCTIONS


def is_liquidity_affecting(function_name: str) -> bool:
    """Check if function affects pool liquidity."""
    return function_name in LIQUIDITY_AFFECTING_FUNCTIONS


def get_functions_by_category(category: str) -> List[str]:
    """Get all functions in a specific category."""
    return [func for func, cat in FUNCTION_CATEGORIES.items() if cat == category]


# Priority functions for each address type
ADDRESS_PRIORITY_FUNCTIONS: Dict[str, List[str]] = {
    "staking": STAKING_FUNCTIONS,
    "lending": LENDING_FUNCTIONS,
    "pool": SWAP_FUNCTIONS + POOL_FUNCTIONS,
    "oracle": ORACLE_FUNCTIONS,
    "governance": GOVERNANCE_FUNCTIONS,
}


def get_priority_functions_for_address_type(address_type: str) -> List[str]:
    """Get priority functions for a specific address type."""
    return ADDRESS_PRIORITY_FUNCTIONS.get(address_type, IMPORTANT_FUNCTIONS)
