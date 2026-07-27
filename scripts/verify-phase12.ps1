param(
    [switch]$IncludeHeavyBuilds
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

function Assert-LastCommand {
    param([Parameter(Mandatory = $true)][string]$Name)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

function New-VerificationSecret {
    $bytes = New-Object byte[] 48
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
        return [Convert]::ToBase64String($bytes)
    }
    finally {
        $generator.Dispose()
    }
}

Push-Location $projectRoot
try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\verify-phase11.ps1"
    Assert-LastCommand "Phase 11 regression gate"

    $env:SECRET_KEY = New-VerificationSecret
    $env:JWT_SECRET_KEY = New-VerificationSecret
    try {
        & docker compose --env-file .env.server.example -f compose.server.yml config --quiet
        Assert-LastCommand "Server Compose validation"
    }
    finally {
        Remove-Item Env:\SECRET_KEY -ErrorAction SilentlyContinue
        Remove-Item Env:\JWT_SECRET_KEY -ErrorAction SilentlyContinue
    }

    if ($IncludeHeavyBuilds) {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\build-windows-release.ps1"
        Assert-LastCommand "Windows release build"
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\smoke-windows-release.ps1"
        Assert-LastCommand "Windows release smoke test"

        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\smoke-server-release.ps1"
        Assert-LastCommand "Docker server release smoke test"
    }
}
finally {
    Pop-Location
}

Write-Host "Phase 12 packaging and deployment verification passed."
