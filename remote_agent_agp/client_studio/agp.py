# SPDX-FileCopyrightText: Copyright (c) 2025 Cisco and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0

# Description: This file contains a sample graph client that makes a stateless request to the Remote Graph Server.
# Usage: python3 client/rest.py

import asyncio
import json
import os
import uuid
from typing import Annotated, Any, Dict, List, TypedDict

import agp_bindings
from agp_bindings import GatewayConfig
from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.utils import convert_to_openai_messages
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from logging_config import configure_logging

logger = configure_logging()


class GatewayHolder:
    gateway = None


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
        logger.info(f".env file loaded from {env_path}")
    else:
        logger.warning("No .env file found. Ensure environment variables are set.")


def decode_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decodes the JSON response from the remote server and extracts relevant information.

    Args:
        response_data (Dict[str, Any]): The JSON response from the server.

    Returns:
        Dict[str, Any]: A structured dictionary containing extracted response fields.
    """
    try:
        agent_id = response_data.get("agent_id", "Unknown")
        output = response_data.get("output", {})
        model = response_data.get("model", "Unknown")
        metadata = response_data.get("metadata", {})

        # Extract messages if present
        messages = output.get("messages", [])

        return {
            "agent_id": agent_id,
            "messages": messages,
            "model": model,
            "metadata": metadata,
        }
    except Exception as e:
        return {"error": f"Failed to decode response: {str(e)}"}


# Define the graph state
class GraphState(TypedDict):
    """Represents the state of the graph, containing a list of messages."""

    messages: Annotated[List[BaseMessage], add_messages]
    gateway: GatewayHolder


async def send_and_recv(msg) -> Dict[str, Any]:
    """
    Send a message to the remote endpoint and
    waits for the reply
    """

    gateway = GatewayHolder.gateway
    if gateway is not None:
        await gateway.publish(msg.encode(), "cisco", "default", "server")
        _, recv = await gateway.receive()
    else:
        raise RuntimeError("Gateway is not initialized yet!")

    response_data = json.loads(recv.decode("utf8"))

    # check for errors
    error_code = response_data.get("error")
    if error_code is not None:
        error_msg = {
            "error": "AGP request failed",
            "status_code": error_code,
            "exception": response_data.get("message"),
        }
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    else:
        # decode message
        decoded_response = decode_response(response_data)
        logger.info(decoded_response)

        # We only store in shared memory the last message from remote to avoid duplication
        return {"messages": decoded_response.get("messages", [])[-1]}


def node_remote_agp(state: GraphState) -> Dict[str, Any]:
    if not state["messages"]:
        logger.error(json.dumps({"error": "GraphState contains no messages"}))
        return {"messages": [HumanMessage(content="Error: No messages in state")]}

    # Extract the latest user query
    query = state["messages"][-1].content
    logger.info(json.dumps({"event": "sending_request", "query": query}))

    messages = convert_to_openai_messages(state["messages"])

    # payload to send to remote server at /runs endpoint
    payload = {
        "agent_id": "remote_agent",
        "input": {"messages": messages},
        "model": "gpt-4o",
        "metadata": {"id": str(uuid.uuid4())},
        # Add the route field to emulate the REST API
        "route": "/runs",
    }

    msg = json.dumps(payload)
    res = asyncio.run(send_and_recv(msg))
    return res


async def connect_to_gateway(address):
    # An agent app is identified by a name in the format
    # /organization/namespace/agent_class/agent_id. The agent_class indicates the
    # type of agent, and there can be multiple instances of the same type running
    # (e.g., horizontal scaling of the same app in Kubernetes). The agent_id
    # identifies a specific instance of the agent and it is returned by the
    # create_agent function is not provided
    organization = "cisco"
    namespace = "default"
    local_agent = "client"
    remote_agent = "server"

    # Define the service based on the local agent
    gateway = agp_bindings.Gateway()

    # Configure gateway
    config = GatewayConfig(endpoint=address, insecure=True)
    gateway.configure(config)

    # Connect to the gateway server
    local_agent_id = await gateway.create_agent(organization, namespace, local_agent)

    # Connect to the service and subscribe for the local name
    # to receive content
    try:
        _ = await gateway.connect()
    except Exception as e:
        raise ValueError(f"{e}")
    await gateway.subscribe(organization, namespace, local_agent, local_agent_id)

    # set the state to connect to the remote agent
    await gateway.set_route(organization, namespace, remote_agent)
    return gateway


# Build the state graph
async def build_graph() -> Any:
    """
    Constructs the state graph for handling requests.

    Returns:
        StateGraph: A compiled LangGraph state graph.
    """
    await init_gateway_conn()
    builder = StateGraph(GraphState)
    builder.add_node("node_remote_agp", node_remote_agp)
    builder.add_edge(START, "node_remote_agp")
    builder.add_edge("node_remote_agp", END)
    return builder.compile()


async def init_gateway_conn():
    port = os.getenv("PORT", "46357")
    address = os.getenv("AGP_ADDRESS", "http://127.0.0.1")
    # TBD: Part of graph config
    GatewayHolder.gateway = await connect_to_gateway(address + ":" + port)


async def main():
    load_environment_variables()
    await init_gateway_conn()

    graph = await build_graph()
    # Determine gateway address from environment variables or use the default

    inputs = {"messages": [HumanMessage(content="Write a story about a cat")]}
    logger.info({"event": "invoking_graph", "inputs": inputs})
    result = graph.invoke(inputs)
    logger.info({"event": "final_result", "result": result})


# Main execution
if __name__ == "__main__":
    asyncio.run(main())
