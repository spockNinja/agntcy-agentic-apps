# remote_graphs

## Overview

This repository contains a Agent Protocol FastAPI application. It also includes examples of JSON-based logging, CORS configuration, and route tagging.

## Requirements

- Python 3.9+
- A virtual environment is recommended for isolating dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/brisacoder/remote_graphs/
   cd your-repo
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

The application uses a `.env` file for storing environment variables.

```bash
OPENAI_API_KEY=sk-<your key>
OPENAI_MODEL_NAME=gpt-4o
```

## Running the Application

You can run the application by executing:

```bash
python main.py
```

### Expected Console Output

On a successful run, you should see logs in your terminal similar to the snippet below. The exact timestamps, process IDs, and file paths will vary:

```plaintext
.\main.py
2025-03-03 12:06:25,242 - INFO - app - Logging is initialized. This should appear in the log file.
2025-03-03 12:06:25,243 - INFO - app - Starting FastAPI application...
2025-03-03 12:06:25,244 - INFO - root - .env file loaded from E:\Dropbox\GitHub\remote_graphs\.env
INFO:     Started server process [26904]
INFO:     Waiting for application startup.
2025-03-03 12:06:25,269 - INFO - root - Starting Remote Graphs App...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8123 (Press CTRL+C to quit)
```

This output confirms that:

1. Logging is properly initialized.
2. The server is listening on `0.0.0.0:8123`.
3. Your environment variables (like `.env file loaded`) are read.

## Logging

- **Format**: The application is configured to use JSON logging by default. Each log line provides a timestamp, log level, module name, and the message.
- **Location**: Logs typically go to stdout when running locally. If you configure a file handler or direct logs to a centralized logging solution, they can be written to a file (e.g., `logs/app.log`) or shipped to another service.
- **Customization**: You can change the log level (`info`, `debug`, etc.) or format by modifying environment variables or the logger configuration in your code. If you run in Docker or Kubernetes, ensure the logs are captured properly and aggregated where needed.

## API Endpoints

By default, the API documentation is available at:

```bash
http://0.0.0.0:8123/docs
```

(Adjust the host and port if you override them via environment variables.)

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and ensure tests pass.
4. Submit a pull request.
