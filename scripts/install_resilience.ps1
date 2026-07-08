# Установка пакета устойчивости на сервер: git pull + cron-мониторинг + smoke.
# Запуск: powershell -ExecutionPolicy Bypass -File scripts\install_resilience.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root
. (Join-Path $PSScriptRoot "_deploy_helpers.ps1")

$cfg = Import-DeployEnv
$dir = $cfg.ProjectDir

Write-Host "Installing resilience monitor on $($cfg.Host)..."
$cmd = @"
set -e
cd $dir
git pull origin main
mkdir -p /var/log/chitatelstvo /var/lib/chitatelstvo-monitor
bash scripts/resilience_install_monitor.sh
python3 scripts/post_deploy_check.py
echo RESILIENCE_OK
"@

Invoke-Remote -Cfg $cfg -Command $cmd -TimeoutSec 120
Write-Host "Done. Alerts go to MONITOR_ALERT_EMAIL from server .env"
