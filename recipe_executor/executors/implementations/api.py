"""API call executor implementation."""

import asyncio
import json
import logging
from typing import Any, Dict

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class ApiCallExecutor:
    """Executor for API call steps."""

    async def execute(
        self, step: RecipeStep, context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute an API call step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            API response
        """
        if not step.api_call:
            raise ValueError(f"Missing api_call configuration for step {step.id}")

        config = step.api_call

        # Import aiohttp for async HTTP requests
        try:
            import aiohttp
        except ImportError:
            raise ImportError(
                "The aiohttp package is required for API calls. Install with: pip install aiohttp"
            )

        # Interpolate URL and prepare request
        url = context.interpolate_variables(config.url)
        method = config.method

        # Prepare headers
        headers = {}
        if config.headers:
            for name, value in config.headers.items():
                headers[name] = context.interpolate_variables(value)

        # Prepare data
        data = None
        if config.data_variable:
            data_var = context.get_variable(config.data_variable)
            if data_var is not None:
                if isinstance(data_var, dict):
                    data = data_var
                elif isinstance(data_var, str):
                    try:
                        data = json.loads(data_var)
                    except json.JSONDecodeError:
                        data = {"data": data_var}
                else:
                    data = {"data": str(data_var)}

        # Prepare auth
        auth = None
        if config.auth_variable:
            auth_var = context.get_variable(config.auth_variable)
            if isinstance(auth_var, tuple) and len(auth_var) == 2:
                auth = aiohttp.BasicAuth(auth_var[0], auth_var[1])
            elif (
                isinstance(auth_var, dict)
                and "username" in auth_var
                and "password" in auth_var
            ):
                auth = aiohttp.BasicAuth(auth_var["username"], auth_var["password"])

        # Set up timeout
        timeout = config.timeout
        if timeout is None and step.timeout:
            timeout = step.timeout
        if timeout is None and context.recipe and context.recipe.timeout:
            timeout = context.recipe.timeout

        # Create aiohttp timeout
        timeout_obj = None
        if timeout:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)

        # Execute the request with retry logic
        retry_count = 0
        max_retries = config.retry_count
        retry_delay = config.retry_delay

        while True:
            try:
                async with aiohttp.ClientSession(
                    auth=auth, timeout=timeout_obj
                ) as session:
                    if method == "GET":
                        async with session.get(
                            url, headers=headers, json=data
                        ) as response:
                            status = response.status
                            try:
                                result = await response.json()
                            except json.JSONDecodeError:
                                result = {
                                    "text": await response.text(),
                                    "status": status,
                                }
                    elif method == "POST":
                        async with session.post(
                            url, headers=headers, json=data
                        ) as response:
                            status = response.status
                            try:
                                result = await response.json()
                            except json.JSONDecodeError:
                                result = {
                                    "text": await response.text(),
                                    "status": status,
                                }
                    elif method == "PUT":
                        async with session.put(
                            url, headers=headers, json=data
                        ) as response:
                            status = response.status
                            try:
                                result = await response.json()
                            except json.JSONDecodeError:
                                result = {
                                    "text": await response.text(),
                                    "status": status,
                                }
                    elif method == "DELETE":
                        async with session.delete(
                            url, headers=headers, json=data
                        ) as response:
                            status = response.status
                            try:
                                result = await response.json()
                            except json.JSONDecodeError:
                                result = {
                                    "text": await response.text(),
                                    "status": status,
                                }
                    elif method == "PATCH":
                        async with session.patch(
                            url, headers=headers, json=data
                        ) as response:
                            status = response.status
                            try:
                                result = await response.json()
                            except json.JSONDecodeError:
                                result = {
                                    "text": await response.text(),
                                    "status": status,
                                }
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                # Check for error status
                if status >= 400:
                    logger.warning(f"API call returned error status {status}: {result}")

                    # Retry if appropriate
                    if retry_count < max_retries and (
                        (status >= 500) or (status == 429)
                    ):
                        retry_count += 1
                        logger.info(
                            f"Retrying API call ({retry_count}/{max_retries}) after {retry_delay}s"
                        )
                        await asyncio.sleep(retry_delay)
                        continue

                    if not step.continue_on_error:
                        raise ValueError(f"API call failed with status {status}")

                # Add status to result if it's a dictionary
                if isinstance(result, dict) and "status" not in result:
                    result["status"] = status

                return result
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"API call error: {e}")

                # Retry if appropriate
                if retry_count < max_retries:
                    retry_count += 1
                    logger.info(
                        f"Retrying API call ({retry_count}/{max_retries}) after {retry_delay}s"
                    )
                    await asyncio.sleep(retry_delay)
                    continue

                if not step.continue_on_error:
                    raise

                return {"error": str(e), "status": 0}

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of an API call step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.api_call:
            return ValidationResult(valid=True, issues=[])

        # Check that the result is a dictionary
        if not isinstance(result, dict):
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message="API call result is not a dictionary", severity="error"
                    )
                ],
            )

        # Check the status code
        status = result.get("status", 0)
        if status >= 400:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"API call failed with status {status}",
                        severity="error",
                    )
                ],
            )

        # Check for error field
        if "error" in result:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"API call returned error: {result['error']}",
                        severity="error",
                    )
                ],
            )

        return ValidationResult(valid=True, issues=[])
