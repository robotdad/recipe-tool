from fastapi import APIRouter, BackgroundTasks, HTTPException
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging

from app.models.schema import ExecutionRequest, ExecutionResponse
from app.core.execution import start_execution, get_execution

router = APIRouter(tags=["executions"])
logger = logging.getLogger(__name__)

@router.post("/api/recipes/execute", response_model=ExecutionResponse)
async def execute_recipe(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a recipe with the given context variables."""
    logger.info(f"Executing recipe: {request.recipe_path}")
    execution_id = await start_execution(request.recipe_path, request.context_vars)
    return {"execution_id": execution_id}

@router.get("/api/execution/{execution_id}/stream")
async def stream_execution(execution_id: str):
    """Stream execution updates via SSE."""
    logger.debug(f"Setting up SSE stream for execution: {execution_id}")
    execution = get_execution(execution_id)
    if not execution:
        logger.warning(f"Execution not found: {execution_id}")
        raise HTTPException(status_code=404, detail="Execution not found")

    async def event_generator():
        last_log_count = 0
        final_check_count = 0
        max_final_checks = 5  # Number of additional checks after completion

        while True:
            # Get current status and logs
            current_status = execution["status"]
            current_logs = execution["logs"]

            # Send new logs if any
            if len(current_logs) > last_log_count:
                new_logs = current_logs[last_log_count:]
                last_log_count = len(current_logs)
                yield {
                    "event": "log",
                    "data": json.dumps(new_logs)
                }
                logger.debug(f"Sent {len(new_logs)} new log entries")

            # Send status update
            yield {
                "event": "status",
                "data": current_status
            }

            # If execution is done, make a few more checks for logs before closing
            if current_status in ["completed", "failed"]:
                final_check_count += 1
                if final_check_count >= max_final_checks:
                    logger.debug(f"Execution {execution_id} complete, closing stream after {final_check_count} final checks")
                    break

                # Use a shorter delay for final checks
                await asyncio.sleep(0.2)
            else:
                # Normal polling during execution
                await asyncio.sleep(0.5)

        # One last check for any final logs
        current_logs = execution["logs"]
        if len(current_logs) > last_log_count:
            final_logs = current_logs[last_log_count:]
            yield {
                "event": "log",
                "data": json.dumps(final_logs)
            }
            logger.debug(f"Sent {len(final_logs)} final log entries before closing")

    return EventSourceResponse(event_generator())