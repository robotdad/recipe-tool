import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0


class ParallelStep(BaseStep[ParallelConfig]):
    """ParallelStep executes multiple sub-recipes concurrently in isolated contexts.

    It uses a ThreadPoolExecutor to run substeps in parallel with optional concurrency limits
    and launch delays. Implements fail-fast behavior: if any substep fails, execution aborts
    and propagates the first encountered exception.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize the base step with ParallelConfig
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """Execute the parallel step: launch substeps concurrently and wait for completion.

        Args:
            context (Context): The execution context.

        Raises:
            Exception: Propagates the first encountered exception from any substep.
        """
        total_substeps = len(self.config.substeps)
        self.logger.info(f"ParallelStep starting with {total_substeps} substep(s).")

        # Determine max_workers: if max_concurrency is 0 or greater than total, use total_substeps
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else total_substeps

        futures = []
        first_exception: Optional[Exception] = None
        executor = ThreadPoolExecutor(max_workers=max_workers)

        try:
            # Submit tasks sequentially and respect delay between launches
            for index, sub_config in enumerate(self.config.substeps):
                # Fail-fast: if an error was encountered, stop launching new substeps
                if first_exception is not None:
                    self.logger.error("Aborting submission of further substeps due to previous error.")
                    break

                # Each substep gets its own cloned context
                sub_context = context.clone()
                
                # Validate that sub_config contains a recognized step type
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    err_msg = f"Unrecognized step type '{step_type}' in substep at index {index}."
                    self.logger.error(err_msg)
                    raise ValueError(err_msg)

                # Instantiate the substep from the registry
                step_class = STEP_REGISTRY[step_type]
                substep_instance = step_class(sub_config, logger=self.logger)

                self.logger.info(f"Launching substep {index} (type: {step_type}).")

                # Submit the substep execution as a separate task
                future = executor.submit(self._execute_substep, substep_instance, sub_context, index)
                futures.append(future)

                # If a delay is configured and this is not the last substep, wait
                if self.config.delay > 0 and index < total_substeps - 1:
                    time.sleep(self.config.delay)

            # Wait for all submitted tasks to complete
            for future in as_completed(futures):
                try:
                    # Will raise exception if substep failed
                    future.result()
                except Exception as exc:
                    self.logger.error(f"A substep failed with error: {exc}", exc_info=True)
                    first_exception = exc
                    # Fail-fast: break out as soon as an error is detected
                    break

            # If an exception was encountered, attempt to cancel remaining tasks
            if first_exception is not None:
                self.logger.error("Fail-fast activated. Cancelling pending substeps.")
                for fut in futures:
                    fut.cancel()
                raise first_exception

            self.logger.info("ParallelStep completed all substeps successfully.")

        finally:
            executor.shutdown(wait=True)

    def _execute_substep(self, step_instance: BaseStep, context: Context, index: int) -> None:
        """Execute an individual substep with its cloned context.

        Args:
            step_instance (BaseStep): The substep instance to execute.
            context (Context): The cloned context for this substep.
            index (int): Index of the substep, for logging purposes.

        Raises:
            Exception: Propagates any exception encountered during execution of the substep.
        """
        self.logger.info(f"Substep {index} started.")
        try:
            step_instance.execute(context)
            self.logger.info(f"Substep {index} completed successfully.")
        except Exception as e:
            self.logger.error(f"Substep {index} failed with error: {e}", exc_info=True)
            raise e
