param (
    [SecureString]$Password = (ConvertTo-SecureString "dummy_password" -AsPlainText -Force)  # Default to secure "dummy_password" if not provided
)

# Convert SecureString to plain text for the environment variable
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
$PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

# Set the environment variable for the password
$env:PASSWORD = $PlainPassword

$ConfigPath = (Resolve-Path "${PWD}/config/base/server-config.yaml").Path -replace '\\', '/'
docker run -it `
    -e PASSWORD=$env:PASSWORD `
    -v "${ConfigPath}:/config.yaml" `
    -p 46357:46357 `
    ghcr.io/agntcy/agp/gw:0.3.10 /gateway --config /config.yaml


