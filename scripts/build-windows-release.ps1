$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"
$frontendRoot = Join-Path $projectRoot "frontend"
$releaseRoot = Join-Path $projectRoot "release"
$staticRoot = Join-Path $backendRoot "static"

function Assert-LastCommand {
    param([Parameter(Mandatory = $true)][string]$Name)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

Push-Location $frontendRoot
try {
    $env:VITE_API_BASE_URL = "/api/v1"
    & npm.cmd run build
    Assert-LastCommand "Frontend production build"
}
finally {
    Remove-Item Env:\VITE_API_BASE_URL -ErrorAction SilentlyContinue
    Pop-Location
}

if (Test-Path $staticRoot) {
    Remove-Item -LiteralPath $staticRoot -Recurse -Force
}
Copy-Item -Path (Join-Path $frontendRoot "dist") -Destination $staticRoot -Recurse

Push-Location $backendRoot
try {
    & ".\.venv\Scripts\python.exe" -m pip install -r requirements-packaging.txt
    Assert-LastCommand "Packaging dependencies"
    & ".\.venv\Scripts\python.exe" -m PyInstaller `
        --clean `
        --noconfirm `
        (Join-Path $projectRoot "packaging\windows\eye-care.spec")
    Assert-LastCommand "PyInstaller"
}
finally {
    Pop-Location
}

if (Test-Path $releaseRoot) {
    Remove-Item -LiteralPath $releaseRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseRoot | Out-Null
$distribution = Join-Path $backendRoot "dist\EyeCareConsultation"
Copy-Item -Path $distribution -Destination $releaseRoot -Recurse
Copy-Item -Path (Join-Path $projectRoot "packaging\windows\Backup Data.cmd") `
    -Destination (Join-Path $releaseRoot "EyeCareConsultation")
Copy-Item -Path (Join-Path $projectRoot "packaging\windows\Diagnostics.cmd") `
    -Destination (Join-Path $releaseRoot "EyeCareConsultation")
Copy-Item -Path (Join-Path $projectRoot "packaging\windows\Reset Demo Data.cmd") `
    -Destination (Join-Path $releaseRoot "EyeCareConsultation")
Copy-Item -Path (Join-Path $projectRoot "packaging\windows\Create Administrator.cmd") `
    -Destination (Join-Path $releaseRoot "EyeCareConsultation")
Copy-Item -Path (Join-Path $projectRoot "docs\windows-release.md") `
    -Destination (Join-Path $releaseRoot "EyeCareConsultation\README.md")

$archive = Join-Path $releaseRoot "EyeCareConsultation-Windows.zip"
Compress-Archive -Path (Join-Path $releaseRoot "EyeCareConsultation") -DestinationPath $archive
$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $archive
"$($hash.Hash.ToLowerInvariant())  $($hash.Path | Split-Path -Leaf)" |
    Set-Content -Encoding ascii (Join-Path $releaseRoot "SHA256SUMS.txt")

Write-Host "Windows release created at $archive"
