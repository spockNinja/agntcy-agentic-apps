param (
    [string]$ImageName = "agp_remote_agent"  # Default name if none is provided
)

# Set the path to the .env file (assume it's in the project root)
$EnvFilePath = "..\..\.env"

# Check if the .env file exists
if (-Not (Test-Path $EnvFilePath)) {
    Write-Host "Warning: .env file not found at $EnvFilePath. Environment variables may be missing."
}

Write-Host "Running Docker container for image: $ImageName"

# Run the Docker container with the .env file if it exists
$Command = @("run", "--env-file", $EnvFilePath, "-d", "--name", "agp_running_container", $ImageName)

# Execute Docker command
$process = Start-Process -NoNewWindow -PassThru -Wait -FilePath "docker" -ArgumentList $Command

# Check if the container started successfully
if ($process.ExitCode -eq 0) {
    Write-Host "Docker container '$ImageName' is running."
} else {
    Write-Host "Failed to start the Docker container."
    exit 1
}
