# Remote Agents with AGP

This repository demonstrates an agentic application that uses a remote agent with Agent Gateway Protocol. It has the following simple topology:

```bash
client <-----> Gateway <----> Server
```

- Client contains a Langgraph application
- Server is a FastAPI application that contains the remote agent
- Gateway is a message broker.

## Requirements

- Python 3.12+
- A virtual environment is recommended for isolating dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/agntcy/agentic-apps
   cd your-repo/remote_agent_agp
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Gateway

Clone the AGP repo and run the gateway

   ```bash
   git clone git@github.com:agntcy/agp.git
   cd agp/data-plane/testing
   task run:agp
   ```

#### Docker on Windows

```bash
git clone git@github.com:agntcy/agp.git
cd agp/data-plane
docker pull ghcr.io/agntcy/agp/gw:latest
```

```bash
docker run -it `
    -e PASSWORD=$env:PASSWORD `
    -v ${PWD}/gw/config/base/server-config.yaml:/config.yaml `
    -p 46357:46357 `
    ghcr.io/agntcy/agp/gw:0.3.3 /gateway --config /config.yaml
```

### Server

You can run the server app by executing from /agentic-apps/remote_agent_agp/app:

   ```bash
   python main.py
   ```

### Client

You can run the client app by executing from `agentic-apps/remote_agent_agp/client`:

   ```bash
   python agp.py
   ```

### Output

On a successful run you should an output similar to the following:

- client:

```bash
{"timestamp": "2025-03-12 07:13:42,912", "level": "INFO", "message": "{'event': 'final_result', 'result': {'messages': [HumanMessage(content='Write a story about a cat', additional_kwargs={}, response_metadata={}, id='c97f93dd-0c55-4109-862b-a34d6fd5aeba'), AIMessage(content='cats are wise', additional_kwargs={}, response_metadata={}, id='c79d1515-340e-43b6-b16c-9e04ae2c3058')]}}", "module": "agp", "function": "<module>", "line": 212, "logger": "graph_client", "pid": 20472}
```

- server:

```bash
{"timestamp": "2025-03-12 07:13:42,910", "level": "INFO", "message": "Received message{\"agent_id\": \"remote_agent\", \"output\": {\"messages\": [{\"role\": \"assistant\", \"content\": \"cats are wise\"}]}, \"model\": \"gpt-4o\", \"metadata\": {\"id\": \"d90cafe8-8f0c-4012-937f-df98356262cc\"}}, from agent <builtins.PyAgentSource object at 0x0000020A5BA2A5F0>", "module": "main", "function": "connect_to_gateway", "line": 184, "logger": "app", "pid": 5808}
```

- Gateway

```bash
2025-03-12T14:13:21.043726Z  INFO data-plane-gateway ThreadId(32) agp_service: running service
2025-03-12T14:13:34.776879Z  INFO data-plane-gateway ThreadId(04) agp_datapath::message_processing: new connection received from remote: (remote: Some(172.17.0.1:49344) - local: Some(172.17.0.2:46357))
2025-03-12T14:13:42.881719Z  INFO data-plane-gateway ThreadId(07) agp_datapath::message_processing: new connection received from remote: (remote: Some(172.17.0.1:46470) - local: Some(172.17.0.2:46357))
2025-03-12T14:13:42.954498Z  INFO data-plane-gateway ThreadId(04) agp_datapath::message_processing: end of stream conn_index=1
```