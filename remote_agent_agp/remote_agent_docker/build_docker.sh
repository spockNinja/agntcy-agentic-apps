#!/bin/bash

# Default image name if none is provided
IMAGE_NAME=${1:-"agp_remote_agent"}

echo "Building Docker image: $IMAGE_NAME"

# Build the Docker image with the parent directory as context
docker build -t "$IMAGE_NAME" -f Dockerfile .. 

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image '$IMAGE_NAME' built successfully!"
else
  echo "Docker build failed!"
  exit 1
fi
