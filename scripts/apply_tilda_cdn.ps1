# Заменяет URL картинок api.chitatelstvo.ru → Tilda CDN.
# CSS/JS и order-config.json остаются на API.
param(
    [string]$TildaBase = "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/",
    [string]$Version = "20260621h",
    [string]$ApiBase = "https://api.chitatelstvo.ru/assets/"
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$dir = Join-Path $root "docs\tilda-zero-main"

if (-not $TildaBase.EndsWith("/")) { $TildaBase += "/" }

function Restore-ApiAssets([string]$text) {
    $keep = @("chit-zero.css", "chit-zero.js", "order-config.json", "chit-quiz.css", "chit-quiz.js", "chit-pay-page.js")
    foreach ($name in $keep) {
        $text = $text.Replace($TildaBase + $name, $ApiBase + $name)
    }
    return $text
}

function Switch-ToTildaCdn([string]$text) {
    $text = $text.Replace($ApiBase, $TildaBase)
    return Restore-ApiAssets $text
}

$litePath = Join-Path $dir "00-tilda-lite.html"
$cssPath = Join-Path $dir "chit-zero.css"
$jsPath = Join-Path $dir "chit-zero.js"

$lite = Get-Content $litePath -Raw -Encoding UTF8
$lite = Switch-ToTildaCdn $lite
$lite = $lite -replace "20260621g", $Version
$lite = $lite -replace "<!-- CHIT VERSION [^·]+·", "<!-- CHIT VERSION $Version ·"

$css = Get-Content $cssPath -Raw -Encoding UTF8
$css = Switch-ToTildaCdn $css

$js = Get-Content $jsPath -Raw -Encoding UTF8
$js = $js.Replace('window.CHIT_IMG_BASE = "https://api.chitatelstvo.ru/assets/";', "window.CHIT_IMG_BASE = `"$TildaBase`";")

$outLite = Join-Path $dir "00-tilda-lite-tildacdn.html"
$desktop = Join-Path $env:USERPROFILE "Desktop\TILDA-$Version.html"

Set-Content -Path $outLite -Value $lite -Encoding UTF8 -NoNewline
Set-Content -Path $litePath -Value $lite -Encoding UTF8 -NoNewline
Set-Content -Path $cssPath -Value $css -Encoding UTF8 -NoNewline
Set-Content -Path $jsPath -Value $js -Encoding UTF8 -NoNewline
Copy-Item $outLite $desktop -Force

Write-Host "OK: $Version"
Write-Host "  HTML: $outLite"
Write-Host "  Desktop: $desktop"
Write-Host "  Tilda base: $TildaBase"
Write-Host ""
Write-Host "Next: deploy CSS+JS, paste HTML into Zero Block, publish."
