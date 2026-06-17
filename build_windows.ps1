param(
    [string[]]$Models = @("small")
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    py -3.11 -m venv .venv
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt pyinstaller

if ($Models.Length -gt 0) {
    & $Python download_models.py @Models
}

& $Python -m PyInstaller --noconfirm STT_Vi.spec

Write-Host ""
Write-Host "Build complete. Executable is in dist\STT_Vi\ or dist\STT_Vi.exe depending on PyInstaller output."
