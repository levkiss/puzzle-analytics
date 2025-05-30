#!/usr/bin/env python3
"""Setup script for Puzzle Swap ETL project."""

import asyncio
import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def check_requirements():
    """Check if all requirements are met."""
    console.print("[bold blue]Checking requirements...[/bold blue]")

    # Check Python version
    if sys.version_info < (3, 9):
        console.print("[red]Error: Python 3.9+ is required[/red]")
        return False

    # Check if Poetry is installed
    if os.system("poetry --version > /dev/null 2>&1") != 0:
        console.print(
            "[red]Error: Poetry is not installed. Please install Poetry first.[/red]"
        )
        console.print("Visit: https://python-poetry.org/docs/#installation")
        return False

    # Check if PostgreSQL is available
    console.print("[green]✓ Python version OK[/green]")
    console.print("[green]✓ Poetry is installed[/green]")

    return True


def setup_environment():
    """Set up the development environment."""
    console.print("[bold blue]Setting up environment...[/bold blue]")

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path("env.example")

    if not env_file.exists() and env_example.exists():
        console.print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        console.print("[green]✓ .env file created[/green]")

    # Create data directories
    data_dirs = ["data/extracted", "data/transformed", "tmp"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    console.print("[green]✓ Data directories created[/green]")


def install_dependencies():
    """Install project dependencies."""
    console.print("[bold blue]Installing dependencies...[/bold blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Installing dependencies...", total=None)

        # Install dependencies
        result = os.system("poetry install")
        if result != 0:
            console.print("[red]Error: Failed to install dependencies[/red]")
            return False

        progress.update(task, description="[green]Dependencies installed successfully!")

    return True


async def setup_database():
    """Set up the database schema."""
    console.print("[bold blue]Setting up database...[/bold blue]")

    try:
        # Import after dependencies are installed
        from puzzle_swap_etl.database import Base, db_manager

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating database schema...", total=None)

            # Create all tables
            async with db_manager.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            progress.update(
                task, description="[green]Database schema created successfully!"
            )

        return True

    except Exception as e:
        console.print(f"[red]Error setting up database: {e}[/red]")
        console.print(
            "[yellow]You can set up the database later using: poetry run puzzle-etl init-db[/yellow]"
        )
        return False


def main():
    """Main setup function."""
    console.print(
        Panel.fit(
            "[bold green]Puzzle Swap ETL Setup[/bold green]\n"
            "This script will set up your development environment.",
            title="Welcome",
            border_style="green",
        )
    )

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Set up environment
    setup_environment()

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Set up database (optional)
    console.print("\n[bold yellow]Database Setup[/bold yellow]")
    setup_db = typer.confirm("Do you want to set up the database now?")

    if setup_db:
        try:
            asyncio.run(setup_database())
        except Exception as e:
            console.print(f"[red]Database setup failed: {e}[/red]")
            console.print(
                "[yellow]You can set up the database later using: poetry run puzzle-etl init-db[/yellow]"
            )

    # Success message
    console.print(
        Panel.fit(
            "[bold green]Setup Complete![/bold green]\n\n"
            "Next steps:\n"
            "1. Update your .env file with your database credentials\n"
            "2. Run: poetry run puzzle-etl init-db (if not done above)\n"
            "3. Run: poetry run puzzle-etl download\n"
            "4. Run: poetry run puzzle-etl run\n\n"
            "For help: poetry run puzzle-etl --help",
            title="Success",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
