import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each with 'type' and 'config'.
        max_concurrency: Maximum concurrent substeps. 0 means no limit.
        delay: Delay in seconds between launching substeps.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        total = len(self.config.substeps)
        self.logger.info("Starting parallel execution: %d substeps", total)

        semaphore: Optional[asyncio.Semaphore]
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)
        else:
            semaphore = None

        error_occurred = False
        first_exception: Optional[BaseException] = None

        async def run_substep(idx: int, substep_def: Dict[str, Any]) -> None:
            nonlocal error_occurred, first_exception
            if error_occurred:
                return

            if semaphore:
                await semaphore.acquire()

            try:
                # Clone context for isolation
                sub_context = context.clone()

                raw_step_type = substep_def.get("type")
                if not isinstance(raw_step_type, str):
                    raise ValueError(f"Invalid substep type: {raw_step_type}")
                step_type = raw_step_type
                step_conf = substep_def.get("config", {})
                step_cls = STEP_REGISTRY.get(step_type)
                if step_cls is None:
                    raise ValueError(f"Unknown substep type: {step_type}")

                sub_logger = self.logger.getChild(f"{step_type}[{idx}]")
                self.logger.debug("Launching substep %d of type %s", idx, step_type)
                step_instance = step_cls(sub_logger, step_conf)

                # Execute the substep (async or sync)
                await step_instance.execute(sub_context)

                self.logger.debug("Completed substep %d", idx)

            except Exception as exc:
                self.logger.error("Substep %d failed: %s", idx, str(exc), exc_info=True)
                if not error_occurred:
                    error_occurred = True
                    first_exception = exc
                raise

            finally:
                if semaphore:
                    semaphore.release()

        # Schedule tasks with optional delay
        tasks: List[asyncio.Task] = []
        for idx, sub_def in enumerate(self.config.substeps):
            if error_occurred:
                break
            task = asyncio.create_task(run_substep(idx, sub_def))
            tasks.append(task)
            if self.config.delay and idx < total - 1:
                await asyncio.sleep(self.config.delay)

        if not tasks:
            self.logger.info("No substeps to run.")
            return

        # Wait for tasks, fail-fast on first exception
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        # Check for exceptions in done
        for t in done:
            if t.cancelled():
                continue
            if t.exception():
                error_occurred = True
                if first_exception is None:
                    first_exception = t.exception()

        # Cancel any pending tasks
        if pending:
            for t in pending:
                t.cancel()
            # Allow cancelled tasks to finish
            await asyncio.gather(*pending, return_exceptions=True)

        if error_occurred and first_exception:
            # Propagate first exception
            raise first_exception

        self.logger.info("Parallel execution complete: %d/%d substeps succeeded", total, total)
