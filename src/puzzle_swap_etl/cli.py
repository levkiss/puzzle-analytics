"""Command-line interface for the Puzzle Swap ETL pipeline."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from puzzle_swap_etl.config import settings
from puzzle_swap_etl.database import db_manager
from puzzle_swap_etl.pipeline import PuzzleSwapETL

# Initialize Rich console
console = Console()

# Create Typer app
app = typer.Typer(
    name="puzzle-etl",
    help="Puzzle Swap ETL - Blockchain data extraction and analysis pipeline",
)


@app.command()
def run(
    full: bool = typer.Option(False, "--full", help="Run full ETL pipeline"),
    extract_only: bool = typer.Option(
        False, "--extract-only", help="Extract data only"
    ),
    transform_only: bool = typer.Option(
        False, "--transform-only", help="Transform data only"
    ),
    load_only: bool = typer.Option(False, "--load-only", help="Load data only"),
    addresses: Optional[str] = typer.Option(
        None, help="Comma-separated list of addresses to process"
    ),
) -> None:
    """Run the ETL pipeline."""
    address_list = None
    if addresses:
        address_list = [addr.strip() for addr in addresses.split(",")]

    if full:
        asyncio.run(run_full_pipeline(address_list))
    elif extract_only:
        asyncio.run(run_extraction())
    elif transform_only:
        asyncio.run(run_transformation())
    elif load_only:
        asyncio.run(run_loading())
    else:
        console.print(
            "[yellow]Please specify a mode: --full, --extract-only, --transform-only, or --load-only"
        )
        raise typer.Exit(1)


@app.command()
def download(
    address: Optional[str] = typer.Option(None, help="Specific address to download"),
    limit: int = typer.Option(10000, help="Maximum transactions to download"),
) -> None:
    """Download blockchain data."""
    asyncio.run(download_blockchain_data(address, limit))


@app.command()
def extract(
    output_dir: str = typer.Option(
        "data/extracted", help="Output directory for extracted data"
    ),
) -> None:
    """Extract data from blockchain."""
    asyncio.run(run_extraction(output_dir))


@app.command()
def transform(
    input_dir: str = typer.Option(
        "data/extracted", help="Input directory with extracted data"
    ),
    output_dir: str = typer.Option(
        "data/transformed", help="Output directory for transformed data"
    ),
) -> None:
    """Transform extracted data."""
    asyncio.run(run_transformation(input_dir, output_dir))


@app.command()
def load(
    input_dir: str = typer.Option(
        "data/transformed", help="Input directory with transformed data"
    ),
) -> None:
    """Load transformed data to database."""
    asyncio.run(run_loading(input_dir))


# Database management commands
@app.command()
def init_db() -> None:
    """Initialize database with schemas and tables."""
    asyncio.run(initialize_database())


@app.command()
def check_db() -> None:
    """Check database connection and show table counts."""
    asyncio.run(check_database())


@app.command()
def drop_db() -> None:
    """Drop all database tables (use with caution!)."""
    confirm = typer.confirm("Are you sure you want to drop all database tables?")
    if confirm:
        asyncio.run(drop_database())
    else:
        console.print("[yellow]Operation cancelled.")


@app.command()
def status() -> None:
    """Show ETL pipeline status and statistics."""
    asyncio.run(show_status())


async def run_full_pipeline(addresses: Optional[list] = None) -> None:
    """Run the complete ETL pipeline."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running ETL pipeline...", total=None)

        async with PuzzleSwapETL() as etl:
            summary = await etl.run_pipeline(addresses=addresses)

            # Display summary
            console.print("\n[bold green]Pipeline Summary:[/bold green]")
            console.print(f"Addresses processed: {summary['addresses_processed']}")
            console.print(
                f"Transactions extracted: {summary['transactions_extracted']}"
            )
            console.print(f"Swaps processed: {summary['swaps_processed']}")
            console.print(
                f"Staking events processed: {summary['staking_events_processed']}"
            )
            console.print(f"Duration: {summary['duration']:.2f} seconds")

            if summary["errors"]:
                console.print(
                    f"\n[red]Errors encountered: {len(summary['errors'])}[/red]"
                )
                for error in summary["errors"]:
                    console.print(f"  - {error}")

        progress.update(
            task, description="[bold green]Pipeline completed successfully!"
        )


