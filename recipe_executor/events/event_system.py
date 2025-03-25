"""Event system interfaces and implementation."""

from typing import List, Protocol, runtime_checkable

from recipe_executor.models.events import ExecutionEvent
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("events")


@runtime_checkable
class EventListener(Protocol):
    """Interface for event listeners."""

    def on_event(self, event: ExecutionEvent) -> None:
        """Called when an event occurs."""
        ...


class EventSystem:
    """Central event system for managing events and listeners."""
    
    def __init__(self):
        """Initialize the event system."""
        self.listeners: List[EventListener] = []
        
    def add_listener(self, listener: EventListener) -> None:
        """
        Add a listener to the event system.
        
        Args:
            listener: Event listener to add
        """
        self.listeners.append(listener)
        
    def remove_listener(self, listener: EventListener) -> None:
        """
        Remove a listener from the event system.
        
        Args:
            listener: Event listener to remove
        """
        if listener in self.listeners:
            self.listeners.remove(listener)
            
    def emit(self, event: ExecutionEvent) -> None:
        """
        Emit an event to all registered listeners.
        
        Args:
            event: Event to emit
        """
        for listener in self.listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
