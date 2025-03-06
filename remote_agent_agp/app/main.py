# SPDX-FileCopyrightText: Copyright (c) 2025 Cisco and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import asyncio
import json
import signal
import agp_bindings
import logging
import os

# move this to a common place
from core.logging_config import configure_logging
from dotenv import find_dotenv, load_dotenv

gateway = agp_bindings.Gateway()


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
        logging.info(f".env file loaded from {env_path}")
    else:
        logging.warning("No .env file found. Ensure environment variables are set.")


def create_error(error, code) -> str:
    """
    Creates a reply message with an error code
    """
    payload = {
        "message": error,
        "error": code,
    }
    msg = json.dumps(payload)
    return msg


def message_parsing(payload) -> str:
    """
    Parse the message and looks for errors
    Replies to the incoming message if no error is detected
    """
    logging.debug("Decoded payload: %s", payload)

    # Extract assistant_id from the payload
    agent_id = payload.get("agent_id")
    logging.debug(f"Agent id: {agent_id}")

    # Validate that the assistant_id is not empty.
    if not payload.get("agent_id"):
        return create_error("agent_id is required and cannot be empty.", 422)

    # Extract the route from the message payload.
    # This step is done to emulate the behavior of the REST API.
    route = payload.get("route")
    if not payload.get("route") or route != "/runs":
        return create_error("Not Found.", 404)

    # Validate the config section: ensure that config.tags is a non-empty list.
    if (metadata := payload.get("metadata", None)) is not None:
        message_id = metadata.get("id")

    # -----------------------------------------------
    # Extract the human input content from the payload.
    # We expect the content to be located at: payload["input"]["messages"][0]["content"]
    # -----------------------------------------------

    # Retrieve the 'input' field and ensure it is a dictionary.
    input_field = payload.get("input")
    if not isinstance(input_field, dict):
        return create_error("The 'input' field should be a dictionary.", 500)

    # Retrieve the 'messages' list from the 'input' dictionary.
    messages = input_field.get("messages")
    if not isinstance(messages, list) or not messages:
        return create_error(
            "The 'input.messages' field should be a non-empty list.", 500
        )

    # Access the first message in the list.
    first_message = messages[0]
    if not isinstance(first_message, dict):
        return create_error(
            "The first element in 'input.messages' should be a dictionary.", 500
        )

    # Extract the 'content' from the first message.
    human_input_content = first_message.get("content")
    if human_input_content is None:
        return create_error(
            "Missing 'content' in the first message of 'input.messages'.", 500
        )

    messages = {
        "messages": [{"role": "assistant", "content": "Received remote request"}]
    }

    # payload to add to the reply
    payload = {
        "agent_id": agent_id,
        "output": messages,
        "model": "gpt-4o",
        "metadata": {"id": message_id},
    }

    msg = json.dumps(payload)
    return msg


def shutdown(loop):
    """
    Signal handler to cancel all tasks and stop the loop.
    """

    print("Received shutdown signal")
    for task in asyncio.all_tasks(loop):
        task.cancel()


async def connect_to_gateway(address) -> str:
    """
    Connection to the remote gateway
    Set states for forwarding and waits for incoming messages
    """

    # An agent app is identified by a name in the format
    # /organization/namespace/agent_class/agent_id. The agent_class indicates the
    # type of agent, and there can be multiple instances of the same type running
    # (e.g., horizontal scaling of the same app in Kubernetes). The agent_id
    # identifies a specific instance of the agent and it is returned by the
    # create_agent function is not provided
    organization = "cisco"
    namespace = "default"
    local_agent = "server"

    # Connect to the gateway server
    local_agent_id = await gateway.create_agent(organization, namespace, local_agent)

    # Connect to the service and subscribe for the local name
    # to receive content
    _ = await gateway.connect(address, insecure=True)
    await gateway.subscribe(organization, namespace, local_agent, local_agent_id)

    try:
        while True:
            src, recv = await gateway.receive()

            payload = json.loads(recv.decode("utf8"))
            msg = message_parsing(payload)

            # publish reply message to src agent
            await gateway.publish_to(msg.encode(), src)
    except asyncio.CancelledError:
        print("Shutdown server")


def main() -> None:
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
    configure_logging()  # Apply global logging settings

    logger = logging.getLogger("app")  # Default logger for main script
    logger.info("Starting AGP application...")

    # Load environment variables before starting the application
    load_environment_variables()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Register the signal handler for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, loop)
    try:
        # Determine gateway address from environment variables or use the default
        port = os.getenv("PORT", "46357")
        address = os.getenv("AGP_ADDRESS", "http://127.0.0.1")
        loop.run_until_complete(connect_to_gateway(address + ":" + port))
    except asyncio.CancelledError:
        print("Main task cancelled")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
