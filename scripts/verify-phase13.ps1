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

Push-Location $projectRoot
try {
    if ($IncludeHeavyBuilds) {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\verify-phase12.ps1" `
            -IncludeHeavyBuilds
    }
    else {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\verify-phase12.ps1"
    }
    Assert-LastCommand "Phase 12 regression gate"

    $python = ".\backend\.venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $python = "python"
    }
    & $python ".\scripts\validate_documentation.py"
    Assert-LastCommand "Documentation integrity validation"
}
finally {
    Pop-Location
}

Write-Host "Phase 13 complete-documentation verification passed."
