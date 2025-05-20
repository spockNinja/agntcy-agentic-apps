#!/bin/bash

set -uo pipefail

# Environment variables (with defaults)
REPO="${REPO:-agntcy}"
HUB_ADDRESS="${HUB_ADDRESS:-https://hub.agntcy.org}"
DIRCTL_VERSION="${DIRCTL_VERSION:-v0.2.3}"
TEMP_DIRCTL="./dirctl" # Temporary binary location if downloaded

# Function to log messages and run a command, printing results
log_and_run() {
  local message="$1"
  local command="$2"

  local output
  output=$(eval "$command" 2>&1)
  local status=$?

  if [[ $status -eq 0 ]]; then
    echo -e "$message \033[1;32m✔\033[0m"
    if [[ -n "$output" ]]; then
      echo -e "output: \033[1;32m$output\033[0m"
    fi
  else
    echo -e "$message failed."
    echo -e "command: \033[1;34m$command\033[0m"
    if [[ -n "$output" ]]; then
      echo -e "output: \033[1;31m$output\033[0m"
    fi
  fi

  return $status
}

# Function to cleanup temporary dirctl binary
cleanup() {
  if [[ -f "$TEMP_DIRCTL" ]]; then
    log_and_run "Cleaning up temporary dirctl binary" "rm -f $TEMP_DIRCTL"
  fi
}
trap cleanup EXIT # Ensure cleanup runs on script exit

# Step 1: Ensure `dirctl` command is available
DIRCTL_CMD=""
if command -v dirctl &> /dev/null; then
  log_and_run "dirctl command found in PATH. Checking version" "true"
  INSTALLED_VERSION=$(dirctl version 2> /dev/null | grep "Application Version" | awk -F':' '{print $2}' | awk '{print $1}')

  if [[ "$INSTALLED_VERSION" == "$DIRCTL_VERSION" ]]; then
    log_and_run "dirctl version matches the required version ($DIRCTL_VERSION)" "true"
    DIRCTL_CMD="dirctl"
  else
    log_and_run "Installed dirctl version ($INSTALLED_VERSION) does not match required version ($DIRCTL_VERSION). Downloading correct version" "curl -L -o \"$TEMP_DIRCTL\" \"https://github.com/agntcy/dir/releases/download/${DIRCTL_VERSION}/dirctl-linux-amd64\" && chmod +x \"$TEMP_DIRCTL\""
    DIRCTL_CMD="$TEMP_DIRCTL"
  fi
else
  log_and_run "dirctl command not found. Downloading temporary dirctl binary" "curl -L -o \"$TEMP_DIRCTL\" \"https://github.com/agntcy/dir/releases/download/${DIRCTL_VERSION}/dirctl-linux-amd64\" && chmod +x \"$TEMP_DIRCTL\""
  DIRCTL_CMD="$TEMP_DIRCTL"
fi

# Step 2: Find all `agent.json` files
log_and_run "Searching for all agent.json files in the repository" "true"
AGENT_FILES=$(find . -name "agent.json")
if [[ -z "$AGENT_FILES" ]]; then
  log_and_run "No agent.json files found. Exiting" "true"
  exit 0
fi

# Prettier output for found files
echo -e "----------------------------------------"
for AGENT_FILE in $AGENT_FILES; do
  echo -e "\033[1;34m  $AGENT_FILE\033[0m"
done
echo -e "----------------------------------------"

# Step 3: Push each `agent.json` file to the hub
ALL_SUCCESS=0
for AGENT_PATH in $AGENT_FILES; do
  # Extract the agent name (parent directory of `agent.json`)
  AGENT_NAME=$(basename "$(dirname "$AGENT_PATH")")

  log_and_run "Pushing agent: $AGENT_NAME (path: $AGENT_PATH)" "$DIRCTL_CMD hub push \"$REPO/$AGENT_NAME\" \"$AGENT_PATH\" --server-address \"$HUB_ADDRESS\""
  PUSH_STATUS=$?

  if [[ $PUSH_STATUS -ne 0 ]]; then
    ALL_SUCCESS=1
  fi

  echo -e "----------------------------------------"
done

log_and_run "All agents have been processed" "true"

# Step 4: Exit with the overall success status
exit $ALL_SUCCESS
