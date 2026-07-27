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
            -File ".\scripts\verify-phase13.ps1" `
            -IncludeHeavyBuilds
    }
    else {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\verify-phase13.ps1"
    }
    Assert-LastCommand "Phase 13 regression gate"

    $python = ".\backend\.venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $python = "python"
    }
    & $python ".\scripts\validate_final_handoff.py"
    Assert-LastCommand "Final handoff validation"
}
finally {
    Pop-Location
}

Write-Host "Phase 14 final audit and handoff verification passed."

