# SPDX-FileCopyrightText: Copyright (c) 2025 Cisco and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import find_dotenv, load_dotenv

from core.logging_config import configure_logging
from gateway.gateway_holder import GatewayHolder
from gateway.api import start_data_plane, try_connect_to_gateway
from rest.app import create_fastapi_app

# Define logger at the module level
logger = logging.getLogger("app")


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
        logging.info(".env file loaded from %s", env_path)
    else:
        logging.warning("No .env file found. Ensure environment variables are set.")


async def main() -> None:
    """
    Entry point for running the application.

    This function performs the following:
    - Configures logging globally.
    - Loads environment variables from a `.env` file.
    - Retrieves the address for the remote gateway
    - Connects to the gateway and waits for incoming messages

    Returns:
        None
    """
    configure_logging()
    logger.info("Starting AGP application...")

    load_environment_variables()

    GatewayHolder.create_gateway()
    GatewayHolder.set_fastapi_app(create_fastapi_app())

    port = os.getenv("PORT", "46357")
    address = os.getenv("AGP_ADDRESS", "http://127.0.0.1")

    try:
        _ = await try_connect_to_gateway(address, port)
        await start_data_plane()
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    except Exception as e:
        logger.info("Unhandled error: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
