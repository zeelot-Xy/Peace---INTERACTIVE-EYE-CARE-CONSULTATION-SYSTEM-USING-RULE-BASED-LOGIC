$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$projectName = "eye-care-phase12-verification"
$port = 18080

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

function Wait-For-Health {
    $deadline = [DateTime]::UtcNow.AddSeconds(90)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $response = Invoke-RestMethod `
                -Uri "http://127.0.0.1:$port/api/v1/health" `
                -TimeoutSec 2
            if ($response.data.status -eq "healthy") {
                return
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    & docker compose -p $projectName -f compose.server.yml logs
    throw "Server container did not become healthy."
}

Push-Location $projectRoot
try {
    $env:SECRET_KEY = New-VerificationSecret
    $env:JWT_SECRET_KEY = New-VerificationSecret
    $env:PUBLIC_ORIGIN = "http://localhost:$port"
    $env:SERVER_PORT = "$port"
    try {
        & docker compose -p $projectName -f compose.server.yml up -d --build
        Assert-LastCommand "Server Docker build and start"
        Wait-For-Health
        & docker compose -p $projectName -f compose.server.yml exec -T eye-care `
            python -c "import sqlite3; c=sqlite3.connect('/data/eye-care.sqlite3'); c.execute('create table if not exists phase12_smoke(value text)'); c.execute('insert into phase12_smoke values (?)', ('retained',)); c.commit(); c.close()"
        Assert-LastCommand "Server persistence marker"
        & docker compose -p $projectName -f compose.server.yml restart eye-care
        Assert-LastCommand "Server restart"
        Wait-For-Health
        & docker compose -p $projectName -f compose.server.yml exec -T eye-care `
            python -c "import sqlite3; c=sqlite3.connect('/data/eye-care.sqlite3'); assert c.execute('select count(*) from phase12_smoke').fetchone()[0] == 1; c.close()"
        Assert-LastCommand "Server persistence verification"
    }
    finally {
        & docker compose -p $projectName -f compose.server.yml down -v
        Remove-Item Env:\SECRET_KEY -ErrorAction SilentlyContinue
        Remove-Item Env:\JWT_SECRET_KEY -ErrorAction SilentlyContinue
        Remove-Item Env:\PUBLIC_ORIGIN -ErrorAction SilentlyContinue
        Remove-Item Env:\SERVER_PORT -ErrorAction SilentlyContinue
    }
}
finally {
    Pop-Location
}

Write-Host "Docker server build, health, restart, and persistence smoke test passed."
