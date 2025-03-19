"""
Configuration module for the Remote Graphs Application.
This module defines the Settings class, which utilizes BaseSettings from pydantic_settings to manage
configuration parameters for the application. The settings include:
- API_V1_STR: The base URL prefix for version 1 of the API.
- ENVIRONMENT: The current runtime environment, restricted to "local", "staging", or "production".
- PROJECT_NAME: The name of the project.
- DESCRIPTION: A brief summary of the project's purpose.
A global instance of the Settings class is instantiated as `settings` to provide application-wide access
to these configuration values.
"""

from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the Remote Graphs Application."""

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str = "Remote Graphs Application"
    DESCRIPTION: str = "Application to demonstrate remote graphs"


settings = Settings()  # type: ignore
