# remote_graphs

## Overview

This repository contains a Agent Gateway Protocol application.

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
