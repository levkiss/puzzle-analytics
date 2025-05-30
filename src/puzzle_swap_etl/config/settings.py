"""Configuration settings for the Puzzle Swap ETL pipeline."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/puzzle_swap",
        description="PostgreSQL database URL",
        examples=["postgresql+asyncpg://user:password@localhost:5432/puzzle_swap"],
    )

    @property
    def database_user(self) -> str:
        """Extract database username from database URL."""
        try:
            # Parse URL to extract username
            # Format: postgresql+asyncpg://username:password@host:port/database
            url_parts = self.database_url.split("://")[1]  # Remove protocol
            user_part = url_parts.split("@")[0]  # Get user:password part
            username = user_part.split(":")[0]  # Get username
            return username
        except Exception:
            return "puzzle_user"  # Default fallback

    # Waves Blockchain Configuration
    waves_node_url: str = Field(
        default="https://nodes.wx.network/",
        description="Primary Waves node URL",
    )
    waves_node_backup_url: str = Field(
        default="http://38.242.253.187:6869/",
        description="Backup Waves node URL",
    )

    @property
    def waves_node_urls(self) -> List[str]:
        """Get list of available Waves node URLs."""
        return [self.waves_node_url, self.waves_node_backup_url]

    # Puzzle Swap Configuration
    puzzle_token_id: str = Field(
        default="HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS",
        description="Puzzle token asset ID",
    )
    puzzle_staking_address: str = Field(
        default="3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS",
        description="Puzzle staking contract address",
    )
    puzzle_oracle_address: str = Field(
        default="3P8d1E1BLKoD52y3bQJ1bDTd2TD1gpaLn9t",
        description="Puzzle oracle contract address",
    )

    # API Configuration
    aggregator_url: str = Field(
        default="https://swapapi.puzzleswap.org/",
        description="Puzzle aggregator API URL",
    )
    puzzle_base_api_url: str = Field(
        default="https://puzzle-js-back.herokuapp.com/api/v1/pools",
        description="Puzzle base API URL for pool information",
    )

    # ETL Configuration
    batch_size: int = Field(
        default=1000,
        description="Batch size for processing transactions",
        ge=1,
        le=10000,
    )
    max_transactions_in_memory: int = Field(
        default=300000,
        description="Maximum transactions to keep in memory before using files",
        ge=1000,
    )
    worker_threads: int = Field(
        default=2,
        description="Number of worker threads for parallel processing",
        ge=1,
        le=10,
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
        pattern="^(json|text)$",
    )

    # Development Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )


# Global settings instance
settings = Settings()
