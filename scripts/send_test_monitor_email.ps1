# Отправить тестовое письмо мониторинга с сервера.
# Запуск: powershell -ExecutionPolicy Bypass -File scripts\send_test_monitor_email.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root
. (Join-Path $PSScriptRoot "_deploy_helpers.ps1")

$cfg = Import-DeployEnv
$dir = $cfg.ProjectDir

Write-Host "Sending test monitor email from $($cfg.Host)..."
$cmd = "cd $dir && git pull -q origin main && docker compose exec -T api python scripts/send_test_monitor_email.py"
Invoke-Remote -Cfg $cfg -Command $cmd -TimeoutSec 60
Write-Host "Done."
