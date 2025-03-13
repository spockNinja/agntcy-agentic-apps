#!/bin/bash

# Navigate to the directory where docker-compose.yml is located
cd "$(dirname "$0")/.."

echo "Pulling the latest AGP Gateway image..."
docker pull ghcr.io/agntcy/agp/gw:latest

echo "Starting Docker Compose services..."
docker-compose up -d

# Check if the services started successfully
if [ $? -eq 0 ]; then
  echo "Docker Compose services are running."
else
  echo "Failed to start Docker Compose services."
  exit 1
fi
