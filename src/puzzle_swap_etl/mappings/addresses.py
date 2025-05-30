"""Address mappings for the Puzzle ecosystem."""

from typing import Dict, List

# Core Puzzle Protocol Addresses
PUZZLE_STAKING_ADDRESS = "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS"
PUZZLE_ORACLE_ADDRESS = "3P8d1E1BLKoD52y3bQJ1bDTd2TD1gpaLn9t"
PUZZLE_BOOSTER_ADDRESS = "3P8eeDzUnoDNbQjW617pAe76cEUDQsP1m1V"
PUZZLE_ARTEFACTS_ADDRESS = "3PFkgvC9y6zHy64zEAscKKgaNY3yipiLqbW"
REX_AGGREGATOR_ADDRESS = "3PGFHzVGT4NTigwCKP1NcwoXkodVZwvBuuU"
PUZZLE_LIMITS_ADDRESS = "3PFB6LJyShsCKEA1AU1U1WLbDazqyj6ZL9b"

# Protocol Fee Collectors
PROTOCOL_FEES_COLLECTORS = [
    "3P4kBiU4wr2yV1S5gMfu3MdkVvy7kxXHsKe",
    "3PFWAVKmXjfHXyzJb12jCbhP4Uhi9t4uWiD",
    "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS",
]

# Main protocol fee collector
MAIN_PROTOCOL_FEE_COLLECTOR = "3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS"

# Staking Addresses
EAGLES_STAKING_ADDRESS = "3PKUxbZaSYfsR7wu2HaAgiirHYwAMupDrYW"
ARKIMALS_EAGLES_ADDRESS = "3PGrthrFFZVfvZeCyrZmEXJ1P29ViPbcy5g"
POWER_DAO_ADDRESS = "3PEwRcYNAUtoFvKpBhKoiwajnZfdoDR6h4h"

# PuzzleLend Addresses
PL_MAIN = "3P4uA5etnZi4AmBabKinq2bMiWU8KcnHZdH"
PL_ROME = "3P8Df2b7ywHtLBHBe8PBVQYd3A5MdEEJAou"
PL_DEFI = "3P4DK5VzDwL3vfc5ahUEhtoe5ByZNyacJ3X"
PL_LOWCAP = "3PHpuQUPVUoR3AYzFeJzeWJfYLsLTmWssVH"
PL_COLD_STORAGE = "3P4QjKNNVnEJdmcvPezmoTvsqpmhtxX2SaA"

PUZZLE_LEND_ADDRESSES = [PL_MAIN, PL_ROME, PL_DEFI, PL_LOWCAP, PL_COLD_STORAGE]
PUZZLE_LEND_WITH_PUZZLE = [PL_MAIN, PL_DEFI]

# Protocol Addresses (for allocation tracking)
PROTOCOL_ADDRESSES = [
    EAGLES_STAKING_ADDRESS,
    ARKIMALS_EAGLES_ADDRESS,
    POWER_DAO_ADDRESS,
] + PUZZLE_LEND_ADDRESSES

# Team Addresses (to be populated as needed)
TEAM_ADDRESSES: List[str] = []

# Locked Addresses (tokens that are locked/vested)
LOCKED_ADDRESSES = [
    ARKIMALS_EAGLES_ADDRESS,
]

# Address to human-readable name mappings
ADDRESS_NAMES: Dict[str, str] = {
    # Core Protocol
    PUZZLE_STAKING_ADDRESS: "Puzzle Staking",
    PUZZLE_ORACLE_ADDRESS: "Puzzle Oracle",
    PUZZLE_BOOSTER_ADDRESS: "Puzzle Booster",
    PUZZLE_ARTEFACTS_ADDRESS: "Puzzle Artefacts",
    REX_AGGREGATOR_ADDRESS: "Rex Aggregator",
    PUZZLE_LIMITS_ADDRESS: "Puzzle Limit Orders",
    # Staking
    EAGLES_STAKING_ADDRESS: "Eagles Staking",
    ARKIMALS_EAGLES_ADDRESS: "Arkimals Eagles",
    POWER_DAO_ADDRESS: "Power DAO",
    # Lending
    PL_MAIN: "Puzzle Lend Main Market",
    PL_ROME: "Puzzle Lend Rome Market",
    PL_DEFI: "Puzzle Lend DEFI Market",
    PL_LOWCAP: "Puzzle Lend Lowcap Market",
    PL_COLD_STORAGE: "Puzzle Lend Cold Storage",
}

# Address categories for easier filtering
STAKING_ADDRESSES = [
    PUZZLE_STAKING_ADDRESS,
    EAGLES_STAKING_ADDRESS,
    ARKIMALS_EAGLES_ADDRESS,
    POWER_DAO_ADDRESS,
]

LENDING_ADDRESSES = PUZZLE_LEND_ADDRESSES

CORE_PROTOCOL_ADDRESSES = [
    PUZZLE_ORACLE_ADDRESS,
    PUZZLE_BOOSTER_ADDRESS,
    PUZZLE_ARTEFACTS_ADDRESS,
    REX_AGGREGATOR_ADDRESS,
    PUZZLE_LIMITS_ADDRESS,
]

# All important addresses for monitoring
ALL_IMPORTANT_ADDRESSES = (
    STAKING_ADDRESSES
    + LENDING_ADDRESSES
    + CORE_PROTOCOL_ADDRESSES
    + PROTOCOL_FEES_COLLECTORS
)

# Address type mappings
ADDRESS_TYPES: Dict[str, str] = {
    # Staking
    PUZZLE_STAKING_ADDRESS: "staking",
    EAGLES_STAKING_ADDRESS: "staking",
    ARKIMALS_EAGLES_ADDRESS: "staking",
    POWER_DAO_ADDRESS: "staking",
    # Lending
    PL_MAIN: "lending",
    PL_ROME: "lending",
    PL_DEFI: "lending",
    PL_LOWCAP: "lending",
    PL_COLD_STORAGE: "lending",
    # Core Protocol
    PUZZLE_ORACLE_ADDRESS: "oracle",
    PUZZLE_BOOSTER_ADDRESS: "booster",
    PUZZLE_ARTEFACTS_ADDRESS: "nft",
    REX_AGGREGATOR_ADDRESS: "aggregator",
    PUZZLE_LIMITS_ADDRESS: "trading",
}


def get_address_name(address: str) -> str:
    """Get human-readable name for an address."""
    return ADDRESS_NAMES.get(address, f"Unknown ({address[:8]}...)")


def get_address_type(address: str) -> str:
    """Get the type/category of an address."""
    return ADDRESS_TYPES.get(address, "unknown")


def is_protocol_address(address: str) -> bool:
    """Check if address belongs to a protocol."""
    return address in PROTOCOL_ADDRESSES


def is_staking_address(address: str) -> bool:
    """Check if address is a staking contract."""
    return address in STAKING_ADDRESSES


def is_lending_address(address: str) -> bool:
    """Check if address is a lending contract."""
    return address in LENDING_ADDRESSES


def is_fee_collector(address: str) -> bool:
    """Check if address is a protocol fee collector."""
    return address in PROTOCOL_FEES_COLLECTORS
