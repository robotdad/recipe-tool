import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from pydantic import BaseModel

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig, BaseModel):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel. Each substep must be defined as an execute_recipe step.
        max_concurrency: Maximum number of substeps to run concurrently. Default of 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep. Default is 0.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """ParallelStep executes multiple sub-recipes concurrently in isolated contexts.

    It clones the current context for each substep, launches them in a ThreadPoolExecutor, and enforces fail-fast behavior.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        # Initialize configuration via Pydantic validation
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info("Starting ParallelStep execution with {} substeps.".format(len(self.config.substeps)))

        substeps = self.config.substeps
        total_substeps = len(substeps)

        # Determine max_workers: if max_concurrency is set (>0), use it, otherwise allow all substeps concurrently.
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else total_substeps
        futures: Dict[Future, int] = {}
        exception_occurred = False
        first_exception = None
        failed_index = None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit substeps one by one, obeying delay and fail-fast policy
            for index, substep_config in enumerate(substeps):
                if exception_occurred:
                    self.logger.info(f"Aborting submission of substep {index} due to a previous error.")
                    break

                # Clone the context for isolation
                cloned_context = context.clone()

                # Resolve and instantiate the sub-step from the registry
                step_type = substep_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep at index {index} has unregistered type: {step_type}")

                step_cls = STEP_REGISTRY[step_type]
                try:
                    step_instance = step_cls(substep_config, self.logger)
                except Exception as e:
                    self.logger.error(f"Failed to instantiate substep at index {index}: {e}")
                    raise

                self.logger.info(f"Submitting substep {index} of type '{step_type}'.")
                future = executor.submit(step_instance.execute, cloned_context)
                futures[future] = index

                # If a delay is configured, wait before launching the next one
                if self.config.delay > 0 and index < total_substeps - 1:
                    time.sleep(self.config.delay)

            # Process futures as they complete
            try:
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        future.result()
                        self.logger.info(f"Substep {index} completed successfully.")
                    except Exception as e:
                        self.logger.error(f"Substep {index} failed with error: {e}")
                        exception_occurred = True
                        first_exception = e
                        failed_index = index
                        # Fail fast: attempt to cancel any futures that haven't started
                        for pending_future in futures:
                            if not pending_future.done():
                                pending_future.cancel()
                        # Break out of the loop as soon as one error is encountered
                        break
            except Exception as overall_exception:
                # If there was an exception while collecting results
                self.logger.error(f"Exception during parallel execution: {overall_exception}")
                raise overall_exception

        if exception_occurred:
            raise RuntimeError(f"ParallelStep aborted because substep {failed_index} failed: {first_exception}")

        self.logger.info("All parallel substeps completed successfully.")
