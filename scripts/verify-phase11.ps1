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
        $pytestTemp = Join-Path ([System.IO.Path]::GetTempPath()) "eye-care-pytest-$PID"
        & ".\.venv\Scripts\python.exe" -m ruff check .
        Assert-LastCommand "Backend Ruff"
        & ".\.venv\Scripts\python.exe" -m pytest --basetemp $pytestTemp --cov=app --cov-report=term-missing --cov-fail-under=90
        Assert-LastCommand "Backend pytest and coverage"
        & ".\.venv\Scripts\python.exe" -m pip check
        Assert-LastCommand "Python dependency compatibility"
        & ".\.venv\Scripts\python.exe" -m pip_audit -r requirements.txt
        Assert-LastCommand "Python vulnerability audit"
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
        & node "..\scripts\check-npm-audit.mjs"
        Assert-LastCommand "Frontend production dependency audit"
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}

Write-Host "Phase 11 security and privacy verification passed."
