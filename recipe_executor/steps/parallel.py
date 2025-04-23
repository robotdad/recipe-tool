import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.protocols import ContextProtocol, StepProtocol


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each a dict with 'type' and 'config'.
        max_concurrency: Maximum number of substeps to run concurrently. 0 means unlimited.
        delay: Optional delay (in seconds) between launching each substep.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        total = len(self.config.substeps)
        self.logger.info(
            f"Starting ParallelStep: {total} substeps, "
            f"max_concurrency={self.config.max_concurrency}, delay={self.config.delay}"
        )

        if total == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit
        concurrency = (
            self.config.max_concurrency if self.config.max_concurrency > 0 else total
        )
        semaphore = asyncio.Semaphore(concurrency)

        # Holder for first failure
        failure_holder: Dict[str, Optional[Exception]] = {"exc": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            # Substep isolation and execution
            sub_logger = self.logger.getChild(f"substep_{idx}")
            try:
                sub_logger.debug(
                    f"Cloning context and preparing substep {idx} ({spec.get('type')})"
                )
                sub_context = context.clone()

                step_type = spec.get("type")
                step_cfg = spec.get("config", {})
                if not step_type or step_type not in STEP_REGISTRY:
                    raise RuntimeError(
                        f"Unknown or missing step type '{step_type}' for substep {idx}"
                    )
                StepClass = STEP_REGISTRY[step_type]
                step_instance: StepProtocol = StepClass(sub_logger, step_cfg)

                sub_logger.info(f"Launching substep {idx} of type '{step_type}'")
                # Execute substep
                await step_instance.execute(sub_context)
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as e:
                # Record first exception and log
                if failure_holder["exc"] is None:
                    failure_holder["exc"] = e
                sub_logger.error(
                    f"Substep {idx} failed: {e}", exc_info=True
                )
                # Propagate to allow gather to detect
                raise

            finally:
                # Release the semaphore slot
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(self.config.substeps):
            # Fail-fast: stop launching if error recorded
            if failure_holder["exc"]:
                self.logger.debug(
                    f"Fail-fast: aborting launch of remaining substeps at index {idx}"
                )
                break

            await semaphore.acquire()
            # Staggered launch
            if self.config.delay > 0:
                await asyncio.sleep(self.config.delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        # Await completion or first failure
        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for tasks, fail fast on exception
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_EXCEPTION
        )

        # If any task raised, cancel pending and re-raise
        if failure_holder["exc"]:
            self.logger.error(
                "A substep failed; cancelling remaining tasks and aborting ParallelStep"
            )
            for p in pending:
                p.cancel()
            # Wait for cancellation to finish
            await asyncio.gather(*pending, return_exceptions=True)
            # Shutdown complete; propagate error
            raise RuntimeError(
                "ParallelStep aborted due to substep failure"
            ) from failure_holder["exc"]

        # All succeeded; gather results
        await asyncio.gather(*done)
        success_count = len(done)
        self.logger.info(
            f"Completed ParallelStep: {success_count}/{total} substeps succeeded"
        )
