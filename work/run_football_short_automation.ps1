$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$python = 'C:\Users\Wendy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$script = Join-Path $root 'work\football_short_automation.py'
$logDir = Join-Path $root 'work\automation_state\logs'

if (-not (Test-Path $python)) {
    throw "Bundled Python runtime not found: $python"
}
if (-not (Test-Path $script)) {
    throw "Automation script not found: $script"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stdout = Join-Path $logDir "$stamp.stdout.log"
$stderr = Join-Path $logDir "$stamp.stderr.log"

$proc = Start-Process `
    -FilePath $python `
    -ArgumentList @($script, '--run-once') `
    -WorkingDirectory $root `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru `
    -Wait `
    -WindowStyle Hidden

if ($proc.ExitCode -ne 0) {
    throw "Football automation exited with code $($proc.ExitCode). See logs: $stdout and $stderr"
}

Write-Host "Football automation completed successfully."
