import logging
from typing import Any, Dict, Iterator, List, Tuple, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over.
        item_key: Key to use when storing the current item in each iteration's context.
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error (default: True).
    """

    items: str
    item_key: str
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve the items path via template
        path_str = render_template(self.config.items, context)
        if not path_str:
            raise ValueError(f"LoopStep: items path resolved to empty string from '{self.config.items}'")

        # Traverse context snapshot to get the collection
        data = context.dict()
        current: Any = data
        for part in path_str.split("."):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"LoopStep: could not resolve part '{part}' in path '{path_str}'")
            current = current[part]
        items_obj = current

        # Determine iteration type and prepare results container
        if isinstance(items_obj, dict):
            iter_items: Iterator[Tuple[Any, Any]] = iter(items_obj.items())
            is_mapping = True
            results: Dict[Any, Any] = {}
            count = len(items_obj)
        elif isinstance(items_obj, (list, tuple)):
            iter_items = enumerate(items_obj)
            is_mapping = False
            results = []  # type: ignore
            count = len(items_obj)
        elif items_obj is None:
            self.logger.info(f"LoopStep: no items found at '{path_str}', storing empty result")
            empty: Union[List[Any], Dict[Any, Any]] = []
            context[self.config.result_key] = empty
            return
        else:
            # Single non-iterable item
            iter_items = enumerate([items_obj])
            is_mapping = False
            results = []  # type: ignore
            count = 1

        self.logger.info(f"LoopStep: processing {count} item(s) from '{path_str}'")
        errors: List[Dict[str, Any]] = []

        from recipe_executor.executor import Executor

        # Iterate and execute substeps in isolated contexts
        for key, item in iter_items:
            label = key if is_mapping else f"index {key}"
            self.logger.debug(f"LoopStep: start processing item {label}")
            sub_ctx = context.clone()
            # Inject current item and index/key
            sub_ctx[self.config.item_key] = item
            if is_mapping:
                sub_ctx["__key"] = key  # type: ignore
            else:
                sub_ctx["__index"] = key  # type: ignore

            # Assemble a small recipe for the substeps
            recipe = {"steps": self.config.substeps}

            executor = Executor(self.logger)
            try:
                await executor.execute(recipe, sub_ctx)
            except Exception as e:
                self.logger.error(f"LoopStep: error processing item {label}: {e}", exc_info=True)
                err_info = {"key": key, "error": str(e)}
                errors.append(err_info)
                if self.config.fail_fast:
                    raise
                # skip adding a result for failed item
                continue

            # Collect the processed item (load from same item_key)
            try:
                result_item = sub_ctx[self.config.item_key]
            except KeyError:
                self.logger.error(f"LoopStep: missing '{self.config.item_key}' after processing item {label}")
                if self.config.fail_fast:
                    raise
                continue

            # Store into results
            if is_mapping:
                results[key] = result_item  # type: ignore
            else:
                results.append(result_item)  # type: ignore
            self.logger.debug(f"LoopStep: finished processing item {label}")

        # Store final results and any errors
        context[self.config.result_key] = results  # type: ignore
        if errors:
            err_key = f"{self.config.result_key}__errors"
            context[err_key] = errors  # type: ignore
            self.logger.info(f"LoopStep: encountered {len(errors)} error(s); stored under '{err_key}'")
        self.logger.info(
            f"LoopStep: completed loop, stored {count - len(errors)} successful result(s) under '{self.config.result_key}'"
        )
