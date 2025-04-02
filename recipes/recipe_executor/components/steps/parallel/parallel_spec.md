# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It is designed to improve execution efficiency by parallelizing independent tasks, while isolating each sub-recipe’s state to prevent interference. This step type allows complex workflows to launch several sub-steps at once (up to a limit), coordinating their execution and consolidating their outcomes in a controlled manner.

## Core Requirements

- Accept a list of sub-step configurations (each sub-step must be of type `execute_recipe` representing a sub-recipe to run)
- Clone the current execution context for each sub-step to ensure isolation between parallel tasks (no cross-contamination of data)
- Launch sub-steps concurrently, respecting a configurable maximum concurrency limit (number of sub-steps running in parallel at a time)
- Optionally introduce a configurable delay (in seconds) between launching each sub-step to stagger start times if needed
- Wait for all spawned sub-steps to complete before marking the parallel step as finished (block until all threads finish or error out)
- **Fail-fast behavior**: if any sub-step encounters an error, immediately stop launching new sub-steps (and cancel running ones if possible) and report the error without waiting for the remaining sub-steps to finish

## Implementation Considerations

- Utilize a `ThreadPoolExecutor` (or similar threading mechanism) to manage parallel execution of sub-steps, using the provided concurrency limit as the `max_workers` to control the number of threads
- Use the Context’s `clone()` method to create a deep copy of the execution context for each sub-step. This ensures each sub-recipe operates on an independent context snapshot, preserving the initial state while preventing modifications from affecting the parent or sibling sub-steps
- If a launch delay is configured, implement a brief pause (e.g. using `time.sleep`) between submitting each sub-step to the thread pool. This delay helps to stagger the tasks’ start times for resource management or sequencing needs
- Provide detailed logging for each sub-step’s lifecycle: log when each sub-recipe starts, when it completes successfully, and any results or key outputs. Also log a final summary after all sub-steps finish (e.g. how many succeeded or failed) to give clarity on the parallel execution as a whole
- Collect and monitor exceptions from each thread as they finish. If an exception arises in any sub-step, capture it immediately and initiate a “fail-fast” shutdown of the remaining parallel tasks. This may involve canceling queued sub-steps in the ThreadPoolExecutor and preventing new submissions. Ensure thread pool shutdown and cleanup is handled to avoid lingering threads
- Consider the performance implications of context cloning and thread startup. Cloning a large context for many sub-steps could be memory-intensive; use efficient deep copy methods and possibly limit concurrency by default to avoid overwhelming system resources

## Component Dependencies

The ParallelStep component depends on:

- **Steps Base** – Inherits from the BaseStep abstract class (and uses a Pydantic StepConfig) to integrate with the step execution framework and configuration validation
- **Context** – Utilizes the Context component for passing data to sub-recipes, specifically calling `Context.clone()` to produce isolated context instances for each parallel sub-step
- **Step Registry** – Uses the Step Registry to resolve and instantiate the `execute_recipe` step for each sub-step configuration. The registry ensures the correct step class (ExecuteRecipeStep) is retrieved using the `type` field of each sub-step definition
- **Executor** – Leverages the RecipeExecutor (or similar execution engine) to actually run each sub-recipe in a separate thread. Each sub-step execution may internally create a new RecipeExecutor instance or use the existing executor infrastructure to perform the sub-recipe’s steps
- **Utils (Template Renderer)** – (Potentially) uses utility functions such as template rendering if sub-step definitions contain templated strings (e.g. in recipe paths or context overrides), ensuring that each sub-step’s configuration is fully resolved before execution

## Error Handling

- If any substep raises an exception during execution, the ParallelStep should immediately abort the parallel execution. This means no new substeps are started, and any pending substeps in the queue are canceled. The first encountered exception is propagated outward as the ParallelStep’s failure
- The error reported by the ParallelStep must clearly convey the context of the failure. For example, include which sub-recipe or sub-step index failed and the original exception message/stack trace. This helps users identify the failing parallel branch quickly
- Log an error entry when a sub-step fails, capturing the exception details and possibly the sub-step’s configuration or identifier. All other substeps should also log their completion status (whether skipped due to failure, canceled, or completed before the abort) for transparency
- Ensure that no threads remain running in the background after a failure is handled. The system should either join all threads or properly shut down the ThreadPoolExecutor to prevent orphaned threads. This guarantees that a failure in one parallel sub-step does not leave the system in an unstable state
- On normal completion (no errors), handle any exceptions or edge cases like timeouts or cancellations gracefully. If a sub-step times out or is externally canceled, treat it as a failure scenario and apply the same fail-fast handling

## Future Considerations

- **Support for arbitrary step types**: Expand the ParallelStep to allow running any step type in parallel (not just `execute_recipe`). This would enable parallel execution of fine-grained steps (like file reads, LLM calls, etc.) directly, not only whole sub-recipes. It would involve generalizing sub-step handling and possibly refining context sharing/merging strategies
- **Result aggregation**: Provide mechanisms to collect outputs or artifacts from sub-steps back into the parent context once all substeps have finished. Future versions might allow specifying how each sub-step’s results (modified contexts, artifacts, or return values) are merged or reported to the parent execution flow. This could include combining artifacts, selecting a particular sub-step’s result to propagate, or summarizing multiple outcomes
- **Dynamic concurrency control**: Consider more advanced features like dynamically adjusting the concurrency level based on system load or sub-step characteristics, and providing better scheduling (e.g. prioritize certain substeps)
- **Timeout and isolation options**: Introduce optional timeouts for substeps or the entire parallel block, and more configurable isolation (for example, choosing to merge contexts automatically vs keep them separate) as the ParallelStep evolves to handle more complex scenarios
