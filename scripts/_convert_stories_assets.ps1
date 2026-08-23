Add-Type -AssemblyName System.Drawing
$root = Join-Path $PSScriptRoot "..\static\early\stories" | Resolve-Path

function Convert-ToJpg {
    param([string]$SrcName, [string]$DstName)
    $src = Join-Path $root $SrcName
    if (-not (Test-Path $src)) {
        Write-Host "MISSING $SrcName"
        return
    }
    $dst = Join-Path $root $DstName
    $img = [System.Drawing.Image]::FromFile($src)
    $bmp = New-Object System.Drawing.Bitmap $img.Width, $img.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::FromArgb(255, 252, 247))
    $g.DrawImage($img, 0, 0, $img.Width, $img.Height)
    $g.Dispose()
    $img.Dispose()
    $enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
    $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
    $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 92L
    $bmp.Save($dst, $enc, $ep)
    $bmp.Dispose()
    $len = (Get-Item $dst).Length
    Write-Host "OK $DstName $len"
}

foreach ($n in 1..5) {
    $id = "{0:D2}" -f $n
    Convert-ToJpg "book-home-$id.PNG" "book-home-$id.jpg"
}
Convert-ToJpg "scene-night-sleep-2.PNG" "scene-night-sleep.jpg"
