#!/bin/bash

# Default image name if none is provided
IMAGE_NAME=${1:-"agp_remote_agent"}

# Set the path to the .env file (assume it's in the project root)
ENV_FILE="../../.env"

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Warning: .env file not found at $ENV_FILE. Environment variables may be missing."
fi

echo "Running Docker container for image: $IMAGE_NAME"

# Run the Docker container with the .env file if it exists
docker run --env-file "$ENV_FILE" -d --name agp_running_container "$IMAGE_NAME"

# Check if the container started successfully
if [ $? -eq 0 ]; then
  echo "Docker container '$IMAGE_NAME' is running."
else
  echo "Failed to start the Docker container."
  exit 1
fi
