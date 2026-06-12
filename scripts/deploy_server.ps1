# Удалённая настройка сервера: git + бэкапы Postgres.
# Использование:
#   1) copy scripts\deploy.env.example scripts\deploy.env
#   2) укажите DEPLOY_PASSWORD (пароль root Timeweb)
#   3) .\scripts\deploy_server.ps1

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
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            Set-Item -Path "env:$key" -Value $val
        }
    }
}

if (-not $DeployHost) { $DeployHost = $env:DEPLOY_HOST }
if (-not $DeployHost) { $DeployHost = "194.87.201.99" }
$User = if ($env:DEPLOY_USER) { $env:DEPLOY_USER } else { $User }
$password = $env:DEPLOY_PASSWORD
$ProjectDir = if ($env:DEPLOY_PROJECT_DIR) { $env:DEPLOY_PROJECT_DIR } else { $ProjectDir }

if (-not $password) {
    Write-Error "Укажите DEPLOY_PASSWORD в scripts\deploy.env (скопируйте из deploy.env.example)"
}

if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Устанавливаю Posh-SSH..."
    Install-Module Posh-SSH -Scope CurrentUser -Force -AllowClobber
}

Import-Module Posh-SSH

$sec = ConvertTo-SecureString $password -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($User, $sec)

Write-Host "Подключение к ${User}@${DeployHost}..."
$session = New-SSHSession -ComputerName $DeployHost -Credential $cred -AcceptKey -ErrorAction Stop

try {
    $localSetup = Join-Path $PSScriptRoot "setup_git_and_backup.sh"
    $remoteSetup = "/tmp/setup_git_and_backup.sh"
    Set-SCPItem -ComputerName $DeployHost -Credential $cred -Path $localSetup -Destination $remoteSetup -AcceptKey

    $cmd = "chmod +x $remoteSetup && PROJECT_DIR=$ProjectDir bash $remoteSetup"
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $cmd -TimeOut 300
    if ($result.Output) { Write-Host $result.Output }
    if ($result.Error) { Write-Host $result.Error -ForegroundColor Yellow }
    if ($result.ExitStatus -ne 0) {
        throw "Команда на сервере завершилась с кодом $($result.ExitStatus)"
    }
    Write-Host "Готово: сервер настроен."
}
finally {
    Remove-SSHSession -SessionId $session.SessionId | Out-Null
}
