# Shared helpers for remote deploy scripts.

function Import-DeployEnv {
    param([string]$ScriptRoot = $PSScriptRoot)
    $envFile = Join-Path $ScriptRoot "deploy.env"
    if (-not (Test-Path $envFile)) {
        throw "Create scripts\deploy.env from deploy.env.example"
    }
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
            Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
        }
    }
    @{
        Host       = if ($env:DEPLOY_HOST) { $env:DEPLOY_HOST } else { "194.87.201.99" }
        User       = if ($env:DEPLOY_USER) { $env:DEPLOY_USER } else { "root" }
        Password   = $env:DEPLOY_PASSWORD
        ProjectDir = if ($env:DEPLOY_PROJECT_DIR) { $env:DEPLOY_PROJECT_DIR } else { "/root/chitatelstvo" }
        KeyPath    = Join-Path $env:USERPROFILE ".ssh\chitatelstvo_deploy"
    }
}

function Ensure-PoshSSH {
    if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
        Write-Host "Installing Posh-SSH..."
        Install-Module Posh-SSH -Scope CurrentUser -Force -AllowClobber
    }
    Import-Module Posh-SSH
}

function Test-DeployKey {
    param([hashtable]$Cfg)
    if (-not (Test-Path $Cfg.KeyPath)) { return $false }
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    try {
        $out = & ssh -i $Cfg.KeyPath -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new `
            "$($Cfg.User)@$($Cfg.Host)" "echo KEY_OK" 2>$null
        return ($LASTEXITCODE -eq 0 -and ($out -join "`n") -match "KEY_OK")
    }
    finally {
        $ErrorActionPreference = $prev
    }
}

function Invoke-Remote {
    param(
        [hashtable]$Cfg,
        [string]$Command,
        [int]$TimeoutSec = 600,
        [switch]$UsePassword
    )

    if (-not $UsePassword -and (Test-DeployKey -Cfg $Cfg)) {
        Write-Host "SSH key: $($Cfg.User)@$($Cfg.Host)"
        $prev = $ErrorActionPreference
        $ErrorActionPreference = "Stop"
        try {
            & ssh -i $Cfg.KeyPath -o BatchMode=yes -o ConnectTimeout=$TimeoutSec `
                -o StrictHostKeyChecking=accept-new "$($Cfg.User)@$($Cfg.Host)" $Command
            if ($LASTEXITCODE -ne 0) {
                throw "Remote command failed with exit code $LASTEXITCODE"
            }
        }
        finally {
            $ErrorActionPreference = $prev
        }
        return
    }

    if (-not $Cfg.Password) {
        throw "SSH key not configured. Run: scripts\setup_ssh_key.bat"
    }

    Ensure-PoshSSH
    Write-Host "SSH password: $($Cfg.User)@$($Cfg.Host)"
    $sec = ConvertTo-SecureString $Cfg.Password -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ($Cfg.User, $sec)
    $session = New-SSHSession -ComputerName $Cfg.Host -Credential $cred -AcceptKey -ErrorAction Stop
    try {
        $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $Command -TimeOut $TimeoutSec
        if ($result.Output) { Write-Host $result.Output }
        if ($result.Error) { Write-Host $result.Error -ForegroundColor Yellow }
        if ($result.ExitStatus -ne 0) {
            throw "Remote command failed with exit code $($result.ExitStatus)"
        }
    }
    finally {
        Remove-SSHSession -SessionId $session.SessionId | Out-Null
    }
}