async def run_extraction(output_dir: str = "data/extracted") -> None:
    """Run extraction phase."""
    from puzzle_swap_etl.extractors import BlockchainExtractor

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting blockchain data...", total=None)

        async with BlockchainExtractor() as extractor:
            # Extract from main addresses
            from puzzle_swap_etl.mappings import ALL_IMPORTANT_ADDRESSES

            addresses = ALL_IMPORTANT_ADDRESSES[:5]  # Limit for testing

            for address in addresses:
                progress.update(task, description=f"Extracting from {address}...")
                transactions, file_count = await extractor.fetch_all_transactions(
                    address
                )

                # Save extracted data
                import json

                import aiofiles

                filename = f"{output_dir}/{address}_transactions.json"
                async with aiofiles.open(filename, "w") as f:
                    await f.write(json.dumps(transactions, default=str))

                console.print(f"Saved {len(transactions)} transactions to {filename}")

        progress.update(task, description="[bold green]Extraction completed!")


async def run_transformation(
    input_dir: str = "data/extracted", output_dir: str = "data/transformed"
) -> None:
    """Run transformation phase."""
    from puzzle_swap_etl.transformers import StakingTransformer, SwapTransformer

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Transforming data...", total=None)

        swap_transformer = SwapTransformer()
        staking_transformer = StakingTransformer()

        # Process extracted files
        import json
        from pathlib import Path

        import aiofiles

        input_path = Path(input_dir)
        for file_path in input_path.glob("*_transactions.json"):
            progress.update(task, description=f"Processing {file_path.name}...")

            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                transactions = json.loads(content)

            # Transform swaps
            swaps = swap_transformer.transform_transactions(transactions)
            if swaps:
                swap_file = f"{output_dir}/{file_path.stem}_swaps.json"
                async with aiofiles.open(swap_file, "w") as f:
                    await f.write(
                        json.dumps([swap.dict() for swap in swaps], default=str)
                    )
                console.print(f"Saved {len(swaps)} swaps to {swap_file}")

            # Transform staking events
            events = staking_transformer.transform_transactions(transactions)
            if events:
                events_file = f"{output_dir}/{file_path.stem}_staking.json"
                async with aiofiles.open(events_file, "w") as f:
                    await f.write(
                        json.dumps([event.dict() for event in events], default=str)
                    )
                console.print(f"Saved {len(events)} staking events to {events_file}")

        progress.update(task, description="[bold green]Transformation completed!")


async def run_loading(input_dir: str = "data/transformed") -> None:
    """Run loading phase."""
    from puzzle_swap_etl.loaders.database import DatabaseLoader

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading data to database...", total=None)

        loader = DatabaseLoader()

        # Process transformed files
        import json
        from pathlib import Path

        import aiofiles

        input_path = Path(input_dir)

        # Load swaps
        for file_path in input_path.glob("*_swaps.json"):
            progress.update(task, description=f"Loading {file_path.name}...")

            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                swaps_data = json.loads(content)

            # Convert to SwapData objects
            from puzzle_swap_etl.models import SwapData

            swaps = [SwapData(**swap) for swap in swaps_data]

            await loader.save_swaps(swaps)
            console.print(f"Loaded {len(swaps)} swaps from {file_path.name}")

        # Load staking events
        for file_path in input_path.glob("*_staking.json"):
            progress.update(task, description=f"Loading {file_path.name}...")

            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                events_data = json.loads(content)

            # Convert to StakingEventData objects
            from puzzle_swap_etl.models import StakingEventData

            events = [StakingEventData(**event) for event in events_data]

            await loader.save_staking_events(events)
            console.print(f"Loaded {len(events)} staking events from {file_path.name}")

        progress.update(task, description="[bold green]Loading completed!")


async def download_blockchain_data(address: Optional[str], limit: int) -> None:
    """Download blockchain data for analysis."""
    from puzzle_swap_etl.extractors import BlockchainExtractor

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading blockchain data...", total=None)

        async with BlockchainExtractor() as extractor:
            if address:
                addresses = [address]
            else:
                # Use default important addresses
                from puzzle_swap_etl.mappings import STAKING_ADDRESSES

                addresses = STAKING_ADDRESSES[:3]  # Limit for testing

            for addr in addresses:
                progress.update(task, description=f"Downloading from {addr}...")
                transactions, file_count = await extractor.fetch_all_transactions(addr)
                console.print(
                    f"Downloaded {len(transactions)} transactions from {addr}"
                )

        progress.update(task, description="[bold green]Download completed!")


