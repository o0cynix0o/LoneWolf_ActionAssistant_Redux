#Requires -Version 5.1
<#
.SYNOPSIS
    Windows convenience wrapper for the Python Lone Wolf launcher.
#>

param(
    [int]$HttpPort = 8797,
    [int]$WsPort = 8798,
    [switch]$NoBrowser
)

$Root = $PSScriptRoot
$Launcher = Join-Path $Root "launch_lonewolf_redux.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Install Python 3 and try again." -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path -LiteralPath $Launcher)) {
    Write-Host "Launcher not found: $Launcher" -ForegroundColor Red
    pause
    exit 1
}

$launcherArgs = @(
    $Launcher,
    "--http-port", [string]$HttpPort,
    "--ws-port", [string]$WsPort
)

if ($NoBrowser) {
    $launcherArgs += "--no-browser"
}

& python @launcherArgs
