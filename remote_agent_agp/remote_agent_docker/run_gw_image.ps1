param (
    [string]$Password = "dummy_password"  # Default to "dummy_password" if not provided
)

# Set the environment variable for the password
$env:PASSWORD = $Password

$ConfigPath = (Resolve-Path "${PWD}/config/base/server-config.yaml").Path -replace '\\', '/'
docker run -it `
    -e PASSWORD=$env:PASSWORD `
    -v "${ConfigPath}:/config.yaml" `
    -p 46357:46357 `
    ghcr.io/agntcy/agp/gw:0.3.6 /gateway --config /config.yaml