async def initialize_database() -> None:
    """Initialize database with schemas and tables."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing database...", total=None)

        try:
            # Check connection first
            if not await db_manager.check_connection():
                console.print("[red]Failed to connect to database!")
                raise typer.Exit(1)

            # Create schemas and tables
            await db_manager.create_tables()

            progress.update(
                task, description="[bold green]Database initialized successfully!"
            )
            console.print(
                "\n[green]Database schemas and tables created successfully![/green]"
            )
            console.print("Schemas created: stg, ods, dm")

        except Exception as e:
            console.print(f"[red]Failed to initialize database: {str(e)}[/red]")
            raise typer.Exit(1)


async def check_database() -> None:
    """Check database connection and show table counts."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking database...", total=None)

        try:
            # Check connection
            if not await db_manager.check_connection():
                console.print("[red]Failed to connect to database!")
                raise typer.Exit(1)

            # Get table counts
            counts = await db_manager.get_table_counts()

            progress.update(task, description="[bold green]Database check completed!")

            # Display results in a table
            table = Table(title="Database Table Counts")
            table.add_column("Schema.Table", style="cyan")
            table.add_column("Row Count", style="magenta")

            for table_name, count in counts.items():
                table.add_row(table_name, str(count))

            console.print(table)

        except Exception as e:
            console.print(f"[red]Database check failed: {str(e)}[/red]")
            raise typer.Exit(1)


async def drop_database() -> None:
    """Drop all database tables."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Dropping database tables...", total=None)

        try:
            await db_manager.drop_tables()

            progress.update(task, description="[bold green]Database tables dropped!")
            console.print("\n[yellow]All database tables have been dropped.[/yellow]")

        except Exception as e:
            console.print(f"[red]Failed to drop database tables: {str(e)}[/red]")
            raise typer.Exit(1)


async def show_status() -> None:
    """Show ETL pipeline status and statistics."""
    try:
        # Check database connection
        if not await db_manager.check_connection():
            console.print("[red]Database connection failed![/red]")
            return

        # Get table counts
        counts = await db_manager.get_table_counts()

        # Create status table
        table = Table(title="Puzzle Swap ETL Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")

        # Database status
        table.add_row(
            "Database",
            "✓ Connected",
            f"PostgreSQL at {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'localhost'}",
        )

        # Schema status
        stg_tables = sum(
            1 for k in counts.keys() if k.startswith("stg.") and counts[k] != "Error"
        )
        ods_tables = sum(
            1 for k in counts.keys() if k.startswith("ods.") and counts[k] != "Error"
        )
        dm_tables = sum(
            1 for k in counts.keys() if k.startswith("dm.") and counts[k] != "Error"
        )

        table.add_row(
            "STG Schema",
            "✓ Ready" if stg_tables > 0 else "⚠ Empty",
            f"{stg_tables} tables",
        )
        table.add_row(
            "ODS Schema",
            "✓ Ready" if ods_tables > 0 else "⚠ Empty",
            f"{ods_tables} tables",
        )
        table.add_row(
            "DM Schema",
            "✓ Ready" if dm_tables > 0 else "⚠ Empty",
            f"{dm_tables} tables (reserved for future use)",
        )

        # Data status
        total_transactions = counts.get("stg.transactions", 0)
        total_swaps = counts.get("ods.swaps", 0)
        total_staking = counts.get("ods.staking_events", 0)

        if isinstance(total_transactions, int) and total_transactions > 0:
            table.add_row(
                "Data Status",
                "✓ Has Data",
                f"{total_transactions} transactions, {total_swaps} swaps, {total_staking} staking events",
            )
        else:
            table.add_row(
                "Data Status", "⚠ No Data", "Run ETL pipeline to populate data"
            )

        console.print(table)

        # Configuration info
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"Puzzle Staking Address: {settings.puzzle_staking_address}")
        console.print(f"Waves Node URLs: {', '.join(settings.waves_node_urls)}")
        console.print("Debug Mode: " + ("Enabled" if settings.debug else "Disabled"))

    except Exception as e:
        console.print(f"[red]Failed to get status: {str(e)}[/red]")


if __name__ == "__main__":
    app()
