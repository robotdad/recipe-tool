import asyncio
import uuid
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# In-memory storage for executions
executions = {}

async def start_execution(recipe_path: str, context_vars: Dict[str, str]) -> str:
    """Start a recipe execution and return the execution ID."""
    execution_id = str(uuid.uuid4())

    # Set up execution tracking
    executions[execution_id] = {
        "status": "pending",
        "logs": [],
        "context": context_vars.copy()
    }

    # Launch in background
    asyncio.create_task(
        run_recipe(execution_id, recipe_path, context_vars)
    )

    return execution_id

async def run_recipe(execution_id: str, recipe_path: str, context_vars: Dict[str, str]) -> None:
    """Run recipe-tool in a subprocess and capture output."""
    executions[execution_id]["status"] = "running"

    # Build command with context variables
    cmd = ["recipe-tool", "--execute", recipe_path]
    for key, value in context_vars.items():
        cmd.append(f"{key}={value}")

    # Run the process and capture output
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Capture stdout
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                log_line = line.decode().strip()
                executions[execution_id]["logs"].append(log_line)
                logger.debug(f"Execution {execution_id}: {log_line}")

        # Wait for completion
        await process.wait()

        if process.returncode == 0:
            executions[execution_id]["status"] = "completed"
            logger.info(f"Execution {execution_id} completed successfully")
        else:
            executions[execution_id]["status"] = "failed"
            logger.error(f"Execution {execution_id} failed with code {process.returncode}")

            # Capture stderr if available
            if process.stderr:
                stderr_data = await process.stderr.read()
                error_message = stderr_data.decode().strip()
                if error_message:
                    executions[execution_id]["logs"].append(f"Error: {error_message}")
                    logger.error(f"Execution {execution_id} error: {error_message}")

    except Exception as e:
        logger.error(f"Error executing recipe: {str(e)}")
        executions[execution_id]["status"] = "failed"
        executions[execution_id]["logs"].append(f"Error: {str(e)}")

def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    """Get execution data by ID."""
    return executions.get(execution_id)

def clean_old_executions(max_age_seconds: int = 3600, max_count: int = 100) -> int:
    """Clean up old execution records to prevent memory leaks.
    Returns the number of records cleaned up.
    """
    # Implementation left as an enhancement
    return 0