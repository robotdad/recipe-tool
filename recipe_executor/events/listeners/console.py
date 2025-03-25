"""Console event listener implementation."""

import json
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
        
        # Handle each event type with proper type checking
        if event.event_type == "step_start":
            step_event = cast(StepStartEvent, event)
            logger.info(f"Starting step: {step_event.step_id} ({step_event.step_name or step_event.step_type})")
        
        elif event.event_type == "step_complete":
            complete_event = cast(StepCompleteEvent, event)
            logger.info(f"Completed step: {complete_event.step_id} ({complete_event.status}) in {complete_event.duration_seconds:.2f}s")
        
        elif event.event_type == "step_failed":
            failed_event = cast(StepFailedEvent, event)
            logger.error(f"Failed step: {failed_event.step_id} - {failed_event.error}")
            if failed_event.traceback:
                debug_logger.debug(f"Step {failed_event.step_id} traceback:\n{failed_event.traceback}")
        
        elif event.event_type == "validation":
            valid_event = cast(ValidationEvent, event)
            if valid_event.valid:
                logger.info(f"Validation passed with {valid_event.issues_count} issues")
            else:
                logger.warning(f"Validation failed with {valid_event.issues_count} issues")
        
        elif event.event_type == "llm_generation":
            llm_event = cast(LLMGenerationEvent, event)
            logger.info(f"LLM generation with model {llm_event.model} (prompt length: {llm_event.prompt_length})")
        
        elif event.event_type == "user_interaction":
            user_event = cast(UserInteractionEvent, event)
            logger.info(f"User interaction required: {user_event.prompt}")
        
        elif event.event_type == "recipe_start":
            start_event = cast(RecipeStartEvent, event)
            logger.info(f"Starting recipe: {start_event.recipe_name}")
        
        elif event.event_type == "recipe_complete":
            recipe_complete_event = cast(RecipeCompleteEvent, event)
            logger.info(f"Completed recipe: {recipe_complete_event.recipe_name} ({recipe_complete_event.status}) in {recipe_complete_event.duration_seconds:.2f}s")
