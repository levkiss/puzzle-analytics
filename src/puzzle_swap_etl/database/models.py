"""Database models for the Puzzle Swap ETL pipeline with 3-layer architecture."""

from sqlalchemy.orm import DeclarativeBase

from .models_dm import *  # noqa: F401, F403
from .models_ods import *  # noqa: F401, F403

# Import all models from layer-specific files
from .models_stg import *  # noqa: F401, F403


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass
