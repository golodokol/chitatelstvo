# Quick deploy: git pull + restart api + quiz assets.
# Run: powershell -ExecutionPolicy Bypass -File scripts\deploy_quick.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root
. (Join-Path $PSScriptRoot "_deploy_helpers.ps1")

$cfg = Import-DeployEnv
$dir = $cfg.ProjectDir

Write-Host "Deploying to $($cfg.Host)..."
$assets = "/var/www/chitatelstvo-assets"
$cmd = "set -e; cd $dir; git pull origin main; docker compose restart api; mkdir -p $assets; cp docs/tilda-zero-main/chit-quiz.js docs/tilda-zero-main/chit-quiz.css $assets/; echo DEPLOY_OK"

Invoke-Remote -Cfg $cfg -Command $cmd
Write-Host "Done."
