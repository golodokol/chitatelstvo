# Диагностика SMTP на сервере (без пароля).
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_deploy_helpers.ps1")
$cfg = Import-DeployEnv
$dir = $cfg.ProjectDir
$cmd = "cd $dir && git pull -q origin main && docker compose exec -T api python scripts/_smtp_diag.py"
Invoke-Remote -Cfg $cfg -Command $cmd -TimeoutSec 45
