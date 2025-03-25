"""Simple progress tracking system."""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("progress")


class ProgressEvent(str, Enum):
    """Types of progress events."""

    RECIPE_START = "recipe_start"
    RECIPE_COMPLETE = "recipe_complete"
    STEP_START = "step_start"
    STEP_COMPLETE = "step_complete"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    LLM_GENERATE = "llm_generate"


# Type for progress callbacks
ProgressCallback = Callable[[ProgressEvent, Dict[str, Any]], None]


class ProgressTracker:
    """Simple progress tracking."""

    def __init__(self):
        """Initialize with no callbacks."""
        self._callbacks: List[ProgressCallback] = []
        self.start_time: Optional[datetime] = None

    def add_callback(self, callback: ProgressCallback) -> None:
        """Add a progress callback."""
        self._callbacks.append(callback)

    def notify(self, event: ProgressEvent, data: Dict[str, Any]) -> None:
        """Notify all callbacks of an event."""
        # Add timestamp to all events
        data["timestamp"] = datetime.now().isoformat()

        # Track start time if this is the recipe start event
        if event == ProgressEvent.RECIPE_START:
            self.start_time = datetime.now()

        # Calculate elapsed time if this isn't the start event
        if self.start_time and event != ProgressEvent.RECIPE_START:
            elapsed = datetime.now() - self.start_time
            data["elapsed_seconds"] = elapsed.total_seconds()

        # Call all registered callbacks
        for callback in self._callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")


def create_console_reporter() -> ProgressCallback:
    """Create a callback that reports progress to the console."""

    def report_progress(event: ProgressEvent, data: Dict[str, Any]) -> None:
        if event == ProgressEvent.RECIPE_START:
            print(f"Starting recipe: {data.get('recipe_name', 'Unnamed')}")
            print(f"Description: {data.get('description', 'No description')}")
            if data.get("step_count"):
                print(f"Total steps: {data.get('step_count')}")

        elif event == ProgressEvent.RECIPE_COMPLETE:
            print(f"\nRecipe completed: {data.get('recipe_name', 'Unnamed')}")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Duration: {data.get('duration_seconds', 0):.2f}s")

        elif event == ProgressEvent.STEP_START:
            step_id = data.get("step_id", "?")
            step_name = data.get("step_name", "Unnamed")
            step_type = data.get("step_type", "Unknown")
            print(f"\nStep {step_id}: {step_name} ({step_type})")

        elif event == ProgressEvent.STEP_COMPLETE:
            duration = data.get("duration_seconds", 0)
            print(f"  ✓ Completed in {duration:.2f}s")

        elif event == ProgressEvent.STEP_FAILED:
            duration = data.get("duration_seconds", 0)
            error = data.get("error", "Unknown error")
            print(f"  ✗ Failed after {duration:.2f}s: {error}")

        elif event == ProgressEvent.STEP_SKIPPED:
            condition = data.get("condition", "condition was false")
            print(f"  ↷ Skipped because {condition}")

        elif event == ProgressEvent.LLM_GENERATE:
            model = data.get("model", "default")
            print(f"  Generating with model: {model}")
            if data.get("prompt_length"):
                print(f"  Prompt length: {data.get('prompt_length')} characters")

    return report_progress


def create_structured_logger() -> ProgressCallback:
    """Create a callback that logs progress events in a structured way."""

    def log_progress(event: ProgressEvent, data: Dict[str, Any]) -> None:
        # Add the event type to the data
        log_data = {"event": event, **data}

        if event == ProgressEvent.RECIPE_START:
            logger.info(f"Recipe started: {data.get('recipe_name')}", extra=log_data)
        elif event == ProgressEvent.RECIPE_COMPLETE:
            logger.info(
                f"Recipe completed: {data.get('recipe_name')} - {data.get('status')}",
                extra=log_data,
            )
        elif event == ProgressEvent.STEP_START:
            logger.info(
                f"Step started: {data.get('step_id')} - {data.get('step_name')}",
                extra=log_data,
            )
        elif event == ProgressEvent.STEP_COMPLETE:
            logger.info(
                f"Step completed: {data.get('step_id')} in {data.get('duration_seconds', 0):.2f}s",
                extra=log_data,
            )
        elif event == ProgressEvent.STEP_FAILED:
            logger.error(
                f"Step failed: {data.get('step_id')} - {data.get('error')}",
                extra=log_data,
            )
        elif event == ProgressEvent.STEP_SKIPPED:
            logger.info(
                f"Step skipped: {data.get('step_id')} - {data.get('condition')}",
                extra=log_data,
            )
        elif event == ProgressEvent.LLM_GENERATE:
            logger.info(
                f"LLM generating: {data.get('model')} for step {data.get('step_id')}",
                extra=log_data,
            )

    return log_progress
