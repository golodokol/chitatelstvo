param(
    [string]$Version = "20260621j",
    [string]$WrongBase = "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/"
)

$root = Split-Path $PSScriptRoot -Parent
$mapPath = Join-Path $root "docs\tilda-zero-main\tilda-images-map.json"
$litePath = Join-Path $root "docs\tilda-zero-main\00-tilda-lite.html"
$cssPath = Join-Path $root "docs\tilda-zero-main\chit-zero.css"

$map = Get-Content $mapPath -Raw -Encoding UTF8 | ConvertFrom-Json
$lite = Get-Content $litePath -Raw -Encoding UTF8
$css = Get-Content $cssPath -Raw -Encoding UTF8

foreach ($prop in $map.PSObject.Properties) {
    $name = $prop.Name
    $url = $prop.Value
    $lite = $lite.Replace($WrongBase + $name, $url)
    $lite = $lite.Replace($WrongBase + $name + "?v=20260621i", $url)
    $lite = $lite.Replace($WrongBase + $name + "?v=20260616g", $url)
    $css = $css.Replace($WrongBase + $name, $url)
}

$lite = $lite.Replace('var A="https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/"', 'var A="https://api.chitatelstvo.ru/assets/"')
$lite = $lite -replace "20260621i", $Version

$desktop = Join-Path $env:USERPROFILE "Desktop\TILDA-$Version.html"
Set-Content -Path $litePath -Value $lite -Encoding UTF8 -NoNewline
Set-Content -Path $cssPath -Value $css -Encoding UTF8 -NoNewline
Copy-Item $litePath $desktop -Force
Write-Host "OK $Version -> $desktop"
