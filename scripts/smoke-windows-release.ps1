$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$executable = Join-Path $projectRoot "release\EyeCareConsultation\EyeCareConsultation.exe"
$dataRoot = Join-Path ([System.IO.Path]::GetTempPath()) "eye-care-release-smoke-$PID"
$port = 18765
$baseUrl = "http://127.0.0.1:$port"
$webSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession

if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Packaged executable is missing: $executable"
}

function Start-And-Verify {
    param([scriptblock]$DuringRun)
    $process = Start-Process `
        -FilePath $executable `
        -ArgumentList @("--data-directory", $dataRoot, "run", "--port", $port, "--no-browser") `
        -WindowStyle Hidden `
        -PassThru
    try {
        $deadline = [DateTime]::UtcNow.AddSeconds(45)
        $ready = $false
        while ([DateTime]::UtcNow -lt $deadline) {
            try {
                $response = Invoke-RestMethod `
                    -Uri "$baseUrl/api/v1/health" `
                    -TimeoutSec 2
                if ($response.data.status -eq "healthy") {
                    $ready = $true
                    break
                }
            }
            catch {
                Start-Sleep -Milliseconds 300
            }
        }
        if (-not $ready) {
            throw "Packaged health endpoint did not become ready."
        }
        if ($DuringRun) {
            & $DuringRun
        }
    }
    finally {
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit()
        }
    }
}

try {
    Start-And-Verify {
        $landing = Invoke-WebRequest `
            -Uri $baseUrl `
            -WebSession $webSession `
            -UseBasicParsing
        if ($landing.StatusCode -ne 200) {
            throw "Packaged frontend was not served."
        }
        $registration = @{
            full_name = "Phase Twelve Example"
            email = "phase12@example.test"
            password = "correct horse battery staple"
        } | ConvertTo-Json
        $registered = Invoke-RestMethod `
            -Method Post `
            -Uri "$baseUrl/api/v1/auth/register" `
            -ContentType "application/json" `
            -Body $registration `
            -WebSession $webSession
        if ($registered.data.user.email -ne "phase12@example.test") {
            throw "Packaged registration response was unexpected."
        }
        $csrf = $webSession.Cookies.GetCookies(
            [Uri]"$baseUrl/api/v1/consultations"
        )["csrf_access_token"].Value
        $consultation = Invoke-RestMethod `
            -Method Post `
            -Uri "$baseUrl/api/v1/consultations" `
            -Headers @{"X-CSRF-TOKEN" = $csrf} `
            -ContentType "application/json" `
            -Body "{}" `
            -WebSession $webSession
        if (-not $consultation.data.consultation.id) {
            throw "Packaged consultation creation failed."
        }
    }
    $database = Join-Path $dataRoot "data\eye-care.sqlite3"
    $secrets = Join-Path $dataRoot "config\installation-secrets.json"
    if (-not (Test-Path -LiteralPath $database -PathType Leaf)) {
        throw "First launch did not create the database."
    }
    if (-not (Test-Path -LiteralPath $secrets -PathType Leaf)) {
        throw "First launch did not create installation secrets."
    }
    $secretHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $secrets).Hash
    Start-And-Verify {
        $profile = Invoke-RestMethod `
            -Uri "$baseUrl/api/v1/users/me" `
            -WebSession $webSession
        if ($profile.data.user.email -ne "phase12@example.test") {
            throw "Packaged authentication or persisted user data failed after restart."
        }
    }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $secrets).Hash -ne $secretHash) {
        throw "Installation secrets changed after restart."
    }
}
finally {
    $resolvedTemp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    $resolvedData = [System.IO.Path]::GetFullPath($dataRoot)
    if ($resolvedData.StartsWith($resolvedTemp, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedData -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Windows release first-run and restart smoke test passed."
