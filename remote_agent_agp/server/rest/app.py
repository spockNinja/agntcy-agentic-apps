"""
The Langchain Agent Protocol Server (LAPS) serves as the entry point for a FastAPI application
configured with JSON logging, environment variable loading, and asynchronous lifespan management.
Designed for secure, headless operation, it will not bind to any IP/port but instead consumes
packets via HTTP injection, aligning with the requirements of Agent operations.

Key functionalities include:
- Loading and managing environment variables using dotenv.
- Configuring JSON-based logging to capture critical startup and runtime events.
- Defining an async lifespan context manager for initializing and cleaning up resources during startup
    and shutdown.
- Creating and configuring the FastAPI application with custom route handlers, unique route ID generation,
    and CORS middleware.
- Serving as the protocol server endpoint for Langgraph Agents, emphasizing secure, injection-based
    packet consumption over traditional network listening.

This design prioritizes clear separation of concerns and facilitates secure integration with Langgraph
agent workflows.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from langsmith.middleware import TracingMiddleware
from starlette.middleware.cors import CORSMiddleware

from .api.routes import stateless_runs
from .core.config import settings

# Step 1: Initialize a basic logger first (to avoid errors before full configuration)
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Minimal level before full configuration
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


def load_environment_variables(env_file: str | None = None) -> None:
    """
    Load environment variables from a .env file safely.

    This function loads environment variables from a `.env` file, ensuring
    that critical configurations are set before the application starts.

    Args:
        env_file (str | None): Path to a specific `.env` file. If None,
                               it searches for a `.env` file automatically.

    Behavior:
    - If `env_file` is provided, it loads the specified file.
    - If `env_file` is not provided, it attempts to locate a `.env` file in the project directory.
    - Logs a warning if no `.env` file is found.

    Returns:
        None
    """
    env_path = env_file or find_dotenv()

    if env_path:
        load_dotenv(env_path, override=True)
        logger.info(".env file loaded from %s", env_path)
    else:
        logger.warning("No .env file found. Ensure environment variables are set.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Defines startup and shutdown logic for the FastAPI application.

    This function follows the `lifespan` approach, allowing resource initialization
    before the server starts and cleanup after it shuts down.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: The application runs while `yield` is active.

    Behavior:
    - On startup: Logs a startup message.
    - On shutdown: Logs a shutdown message.
    - Can be extended to initialize resources (e.g., database connections).
    """
    logging.info("Starting Remote Graphs App...")

    # Example: Attach database connection to app state (if needed)
    # app.state.db = await init_db_connection()

    yield  # Application runs while 'yield' is in effect.

    logging.info("Application shutdown")

    # Example: Close database connection (if needed)
    # await app.state.db.close()


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generates a unique identifier for API routes.

    Args:
        route (APIRoute): The FastAPI route object.

    Returns:
        str: A unique string identifier for the route.

    Behavior:
    - If the route has tags, the ID is formatted as `{tag}-{route_name}`.
    - If no tags exist, the route name is used as the ID.
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def add_handlers(app: FastAPI) -> None:
    """
    Adds global route handlers to the FastAPI application.

    This function registers common endpoints, such as the root message
    and the favicon.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """

    @app.get(
        "/",
        summary="Root endpoint",
        description="Returns a welcome message for the API.",
        tags=["General"],
    )
    async def root() -> dict:
        """
        Root endpoint that provides a welcome message.

        Returns:
            dict: A JSON response with a greeting message.
        """
        return {"message": "Gateway of the App"}

    @app.get("/favicon.png", include_in_schema=False)
    async def favicon() -> FileResponse:
        """
        Serves the favicon as a PNG file.

        This prevents the browser from repeatedly requesting a missing
        favicon when accessing the API.

        Returns:
            FileResponse: A response serving the `favicon.png` file.

        Raises:
            FileNotFoundError: If the favicon file is missing.
        """
        file_name = "favicon.png"
        file_path = os.path.join(app.root_path, "", file_name)
        return FileResponse(
            path=file_path, media_type="image/png"  # Ensures it's served inline
        )


def create_fastapi_app() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    This function sets up:
    - The API metadata (title, version, OpenAPI URL).
    - CORS middleware to allow cross-origin requests.
    - Route handlers for API endpoints.
    - A custom unique ID generator for API routes.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        version="0.1.0",
        description=settings.PROJECT_NAME,
        lifespan=lifespan,  # Use the new lifespan approach for startup/shutdown
    )

    add_handlers(app)
    app.include_router(stateless_runs.router, prefix=settings.API_V1_STR)

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.add_middleware(TracingMiddleware)

    return app
