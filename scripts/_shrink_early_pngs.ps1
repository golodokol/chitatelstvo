Add-Type -AssemblyName System.Drawing

$root = Split-Path $PSScriptRoot -Parent
if (-not $root) { $root = (Get-Location).Path }
$early = Join-Path $root "static\early"

function Get-JpegCodec {
  [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
    Where-Object { $_.MimeType -eq "image/jpeg" } |
    Select-Object -First 1
}

function Save-Jpeg($bmp, $path, $quality) {
  $codec = Get-JpegCodec
  $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
  $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter (
    [System.Drawing.Imaging.Encoder]::Quality, [int64]$quality)
  $tmp = "$path.tmp"
  $bmp.Save($tmp, $codec, $ep)
  $ep.Dispose()
  Move-Item -Force $tmp $path
}

function Save-Png($bmp, $path) {
  $tmp = "$path.tmp"
  $bmp.Save($tmp, [System.Drawing.Imaging.ImageFormat]::Png)
  Move-Item -Force $tmp $path
}

function Resize-ImageFile {
  param(
    [string]$Path,
    [int]$MaxSide,
    [switch]$Jpeg,
    [int]$Quality = 80
  )
  $img = [System.Drawing.Image]::FromFile($Path)
  try {
    $w = $img.Width
    $h = $img.Height
    $scale = [Math]::Min(1.0, $MaxSide / [Math]::Max($w, $h))
    $nw = [Math]::Max(1, [int][Math]::Round($w * $scale))
    $nh = [Math]::Max(1, [int][Math]::Round($h * $scale))
    $fmt = [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    if ($Jpeg) { $fmt = [System.Drawing.Imaging.PixelFormat]::Format24bppRgb }
    $bmp = New-Object System.Drawing.Bitmap $nw, $nh, $fmt
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
      $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
      $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
      $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
      if ($Jpeg) {
        $g.Clear([System.Drawing.Color]::FromArgb(255, 255, 250, 242))
      }
      $g.DrawImage($img, 0, 0, $nw, $nh)
    } finally { $g.Dispose() }

    $before = (Get-Item $Path).Length
    $img.Dispose()
    $img = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    if ($Jpeg) {
      $out = [IO.Path]::ChangeExtension($Path, ".jpg")
      Save-Jpeg $bmp $out $Quality
    } else {
      Save-Png $bmp $Path
      $out = $Path
    }
    $bmp.Dispose()
    $after = (Get-Item $out).Length
    "{0,5}x{1,-5} {2,5}KB -> {3,4}x{4,-4} {5,4}KB  {6}" -f $w, $h, [int]($before/1KB), $nw, $nh, [int]($after/1KB), ($out.Substring($early.Length+1))
  } finally {
    if ($img) { $img.Dispose() }
  }
}

$jpegCodec = Get-JpegCodec
if (-not $jpegCodec) { throw "No JPEG codec" }

Get-ChildItem -Path $early -Recurse -Filter *.png | ForEach-Object {
  $rel = $_.FullName.Substring($early.Length + 1)
  $name = $_.Name
  if ($name -like "scene-*.png") {
    Resize-ImageFile -Path $_.FullName -MaxSide 1280 -Jpeg -Quality 78
  } elseif ($rel -like "slovik\*") {
    Resize-ImageFile -Path $_.FullName -MaxSide 480
  } elseif ($name -like "letter-a-*") {
    Resize-ImageFile -Path $_.FullName -MaxSide 720
  } elseif ($name -eq "spark.png") {
    Resize-ImageFile -Path $_.FullName -MaxSide 256
  } else {
    Resize-ImageFile -Path $_.FullName -MaxSide 400
  }
}
