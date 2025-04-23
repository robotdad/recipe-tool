import logging
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig


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
    """LoopStep: iterate over a collection and run substeps for each item."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Retrieve the items collection
        raw = context.get(self.config.items)
        if raw is None:
            raise ValueError(f"LoopStep: context missing items key '{self.config.items}'")

        # Determine iteration mode
        is_mapping = isinstance(raw, dict)
        if is_mapping:
            iterable = list(raw.items())  # type: ignore
            total = len(iterable)
        elif isinstance(raw, (list, tuple)):
            iterable = list(enumerate(raw))
            total = len(iterable)
        else:
            raise ValueError(
                f"LoopStep: items under '{self.config.items}' is not iterable (got {type(raw)})"
            )

        self.logger.info(
            f"LoopStep: processing {total} items from key '{self.config.items}'"
        )

        results_list: List[Any] = []
        results_map: Dict[Any, Any] = {}
        errors: List[Dict[str, Any]] = []

        from recipe_executor.steps.registry import STEP_REGISTRY

        for idx, val in iterable:
            self.logger.debug(f"LoopStep: start item '{idx}'")
            # Clone context for isolation
            ctx_clone = context.clone()
            # Inject current item and index/key
            ctx_clone[self.config.item_key] = val
            if is_mapping:
                ctx_clone["__key"] = idx
            else:
                ctx_clone["__index"] = idx

            try:
                # Execute substeps sequentially
                for step_conf in self.config.substeps:
                    stype = step_conf.get("type")
                    if not stype:
                        raise ValueError("LoopStep: substep missing 'type'")
                    StepCls = STEP_REGISTRY.get(stype)
                    if StepCls is None:
                        raise ValueError(f"LoopStep: unknown substep type '{stype}'")
                    config_dict = step_conf.get("config", {}) or {}
                    step: StepProtocol = StepCls(self.logger, config_dict)
                    # substeps may be async
                    result = step.execute(ctx_clone)
                    if hasattr(result, "__await__"):
                        await result  # type: ignore
                # Extract processed item result
                item_result = ctx_clone.get(self.config.item_key)
                # Collect result
                if is_mapping:
                    results_map[idx] = item_result
                else:
                    results_list.append(item_result)
                self.logger.debug(f"LoopStep: finished item '{idx}'")
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(
                    f"LoopStep: error on item '{idx}': {e}\n{tb}"
                )
                if self.config.fail_fast:
                    raise
                errors.append({
                    "item_key": idx,
                    "error": str(e),
                    "traceback": tb,
                })
                # continue to next item

        # Assemble final result
        if is_mapping:
            final: Union[Dict[Any, Any], Any] = results_map
            if errors:
                final["__errors"] = errors  # type: ignore
        else:
            if errors:
                final = {"results": results_list, "__errors": errors}
            else:
                final = results_list

        # Store in parent context
        context[self.config.result_key] = final
        self.logger.info(
            f"LoopStep: stored results under '{self.config.result_key}'"
        )