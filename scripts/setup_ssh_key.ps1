# One-time SSH key setup for deploy scripts.
# Run: powershell -ExecutionPolicy Bypass -File scripts\setup_ssh_key.ps1

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_deploy_helpers.ps1")

$cfg = Import-DeployEnv
$keyPub = (Get-Content "$($cfg.KeyPath).pub" -Raw).Trim()

if (-not $cfg.Password) {
    throw "Set DEPLOY_PASSWORD in scripts\deploy.env"
}

Write-Host "Installing SSH key on $($cfg.Host)..."
$cmd = "set -e; mkdir -p ~/.ssh; chmod 700 ~/.ssh; grep -qxF '$keyPub' ~/.ssh/authorized_keys 2>/dev/null || echo '$keyPub' >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys; echo KEY_INSTALLED"

Invoke-Remote -Cfg $cfg -Command $cmd -UsePassword

if (Test-DeployKey -Cfg $cfg) {
    Write-Host "OK: key works. Next run: scripts\deploy_quick.bat"
} else {
    throw "Key was added but login failed. Check password in deploy.env"
}
