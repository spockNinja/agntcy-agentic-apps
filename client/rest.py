# Description: This file contains a sample graph client that makes a stateless request to the Remote Graph Server.
# Usage: python3 client/rest.py

import json
import logging
import traceback
import os
from typing import TypedDict, List, Dict

import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, END, StateGraph, CompiledGraph

# Log file path
LOG_FILE = "graph_client.log"

# Remove existing log file before a new run
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)


# Configure structured JSON logging
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logs."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["error"] = {
                "type": str(record.exc_info[0]),
                "message": str(record.exc_info[1]),
                "stack_trace": traceback.format_exc(),
            }
        return json.dumps(log_data)


# Set up logger with both console and file handlers
logger = logging.getLogger("json_logger")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# URL for the Remote Graph Server /runs endpoint
REMOTE_SERVER_URL = "http://127.0.0.1:8123/runs"


# Define the graph state
class GraphState(TypedDict):
    """Represents the state of the graph, containing a list of messages."""

    messages: List[BaseMessage]


# Graph node that makes a stateless request to the Remote Graph Server
def node_remote_request_stateless(state: GraphState) -> Dict[str, List[BaseMessage]]:
    """
    Sends a stateless request to the Remote Graph Server.

    Args:
        state (GraphState): The current graph state containing messages.

    Returns:
        Dict[str, List[BaseMessage]]: Updated state containing server response or error message.
    """
    if not state["messages"]:
        logger.error(json.dumps({"error": "GraphState contains no messages"}))
        return {"messages": [HumanMessage(content="Error: No messages in state")]}

    # Extract the latest user query
    query = state["messages"][-1].content
    logger.info(json.dumps({"event": "sending_request", "query": query}))

    # Request headers
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Payload for the request
    payload = json.dumps({"input": [{"query": query}]})

    # Use a session for efficiency
    session = requests.Session()

    try:
        response = session.post(
            REMOTE_SERVER_URL, headers=headers, data=payload, timeout=10
        )

        # Raise exception for HTTP errors
        response.raise_for_status()

        # Parse response as JSON
        response_data = response.json()
        logger.info(
            json.dumps(
                {
                    "event": "received_response",
                    "status_code": response.status_code,
                    "response_body": response_data,
                }
            )
        )

        return {"messages": [HumanMessage(content=json.dumps(response_data))]}

    except (Timeout, ConnectionError) as conn_err:
        error_msg = {
            "error": "Connection timeout or failure",
            "exception": str(conn_err),
        }
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    except HTTPError as http_err:
        error_msg = {
            "error": "HTTP request failed",
            "status_code": response.status_code,
            "exception": str(http_err),
        }
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    except RequestException as req_err:
        error_msg = {"error": "Request failed", "exception": str(req_err)}
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    except json.JSONDecodeError as json_err:
        error_msg = {"error": "Invalid JSON response", "exception": str(json_err)}
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    except Exception as e:
        error_msg = {
            "error": "Unexpected failure",
            "exception": str(e),
            "stack_trace": traceback.format_exc(),
        }
        logger.error(json.dumps(error_msg))
        return {"messages": [HumanMessage(content=json.dumps(error_msg))]}

    finally:
        session.close()


# Build the state graph
def build_graph() -> CompiledGraph:
    """
    Constructs the state graph for handling requests.

    Returns:
        StateGraph: A compiled LangGraph state graph.
    """
    builder = StateGraph(GraphState)
    builder.add_node("node_remote_request_stateless", node_remote_request_stateless)
    builder.add_edge(START, "node_remote_request_stateless")
    builder.add_edge("node_remote_request_stateless", END)
    return builder.compile()


# Main execution
if __name__ == "__main__":
    # Construct the graph
    graph = build_graph()

    # Define input state
    inputs = {"messages": [HumanMessage(content="Write a story about a cat")]}

    # Invoke the graph
    logger.info(json.dumps({"event": "invoking_graph", "inputs": inputs}))
    result = graph.invoke(inputs)

    # Log final response
    logger.info(json.dumps({"event": "final_result", "result": result}))
