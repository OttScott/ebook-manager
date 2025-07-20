# Immediate Use Script for ebook-manager
# This script allows you to use ebook-manager commands immediately without PATH setup

param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$Command,
    
    [Parameter(Position = 1, Mandatory = $false)]
    [string]$Path,
    
    [Parameter(Mandatory = $false)]
    [string]$Ext,
    
    [Parameter(Mandatory = $false)]
    [switch]$OneFile
)

# Get the Python Scripts directory
try {
    # First, try to detect the correct Python executable
    $pythonCmd = "python"
    
    # Try to find Python 3.13 specifically if available
    $python313Paths = @(
        "E:\Program Files\Python313\python.exe",
        "C:\Program Files\Python313\python.exe",
        "python3.13",
        "python3"
    )
    
    foreach ($path in $python313Paths) {
        try {
            if (Test-Path $path) {
                $pythonCmd = $path
                break
            }
            elseif ($path -like "*python*") {
                $null = & $path --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pythonCmd = $path
                    break
                }
            }
        }
        catch {
            continue
        }
    }
    
    # Try to get the correct Scripts directory by detecting Python version
    $pythonOutput = & $pythonCmd -c "import site; import sys; import os; user_base = site.USER_BASE; python_version = f'Python{sys.version_info.major}{sys.version_info.minor}'; versioned_scripts = os.path.join(user_base, python_version, 'Scripts'); generic_scripts = os.path.join(user_base, 'Scripts'); print(versioned_scripts if os.path.exists(versioned_scripts) else generic_scripts)"
    $scriptsDir = $pythonOutput.Trim()
    $ebookManagerExe = Join-Path $scriptsDir "ebook-manager.exe"
    $ebmExe = Join-Path $scriptsDir "ebm.exe"
    
    if (-not (Test-Path $ebookManagerExe)) {
        Write-Host "Error: ebook-manager.exe not found!" -ForegroundColor Red
        Write-Host "Please install first with: pip install -e ." -ForegroundColor Red
        exit 1
    }
    
    # If no parameters, show help
    if (-not $Command) {
        Write-Host "Ebook Manager - Quick Use Script" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Green
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  .\use-ebm.ps1 scan C:/Books/" -ForegroundColor White
        Write-Host "  .\use-ebm.ps1 import C:/Books/ -Ext .epub -OneFile" -ForegroundColor White
        Write-Host "  .\use-ebm.ps1 analyze C:/Books/" -ForegroundColor White
        Write-Host "`nAvailable commands:" -ForegroundColor Yellow
        Write-Host "  scan, import, analyze, batch-import, import-dir, test-organize, organize" -ForegroundColor White
        Write-Host "`nOptions:" -ForegroundColor Yellow
        Write-Host "  -Ext <extensions>  : Filter by extensions (e.g., -Ext '.epub,.pdf')" -ForegroundColor White
        Write-Host "  -OneFile          : Select one file per book (highest priority)" -ForegroundColor White
        Write-Host "`nDirect executable paths:" -ForegroundColor Yellow
        Write-Host "  Full: $ebookManagerExe" -ForegroundColor Gray
        Write-Host "  Short: $ebmExe" -ForegroundColor Gray
        return
    }
    
    # Build the command arguments
    $cmdArgs = @($Command)
    if ($Path) { $cmdArgs += $Path }
    if ($Ext) { $cmdArgs += "--ext", $Ext }
    if ($OneFile) { $cmdArgs += "--onefile" }
    
    # Execute the command
    Write-Host "Running: ebm $($cmdArgs -join ' ')" -ForegroundColor Green
    & $ebmExe @cmdArgs
    
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
