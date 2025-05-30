# Puzzle Swap ETL

A professional ETL (Extract, Transform, Load) pipeline for extracting and analyzing Puzzle Swap blockchain data from the Waves blockchain.

## Overview

This project extracts transaction data from the Waves blockchain, processes it to calculate key metrics for the Puzzle Swap exchange, and stores the results in a PostgreSQL database for analysis and visualization with Apache Superset.

## Key Metrics

The ETL pipeline calculates the following metrics:

- **Количество обменов** (Number of swaps)
- **Топ трейдеров** (Top traders)
- **Объем свопов по парам** (Swap volume by pairs)
- **Общий объём застейканных Puzzle** (Total staked Puzzle tokens)
- **Количество уникальных стейкеров Puzzle** (Number of unique Puzzle stakers)

## Architecture

```
src/puzzle_swap_etl/
├── config/          # Configuration management
├── database/        # Database models and connections
├── extractors/      # Blockchain data extraction
├── transformers/    # Data transformation logic
├── loaders/         # Data loading to PostgreSQL
├── models/          # Pydantic data models
└── utils/           # Utility functions
```

## Installation

### Prerequisites

- Python 3.9+
- Poetry
- PostgreSQL database

### Setup

1. Clone the repository and navigate to the project directory
2. Install dependencies:
   ```bash
   make install
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and updating the values:
   ```bash
   cp .env.example .env
   ```

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

## Configuration

The project uses `pydantic-settings` for configuration management. Set the following environment variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/puzzle_swap

# Waves Blockchain
WAVES_NODE_URL=https://nodes.wx.network/
WAVES_NODE_BACKUP_URL=http://38.242.253.187:6869/

# Puzzle Swap
PUZZLE_TOKEN_ID=HEB8Qaw9xrWpWs8tHsiATYGBWDBtP2S7kcPALrMu43AS
PUZZLE_STAKING_ADDRESS=3PFTbywqxtFfukX3HyT881g4iW5K4QL3FAS

# Logging
LOG_LEVEL=INFO
```

## Usage

### Available Commands

```bash
make help           # Show available commands
make install        # Install dependencies
make build          # Build the project
make test           # Run tests
make lint           # Run linting and type checking
make format         # Format code
make run            # Run the ETL pipeline
make run-download   # Download and process blockchain data
make clean          # Clean build artifacts
```

### Running the ETL Pipeline

1. **Download blockchain data:**
   ```bash
   make run-download
   ```

2. **Run the full ETL pipeline:**
   ```bash
   make run
   ```

3. **Run specific components:**
   ```bash
   poetry run puzzle-etl extract    # Extract data only
   poetry run puzzle-etl transform  # Transform data only
   poetry run puzzle-etl load       # Load data only
   ```

## Database Schema

The project creates the following main tables:

- `transactions` - Raw blockchain transactions
- `swaps` - Processed swap transactions
- `staking_events` - Puzzle token staking events
- `traders` - Trader statistics
- `pair_volumes` - Trading pair volume statistics
- `staking_stats` - Staking statistics

## Development

### Code Quality

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

Run all checks:
```bash
make lint
```

Format code:
```bash
make format
```

### Testing

Run tests:
```bash
make test
```

## Apache Superset Integration

After running the ETL pipeline, connect Apache Superset to your PostgreSQL database to create dashboards and visualizations for the extracted metrics.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License. 