# Коммит и push одной командой. Использование:
#   .\commit-push.bat "Краткое сообщение коммита"
#   .\commit-push.bat "Заголовок" "Подробное описание (опционально)"
#
# Автор коммита: scripts\git-author.env (скопируйте из git-author.env.example)

param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$Message,

    [Parameter(Position = 1)]
    [string]$Body = ""
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$GitConfigArgs = @()
$authorFile = Join-Path $PSScriptRoot "git-author.env"
if (Test-Path $authorFile) {
    Get-Content $authorFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            if ($key -eq "GIT_AUTHOR_NAME") { $GitConfigArgs += "-c", "user.name=$val" }
            if ($key -eq "GIT_AUTHOR_EMAIL") { $GitConfigArgs += "-c", "user.email=$val" }
        }
    }
}

function Run-Git {
    param([Parameter(Mandatory = $true)][string[]]$Args)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $out = & git @GitConfigArgs @Args 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    if ($code -ne 0) {
        if ($out) { Write-Host $out }
        exit $code
    }
    return ,$out
}

$porcelain = @(Run-Git @("status", "--porcelain"))
$hasChanges = $porcelain.Count -gt 0

if ($hasChanges) {
    Run-Git @("add", "-A") | Out-Null
    if ($Body) {
        Run-Git @("commit", "-m", $Message, "-m", $Body) | Out-Null
    } else {
        Run-Git @("commit", "-m", $Message) | Out-Null
    }
    Write-Host "Committed."
} else {
    $branch = (Run-Git @("branch", "--show-current")).Trim()
    $ahead = (Run-Git @("rev-list", "--count", "origin/$branch..HEAD")).Trim()
    if ($ahead -eq "0") {
        Write-Host "Nothing to commit. Branch is up to date with origin/$branch."
        exit 0
    }
    Write-Host "No local changes. Pushing $ahead commit(s)..."
}

$branch = (Run-Git @("branch", "--show-current")).Trim()
Run-Git @("push", "origin", $branch) | Out-Null
Write-Host "Pushed to origin/$branch"
