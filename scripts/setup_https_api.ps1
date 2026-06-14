# HTTPS for api.chitatelstvo.ru (Timeweb VPS)
# 1) copy scripts\deploy.env.example scripts\deploy.env
# 2) set DEPLOY_PASSWORD and CERTBOT_EMAIL
# 3) .\scripts\setup_https_api.ps1

param(
    [string]$DeployHost = "",
    [string]$User = "root",
    [string]$ProjectDir = "/root/chitatelstvo"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$envFile = Join-Path $PSScriptRoot "deploy.env"
if (Test-Path $envFile) {
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
            Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
        }
    }
}

if (-not $DeployHost) { $DeployHost = $env:DEPLOY_HOST }
if (-not $DeployHost) { $DeployHost = "194.87.201.99" }
$User = if ($env:DEPLOY_USER) { $env:DEPLOY_USER } else { $User }
$password = $env:DEPLOY_PASSWORD
$email = $env:CERTBOT_EMAIL
$ProjectDir = if ($env:DEPLOY_PROJECT_DIR) { $env:DEPLOY_PROJECT_DIR } else { $ProjectDir }

if (-not $password) {
    throw "Missing DEPLOY_PASSWORD in scripts\deploy.env (copy from deploy.env.example)"
}
if (-not $email) {
    throw "Missing CERTBOT_EMAIL in scripts\deploy.env"
}

if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Installing Posh-SSH..."
    Install-Module Posh-SSH -Scope CurrentUser -Force -AllowClobber
}
Import-Module Posh-SSH

$sec = ConvertTo-SecureString $password -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($User, $sec)

Write-Host "Connecting to ${User}@${DeployHost}..."
$session = New-SSHSession -ComputerName $DeployHost -Credential $cred -AcceptKey -ErrorAction Stop

try {
    $localSh = Join-Path $PSScriptRoot "setup_https_api.sh"
    $remoteSh = "/tmp/setup_https_api.sh"
    Set-SCPItem -ComputerName $DeployHost -Credential $cred -Path $localSh -Destination $remoteSh -AcceptKey

    $nginxLocal = Join-Path $Root "deploy\nginx-chitatelstvo.conf"
    $remoteNginxDir = "$ProjectDir/deploy"
    Invoke-SSHCommand -SessionId $session.SessionId -Command "mkdir -p $remoteNginxDir" -TimeOut 60 | Out-Null
    if (Test-Path $nginxLocal) {
        Set-SCPItem -ComputerName $DeployHost -Credential $cred -Path $nginxLocal -Destination "$remoteNginxDir/nginx-chitatelstvo.conf" -AcceptKey
    }

    $cmd = "chmod +x $remoteSh && PROJECT_DIR=$ProjectDir CERTBOT_EMAIL=$email bash $remoteSh"
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $cmd -TimeOut 600
    if ($result.Output) { Write-Host $result.Output }
    if ($result.Error) { Write-Host $result.Error -ForegroundColor Yellow }
    if ($result.ExitStatus -ne 0) {
        throw "Remote script exit code $($result.ExitStatus)"
    }
    Write-Host "Done. Open https://api.chitatelstvo.ru/health"
}
finally {
    Remove-SSHSession -SessionId $session.SessionId | Out-Null
}
