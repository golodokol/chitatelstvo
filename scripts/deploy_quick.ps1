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
$cmd = "set -e; cd $dir; git pull origin main; cat db/migrations/002_tale_ratings.sql | docker compose exec -T postgres psql -U literary -d literary_school; cat db/migrations/003_chest_claims.sql | docker compose exec -T postgres psql -U literary -d literary_school; cat db/migrations/004_enrollment_promo_code.sql | docker compose exec -T postgres psql -U literary -d literary_school; docker compose up -d --build api worker; mkdir -p $assets; cp docs/tilda-zero-main/chit-quiz.js docs/tilda-zero-main/chit-quiz.css docs/tilda-zero-main/chit-zero.js docs/tilda-zero-main/chit-zero.css docs/tilda-zero-main/chit-pay-page.js $assets/; cp docs/images/gamify-badge-* $assets/ 2>/dev/null || true; bash scripts/rename_assets_lower.sh; echo DEPLOY_OK"

Invoke-Remote -Cfg $cfg -Command $cmd
Write-Host "Done."
