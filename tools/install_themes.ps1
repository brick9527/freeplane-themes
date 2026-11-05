#Requires -Version 5.1
<#
.SYNOPSIS
    Copies the .mm themes of this project into the Freeplane user template folder.

.DESCRIPTION
    Freeplane reads user templates from  <user directory>\templates .
    The Windows installer points the user directory at %APPDATA%\Freeplane\<version>,
    the portable/default build uses %USERPROFILE%\.freeplane\<version>.
    Start Freeplane once before running this script so that the directory exists.

.PARAMETER UserDir
    Explicit Freeplane user directory (the one that contains preferences.xml /
    the version folder). Overrides auto detection.

.PARAMETER ThemeDir
    Folder with the .mm files. Defaults to ..\themes next to this script.

.PARAMETER WhatIf
    Only print what would be copied.

.EXAMPLE
    .\install_themes.ps1

.EXAMPLE
    .\install_themes.ps1 -UserDir "$env:APPDATA\Freeplane\1.12.x"
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$UserDir,
    [string]$ThemeDir = (Join-Path $PSScriptRoot '..\themes')
)

$ErrorActionPreference = 'Stop'

function Find-UserDirs {
    $roots = @()
    if ($env:APPDATA)  { $roots += (Join-Path $env:APPDATA 'Freeplane') }
    if ($env:USERPROFILE) { $roots += (Join-Path $env:USERPROFILE '.freeplane') }
    foreach ($root in $roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { $_.FullName }
    }
}

if (-not (Test-Path -LiteralPath $ThemeDir)) {
    throw "Theme folder not found: $ThemeDir"
}

$themes = Get-ChildItem -LiteralPath $ThemeDir -Filter *.mm -File
if (-not $themes) {
    throw "No .mm theme found in $ThemeDir"
}

$targets = @()
if ($UserDir) {
    if (-not (Test-Path -LiteralPath $UserDir)) {
        throw "User directory not found: $UserDir"
    }
    $targets = @($UserDir)
}
else {
    $targets = @(Find-UserDirs)
    # A stale version folder (e.g. left behind by an installer that only wrote a
    # README) has no user configuration in it. If exactly one candidate looks
    # like the directory Freeplane actually uses, install only there.
    $markers = 'accelerator.properties', 'auto.properties', 'preferences.xml', 'logs'
    $active = @($targets | Where-Object {
        $dir = $_
        $markers | Where-Object { Test-Path -LiteralPath (Join-Path $dir $_) } | Select-Object -First 1
    })
    if ($active.Count -eq 1) { $targets = $active }
}

if (-not $targets) {
    Write-Host "No Freeplane user directory found." -ForegroundColor Yellow
    Write-Host "  looked in: $env:APPDATA\Freeplane and $env:USERPROFILE\.freeplane"
    Write-Host ""
    Write-Host "Start Freeplane once, then run this script again - or pass the path from"
    Write-Host "Freeplane's 'Tools > Open user directory' with -UserDir."
    exit 1
}

foreach ($target in $targets) {
    $templates = Join-Path $target 'templates'
    if (-not (Test-Path -LiteralPath $templates)) {
        if ($PSCmdlet.ShouldProcess($templates, 'Create folder')) {
            New-Item -ItemType Directory -Path $templates -Force | Out-Null
        }
    }
    foreach ($theme in $themes) {
        $destination = Join-Path $templates $theme.Name
        if ($PSCmdlet.ShouldProcess($destination, "Copy $($theme.Name)")) {
            Copy-Item -LiteralPath $theme.FullName -Destination $destination -Force
            Write-Host ("copied  {0}  ->  {1}" -f $theme.Name, $templates)
        }
    }
}

Write-Host ""
Write-Host "Next in Freeplane:"
Write-Host "  File > New map from template...  (choose 'User templates (*.mm)' at the bottom)"
Write-Host "  or Format > Manage Styles > Copy map styles from... / Replace map styles by..."
Write-Host "  or Tools > Preferences > Environment > 'Standard template file'"
Write-Host ""
