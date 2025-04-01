# ParallelStep Component Usage

## Importing

To use the ParallelStep in your project, import the step class and its configuration class from the recipe executor’s steps module:

```python
from recipe_executor.steps.parallel import ParallelStep, ParallelConfig
```

## Configuration

The ParallelStep is configured with a corresponding `ParallelConfig` class, which defines its parameters:

```python
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
```

In the configuration:

- **`substeps`** (required) is a list of step configurations, where each item is typically an object/dict specifying an `execute_recipe` step (with its `recipe_path`, and optionally `context_overrides`, etc.). This defines which sub-recipes will be run in parallel.
- **`max_concurrency`** (optional) limits how many sub-recipes run at the same time. For example, setting `max_concurrency` to 2 will ensure at most two substeps are executing in parallel; additional substeps will wait until a slot is free. If this value is 0 or not set, the ParallelStep will attempt to run all substeps concurrently (unbounded, which effectively means as many threads as substeps).
- **`delay`** (optional) if provided, introduces a pause between launching each substep. This is useful to stagger execution starts. For instance, a delay of `1.5` means after starting one substep, the ParallelStep will wait 1.5 seconds before starting the next substep. By default this is 0, meaning no deliberate delay between thread launches.

## Step Registration

Like other step types, the ParallelStep must be registered so the Recipe Executor knows about it. This is typically done in the steps registry setup:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.parallel import ParallelStep

STEP_REGISTRY["parallel"] = ParallelStep
```

Registering the `"parallel"` type ensures that when a recipe contains a step with `"type": "parallel"`, the executor will instantiate and use a `ParallelStep` to execute it.

## Basic Usage in Recipes

The ParallelStep is used in recipes to run multiple sub-recipes concurrently. This is ideal when you have several independent tasks that can be executed in parallel to reduce overall runtime. For example, suppose you want to run two separate sub-recipes at the same time — you can define a parallel step as follows:

```json
{
  "steps": [
    {
      "type": "parallel",
      "substeps": [
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_a.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        },
        {
          "type": "execute_recipe",
          "recipe_path": "recipes/subtask_b.json",
          "context_overrides": {
            "input_data": "{{shared_input}}"
          }
        }
      ],
      "max_concurrency": 2,
      "delay": 1
    }
  ]
}
```

In this JSON snippet:

- The `ParallelStep` is represented by an object with `"type": "parallel"`. It contains a `substeps` array defining two sub-steps, each of which is an `execute_recipe` step running a sub-recipe (`subtask_a.json` and `subtask_b.json`). Both sub-recipes in this example use a context value `shared_input` (passed via context overrides) but they will run in isolation from each other.
- The `max_concurrency` is set to `2`, meaning up to two substeps can run at the same time. Here we have exactly two substeps, so they will indeed run simultaneously. If there were more substeps than the concurrency limit, the extra ones would wait until others finish before starting.
- The `delay` is set to `1` second. This will cause the ParallelStep to wait 1 second after launching the first substep (`subtask_a`) before launching the second substep (`subtask_b`). The delay can help in staggering the workload (for example, to avoid hitting a resource spike by starting many tasks at the exact same moment). In this case, since `max_concurrency` is 2 and we have 2 substeps, both will still run in parallel (just with a 1-second offset in their start times).

When the ParallelStep executes, it will start both **Subtask A** and **Subtask B** almost concurrently (with the specified delay). Each subtask will run in its own cloned context, so any changes they make to context (like artifacts or intermediate data) remain in their sub-recipe’s context. The parent recipe’s context (`shared_input` in this case) is not modified by the sub-recipes, unless you explicitly write results back to it (which by default does not happen in the current design).

## Error Handling

If any sub-recipe within the parallel step fails or throws an error, the ParallelStep will halt and propagate that error immediately (fail-fast). This means you should be prepared to catch exceptions from a ParallelStep execution just as you would for other steps. For example:

```python
try:
    parallel_step.execute(context)
except Exception as e:
    # If any substep fails, an exception will be raised here
    print(f"Parallel step failed: {e}")
```

In practice, the type of exception will depend on the nature of the sub-recipe failure. For instance, if one sub-recipe tries to read a missing file, a `FileNotFoundError` might be raised; if a sub-recipe has an invalid configuration, it could raise a `ValueError` or custom step error. The ParallelStep does not yet define a special exception type for aggregated errors, so it will typically raise the first encountered sub-step exception. The error message should include information to identify which substep failed (e.g., the recipe path or an index) to aid in debugging. All other substeps will be canceled or stopped as soon as an error is detected, so their effects (if any) might be partial or rolled back when the exception is raised.

## Important Notes

1. **Context Isolation:** Each substep runs with its own cloned Context. The ParallelStep uses a deep copy of the parent context for each sub-recipe, meaning substeps do not share state with each other. Any modifications a sub-recipe makes to its context will _not_ appear in the parent or sibling contexts. This prevents race conditions or data leaks between parallel tasks. (The parent context remains unchanged by default through the parallel execution.)
2. **Concurrency Control:** The `max_concurrency` setting governs how many sub-recipes execute simultaneously. If you have more substeps than the `max_concurrency`, the extra substeps will wait in a queue until a running substep finishes. By default (`max_concurrency: 0` meaning unlimited), the ParallelStep will launch all substeps at once, which can maximize parallelism but also increase load on the system. It’s often wise to set a reasonable limit based on your environment (e.g., number of CPU cores or external API rate limits).
3. **Launch Delay:** Using the `delay` parameter, you can stagger the start of each parallel task. In high-load scenarios, a slight delay (even a fraction of a second) between launches can prevent all threads from spiking at exactly the same time. The delay is applied between each substep launch. For example, with `delay: 2`, there will be a 2-second pause before launching each subsequent substep. If `max_concurrency` is also set, the delay still applies as long as additional substeps are being started.
4. **Fail-Fast Behavior:** ParallelStep is designed to fail fast. If any one of the parallel sub-recipes fails, the entire ParallelStep is considered failed immediately. In such a case, no further substeps will be started, and any substeps that are still running may be interrupted or will be awaited to stop. This ensures that you don’t continue a workflow when part of the parallel work has gone wrong. You should design parallel tasks such that they can either all succeed or handle partial failure if that’s acceptable (future enhancements may allow continuing despite one failure, but currently the behavior is to abort on first error).
5. **Limitations:** As of now, the ParallelStep can only execute substeps of type `execute_recipe`. In other words, each parallel subtask must be an entire sub-recipe executed via an ExecuteRecipeStep. You cannot yet list arbitrary step types under `substeps` (e.g., you cannot directly put a `"type": "read_file"` step in substeps for parallel execution at this time). This may be expanded in the future to allow more flexible parallelization of different step kinds.
6. **No Automatic Result Merging:** Results produced by sub-recipes (for example, artifacts or context changes within those sub-recipes) are not automatically merged back into the parent context. Currently, the ParallelStep treats sub-recipes as isolated parallel jobs whose side-effects remain in their own contexts. If you need to use results from sub-recipes, you would have to handle that in the sub-recipes themselves (e.g. writing to a common output or updating an external resource), or a future enhancement of ParallelStep may provide a way to collect outputs. This is an important consideration when designing your recipes – ensure that either the parallel tasks are truly independent or that you implement a mechanism to consolidate their outcomes afterward.
