"""Configuration for the documentation server."""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DocsServerSettings(BaseSettings):
    """Settings for the documentation server."""

    model_config = SettingsConfigDict(
        env_prefix="DOCS_SERVER_",
        env_file=".env",
        extra="ignore",
    )

    # Paths to documentation files
    doc_paths: List[Path] = Field(
        default_factory=lambda: [Path(".")],
        description="List of paths to documentation files or directories",
    )

    # File patterns to include
    include_patterns: List[str] = Field(
        default_factory=lambda: ["*.md", "*.txt", "*.rst"],
        description="File patterns to include when scanning directories",
    )

    # File patterns to exclude
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [".*", "__pycache__", "*.pyc"],
        description="File patterns to exclude when scanning directories",
    )

    # Maximum file size to process (in bytes)
    max_file_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum file size to process in bytes",
    )

    # Server settings
    host: str = Field(
        default="localhost",
        description="Host for SSE server",
    )

    port: int = Field(
        default=3003,
        description="Port for SSE server",
    )

    # Cache settings
    enable_cache: bool = Field(
        default=True,
        description="Enable caching of documentation content",
    )

    cache_ttl: int = Field(
        default=300,  # 5 minutes
        description="Cache time-to-live in seconds",
    )
