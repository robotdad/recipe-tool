"""Event system interfaces."""

from typing import Protocol, runtime_checkable

from recipe_executor.models.events import ExecutionEvent


@runtime_checkable
class EventListener(Protocol):
    """Interface for event listeners."""

    def on_event(self, event: ExecutionEvent) -> None:
        """Called when an event occurs."""
        ...
