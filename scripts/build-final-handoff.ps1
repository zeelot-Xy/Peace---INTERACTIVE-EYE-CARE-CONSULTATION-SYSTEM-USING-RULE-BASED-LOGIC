param(
    [switch]$IncludeHeavyBuilds,
    [switch]$ReuseVerifiedWindowsArchive
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$releaseRoot = Join-Path $projectRoot "release"
$handoffRoot = Join-Path $releaseRoot "Final-Handoff"

function Assert-LastCommand {
    param([Parameter(Mandatory = $true)][string]$Name)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

function Write-Checksums {
    param(
        [Parameter(Mandatory = $true)][string]$Directory,
        [Parameter(Mandatory = $true)][string]$Output
    )
    $lines = Get-ChildItem -LiteralPath $Directory -File |
        Where-Object { $_.FullName -ne $Output } |
        Sort-Object Name |
        ForEach-Object {
            $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName
            "$($hash.Hash.ToLowerInvariant())  $($_.Name)"
        }
    $lines | Set-Content -Encoding ascii -LiteralPath $Output
}

Push-Location $projectRoot
try {
    & git diff --check
    Assert-LastCommand "Git whitespace check"

    if ($IncludeHeavyBuilds) {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\verify-phase14.ps1" `
            -IncludeHeavyBuilds
        Assert-LastCommand "Heavy final verification"
    }
    else {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\verify-phase14.ps1"
        Assert-LastCommand "Final verification"
    }

    $windowsArchive = Join-Path $releaseRoot "EyeCareConsultation-Windows.zip"
    if (-not $ReuseVerifiedWindowsArchive -or -not (Test-Path $windowsArchive)) {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File ".\scripts\build-windows-release.ps1"
        Assert-LastCommand "Windows release build"
        $windowsArchive = Join-Path $releaseRoot "EyeCareConsultation-Windows.zip"
    }

    if (Test-Path $handoffRoot) {
        Remove-Item -LiteralPath $handoffRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $handoffRoot | Out-Null

    $sourceArchive = Join-Path $handoffRoot "EyeCareConsultation-Source.zip"
    & git archive --format=zip --output=$sourceArchive HEAD
    Assert-LastCommand "Source archive"

    $gitBundle = Join-Path $handoffRoot "EyeCareConsultation-Git.bundle"
    & git bundle create $gitBundle --all
    Assert-LastCommand "Git bundle creation"
    & git bundle verify $gitBundle
    Assert-LastCommand "Git bundle verification"

    & git log --date=iso-strict `
        --pretty=format:"%H%x09%ad%x09%an%x09%s" |
        Set-Content -Encoding utf8 (Join-Path $handoffRoot "Git-History.txt")
    Assert-LastCommand "Git history export"

    Copy-Item -LiteralPath $windowsArchive `
        -Destination (Join-Path $handoffRoot "EyeCareConsultation-Windows.zip")
    Copy-Item -LiteralPath (Join-Path $projectRoot "docs\client-handoff.md") `
        -Destination (Join-Path $handoffRoot "HANDOFF-README.md")

    $metadata = [ordered]@{
        project = "Interactive Eye Care Consultation System Using Rule-Based Logic"
        release_commit = (& git rev-parse HEAD).Trim()
        branch = (& git branch --show-current).Trim()
        created_at_utc = [DateTime]::UtcNow.ToString("o")
        clinical_status = "Educational academic prototype; not clinically validated"
        artifact_count = 5
    }
    $metadata | ConvertTo-Json |
        Set-Content -Encoding utf8 (Join-Path $handoffRoot "Release-Metadata.json")

    $checksums = Join-Path $handoffRoot "SHA256SUMS.txt"
    Write-Checksums -Directory $handoffRoot -Output $checksums

    $handoffArchive = Join-Path $releaseRoot "EyeCareConsultation-Final-Handoff.zip"
    if (Test-Path $handoffArchive) {
        Remove-Item -LiteralPath $handoffArchive -Force
    }
    Compress-Archive -Path (Join-Path $handoffRoot "*") -DestinationPath $handoffArchive

    $handoffHash = Get-FileHash -Algorithm SHA256 -LiteralPath $handoffArchive
    "$($handoffHash.Hash.ToLowerInvariant())  $($handoffHash.Path | Split-Path -Leaf)" |
        Set-Content -Encoding ascii (Join-Path $releaseRoot "FINAL-SHA256SUMS.txt")
}
finally {
    Pop-Location
}

Write-Host "Final handoff created at $handoffArchive"

