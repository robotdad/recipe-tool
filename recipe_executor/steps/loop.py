import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.
    """
    items: Union[str, List[Any], Dict[Any, Any]]
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, execute substeps for each item.
    """
    def __init__(
        self, logger: logging.Logger, config: Dict[str, Any]
    ) -> None:
        # Validate configuration via Pydantic
        validated = LoopStepConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        # dynamic import to avoid circular dependencies
        from recipe_executor.executor import Executor  # type: ignore

        # Resolve items definition (could be path or direct list/dict)
        items_def: Union[str, List[Any], Dict[Any, Any]] = self.config.items
        if isinstance(items_def, str):
            # Render template to get path
            rendered_path: str = render_template(items_def, context)
            items_obj: Any = _resolve_path(rendered_path, context)
        else:
            # Direct list or dict provided
            items_obj = items_def  # type: ignore

        # Validate items_obj
        if items_obj is None:
            raise ValueError(
                f"LoopStep: Items collection '{items_def}' not found in context."
            )
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(
                f"LoopStep: Items collection must be a list or dict, got {type(items_obj).__name__}."
            )

        # Build list of (key/index, value)
        items_list: List[Tuple[Any, Any]] = []
        if isinstance(items_obj, list):
            for idx, value in enumerate(items_obj):
                items_list.append((idx, value))
        else:
            for key, value in items_obj.items():
                items_list.append((key, value))
        total_items: int = len(items_list)

        self.logger.info(
            f"LoopStep: Processing {total_items} items with max_concurrency={self.config.max_concurrency}."
        )

        # Handle empty collection
        if total_items == 0:
            # Preserve type (list or dict)
            empty_result: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = empty_result
            self.logger.info("LoopStep: No items to process.")
            return

        # Prepare result and error containers
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = (
            [] if isinstance(items_obj, list) else {}
        )

        # Concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        max_c = self.config.max_concurrency
        if max_c and max_c > 0:
            semaphore = asyncio.Semaphore(max_c)

        # Executor for substeps
        step_executor: ExecutorProtocol = Executor(self.logger)
        substeps_recipe: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered: bool = False
        tasks: List[asyncio.Task] = []
        completed_count: int = 0

        async def process_single_item(
            key: Any, value: Any
        ) -> Tuple[Any, Any, Optional[str]]:
            # Clone context for isolation
            item_ctx: ContextProtocol = context.clone()
            item_ctx[self.config.item_key] = value
            # Attach iteration metadata
            if isinstance(items_obj, list):
                item_ctx["__index"] = key
            else:
                item_ctx["__key"] = key
            try:
                self.logger.debug(f"LoopStep: Starting item {key}.")
                await step_executor.execute(substeps_recipe, item_ctx)
                # Retrieve processed item result
                result = item_ctx.get(self.config.item_key, value)
                self.logger.debug(f"LoopStep: Finished item {key}.")
                return key, result, None
            except Exception as exc:
                self.logger.error(f"LoopStep: Error processing item {key}: {exc}")
                return key, None, str(exc)

        async def run_sequential() -> None:
            nonlocal fail_fast_triggered, completed_count
            for key, value in items_list:
                if fail_fast_triggered:
                    break
                idx, res, err = await process_single_item(key, value)
                if err:
                    # Record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # Record success
                    if isinstance(results, list):
                        results.append(res)
                    else:
                        results[idx] = res
                completed_count += 1

        async def run_parallel() -> None:
            nonlocal fail_fast_triggered, completed_count

            async def worker(k: Any, v: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore:
                    async with semaphore:
                        return await process_single_item(k, v)
                return await process_single_item(k, v)

            # Launch tasks with optional delay
            for idx, (k, v) in enumerate(items_list):  # type: ignore
                if fail_fast_triggered:
                    break
                task = asyncio.create_task(worker(k, v))
                tasks.append(task)
                if self.config.delay and idx < total_items - 1:
                    await asyncio.sleep(self.config.delay)

            # Collect task results as they complete
            for fut in asyncio.as_completed(tasks):
                if fail_fast_triggered:
                    break
                try:
                    k, res, err = await fut
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": k, "error": err})
                        else:
                            errors[k] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(res)
                        else:
                            results[k] = res
                    completed_count += 1
                except Exception as exc:
                    self.logger.error(f"LoopStep: Unexpected exception: {exc}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break

        # Execute in chosen mode
        if self.config.max_concurrency and self.config.max_concurrency > 1:
            await run_parallel()
        else:
            await run_sequential()

        # Store results and errors in parent context
        context[self.config.result_key] = results
        has_errors = bool(errors) if isinstance(errors, list) else bool(errors)
        if has_errors:
            context[f"{self.config.result_key}__errors"] = errors

        self.logger.info(
            f"LoopStep: Processed {completed_count} items. Errors: "
            f"{len(errors) if has_errors else 0}."
        )


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dicts.
    """
    current: Any = context
    for part in path.split('.'):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current
