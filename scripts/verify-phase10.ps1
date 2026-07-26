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
    & git diff --check
    Assert-LastCommand "Git whitespace check"

    Push-Location "backend"
    try {
        & ".\.venv\Scripts\python.exe" -m ruff check .
        Assert-LastCommand "Backend Ruff"
        & ".\.venv\Scripts\python.exe" -m pytest --cov=app --cov-report=term-missing --cov-fail-under=90
        Assert-LastCommand "Backend pytest and coverage"
    }
    finally {
        Pop-Location
    }

    Push-Location "frontend"
    try {
        & npm.cmd run lint
        Assert-LastCommand "Frontend ESLint"
        & npm.cmd test
        Assert-LastCommand "Frontend Vitest"
        & npm.cmd run build
        Assert-LastCommand "Frontend production build"
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}

Write-Host "Phase 10 verification passed."
