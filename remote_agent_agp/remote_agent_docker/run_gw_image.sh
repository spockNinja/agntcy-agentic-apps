#!/bin/bash

# Default password if not provided as an argument
PASSWORD=${1:-"dummy_password"}

# Set the environment variable for the password
export PASSWORD

# Resolve the config path and replace backslashes with forward slashes
CONFIG_PATH=$(realpath ./config/base/server-config.yaml)

# Run the Docker container
docker run -it \
    -e PASSWORD="$PASSWORD" \
    -v "$CONFIG_PATH:/config.yaml" \
    -p 46357:46357 \
    ghcr.io/agntcy/agp/gw:0.3.10 /gateway --config /config.yaml