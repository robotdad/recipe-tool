"""API call configuration model."""

from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field


class ApiCallConfig(BaseModel):
    """Configuration for making API calls."""

    url: str = Field(description="URL to call")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(
        description="HTTP method to use", default="GET"
    )
    headers: Optional[Dict[str, str]] = Field(description="HTTP headers", default=None)
    data_variable: Optional[str] = Field(
        description="Name of the variable containing the data to send", default=None
    )
    auth_variable: Optional[str] = Field(
        description="Name of the variable containing auth credentials", default=None
    )
    output_variable: str = Field(
        description="Name of the variable to store the response in"
    )
    timeout: Optional[int] = Field(
        description="Timeout in seconds for the API call", default=30
    )
    retry_count: int = Field(
        description="Number of retries for failed requests", default=3
    )
    retry_delay: int = Field(description="Delay in seconds between retries", default=1)
