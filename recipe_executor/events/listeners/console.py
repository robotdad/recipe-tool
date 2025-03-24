"""Console event listener implementation."""

import json
import logging
from typing import cast

from recipe_executor.models.events import (
    ExecutionEvent,
    LLMGenerationEvent,
    RecipeCompleteEvent,
    RecipeStartEvent,
    StepCompleteEvent,
    StepFailedEvent,
    StepStartEvent,
    UserInteractionEvent,
    ValidationEvent,
)
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("events")


class ConsoleEventListener:
    """Event listener that prints events to the console."""

    def on_event(self, event: ExecutionEvent) -> None:
        """Print the event to the console and log details at debug level."""
        # Log full event details at debug level
        debug_logger = log_utils.get_logger("debug")
        debug_logger.debug(f"EVENT: {event.event_type} - {json.dumps(event.model_dump(), default=str)}")
        
        if event.event_type == "step_start":
            event = cast(StepStartEvent, event)
            logger.info(
                f"Starting step: {event.step_id} ({event.step_name or event.step_type})"
            )
        elif event.event_type == "step_complete":
            event = cast(StepCompleteEvent, event)
            logger.info(
                f"Completed step: {event.step_id} ({event.status}) in {event.duration_seconds:.2f}s"
            )
        elif event.event_type == "step_failed":
            event = cast(StepFailedEvent, event)
            logger.error(f"Failed step: {event.step_id} - {event.error}")
            # Log traceback at debug level if available
            if event.traceback:
                debug_logger.debug(f"Step {event.step_id} traceback:\n{event.traceback}")
        elif event.event_type == "validation":
            event = cast(ValidationEvent, event)
            if event.valid:
                logger.info(f"Validation passed with {event.issues_count} issues")
            else:
                logger.warning(f"Validation failed with {event.issues_count} issues")
        elif event.event_type == "llm_generation":
            event = cast(LLMGenerationEvent, event)
            logger.info(
                f"LLM generation with model {event.model} (prompt length: {event.prompt_length})"
            )
        elif event.event_type == "user_interaction":
            event = cast(UserInteractionEvent, event)
            logger.info(f"User interaction required: {event.prompt}")
        elif event.event_type == "recipe_start":
            event = cast(RecipeStartEvent, event)
            logger.info(f"Starting recipe: {event.recipe_name}")
        elif event.event_type == "recipe_complete":
            event = cast(RecipeCompleteEvent, event)
            logger.info(
                f"Completed recipe: {event.recipe_name} ({event.status}) in {event.duration_seconds:.2f}s"
            )
