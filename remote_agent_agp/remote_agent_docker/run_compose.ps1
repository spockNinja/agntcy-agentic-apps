Write-Host "Pulling the latest AGP Gateway image..."
docker pull ghcr.io/agntcy/agp/gw:latest

Write-Host "Starting Docker Compose services..."

# Get the script directory (remote_agent_docker/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change directory to the project root (where docker-compose.yml is located)
Set-Location -Path "$scriptDir\.."

# Run Docker Compose
$process = Start-Process -NoNewWindow -PassThru -Wait -FilePath "docker-compose" -ArgumentList @("up", "-d")

# Check if the services started successfully
if ($process.ExitCode -eq 0) {
    Write-Host "Docker Compose services are running."
} else {
    Write-Host "Failed to start Docker Compose services."
    exit 1
}

# Change back to the original directory after execution
Set-Location -Path $scriptDir
