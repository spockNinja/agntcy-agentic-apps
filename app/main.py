from __future__ import annotations

import os
import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import stateless_runs
from app.core.config import settings


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Defines startup and shutdown logic. Everything before 'yield' is startup,
    everything after 'yield' is shutdown.
    """
    # --- Startup logic ---
    logging.info("Starting Agentic DB API...")

    # If you have resources to initialize (e.g., DB connections),
    # do them here and attach them to 'app.state' if needed.
    # Example:
    # app.state.db = await init_db_connection()

    yield  # The application runs (serves requests) while 'yield' is in effect.

    # --- Shutdown logic ---
    logging.info("Application shutdown")

    # Close or clean up any resources before exit
    # Example:
    # await app.state.db.close()


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def add_handlers(app: FastAPI):
    @app.get("/", summary="Root endpoint", description="Returns a welcome message for the API.", tags=["General"])
    async def root() -> dict:
        return {"message": "Gateway of the App"}

    # @app.get('/favicon.ico', include_in_schema=False)
    # async def favicon():
    #     file_name = "favicon.ico"
    #     file_path = os.path.join(app.root_path, "", file_name)
    #     return FileResponse(path=file_path, headers={"Content-Disposition": "image/x-icon; filename=" + file_name})

    @app.get("/favicon.png", include_in_schema=False)
    async def favicon() -> FileResponse:
        """
        Serves the favicon as a PNG. The media_type is set so it won't be downloaded.
        """
        file_name = "favicon.png"
        file_path = os.path.join(app.root_path, "", file_name)
        return FileResponse(
            path=file_path,
            media_type="image/png"  # This ensures it's served inline
        )


def create_app():

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
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    return app


def main() -> None:
    """
    Entry point for running the application via python main.py
    """
    # If you want to allow an environment variable override for the port, do so here
    port = int(os.getenv("PORT", "8123"))
    uvicorn.run(
        create_app(),
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
