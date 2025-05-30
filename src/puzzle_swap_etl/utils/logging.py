"""Logging utilities for the Puzzle Swap ETL pipeline."""

import logging
import sys
from typing import Any, Dict

import structlog
from rich.console import Console
from rich.logging import RichHandler

from puzzle_swap_etl.config import settings


def setup_logging() -> None:
    """Set up structured logging for the application."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            (
                structlog.processors.JSONRenderer()
                if settings.log_format == "json"
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
        handlers=(
            [
                RichHandler(
                    console=Console(stderr=True),
                    show_time=False,
                    show_path=False,
                    markup=True,
                )
            ]
            if settings.log_format == "text"
            else []
        ),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)

    def log_operation(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Log an operation with context.

        Args:
            operation: Operation name
            **kwargs: Additional context

        Returns:
            Context dictionary for further logging
        """
        context = {"operation": operation, **kwargs}
        self.logger.info("Starting operation", **context)
        return context

    def log_success(self, context: Dict[str, Any], **kwargs: Any) -> None:
        """Log successful operation completion.

        Args:
            context: Operation context
            **kwargs: Additional context
        """
        self.logger.info("Operation completed successfully", **context, **kwargs)

    def log_error(
        self, context: Dict[str, Any], error: Exception, **kwargs: Any
    ) -> None:
        """Log operation error.

        Args:
            context: Operation context
            error: Exception that occurred
            **kwargs: Additional context
        """
        self.logger.error(
            "Operation failed",
            **context,
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )
