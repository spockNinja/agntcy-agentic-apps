param (
    [string]$ImageName = "agp_remote_agent"  # Default to "agp_remote_agent" if not provided
)

Write-Host "Building Docker image: $ImageName"

# Build the Docker image with the parent directory as the context
$process = Start-Process -NoNewWindow -PassThru -Wait -FilePath "docker" -ArgumentList @(
    "build", "-t", $ImageName, "-f", "Dockerfile", ".."
)

# Check the exit code to determine if the build was successful
if ($process.ExitCode -eq 0) {
    Write-Host "Docker image '$ImageName' built successfully!"
} else {
    Write-Host "Docker build failed!"
    exit 1
}
