"""Parallel execution configuration model."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParallelConfig(BaseModel):
    """Configuration for parallel execution."""

    steps: List[Dict[str, Any]] = Field(
        description="List of steps to execute in parallel"
    )
    output_variable: Optional[str] = Field(
        description="Name of the variable to store all results in", default=None
    )
    max_workers: Optional[int] = Field(
        description="Maximum number of worker threads", default=None
    )
    timeout: Optional[int] = Field(
        description="Timeout in seconds for all parallel steps", default=None
    )
