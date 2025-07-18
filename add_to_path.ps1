# Add Python Scripts to PATH for ebook-manager
# Run this script to add the Python Scripts directory to your PATH

Write-Host "Adding Python Scripts directory to PATH..." -ForegroundColor Green

# Get the Python Scripts directory dynamically
try {
    $pythonOutput = & python -c "import site; print(site.USER_BASE + '\\Scripts')"
    $scriptsDir = $pythonOutput.Trim()
    
    Write-Host "Python Scripts directory: $scriptsDir" -ForegroundColor Yellow
    
    # Check if directory exists
    if (-not (Test-Path $scriptsDir)) {
        Write-Host "Error: Scripts directory does not exist: $scriptsDir" -ForegroundColor Red
        Write-Host "Please install ebook-manager first with: pip install -e ." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Check if already in PATH
    if ($currentPath -like "*$scriptsDir*") {
        Write-Host "Python Scripts directory is already in PATH!" -ForegroundColor Green
    } else {
        # Add to user PATH
        $newPath = "$currentPath;$scriptsDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        Write-Host "Success! Python Scripts directory added to user PATH." -ForegroundColor Green
        Write-Host "Please restart your PowerShell/Command Prompt to use:" -ForegroundColor Cyan
        Write-Host "  ebook-manager scan C:/Books/" -ForegroundColor White
        Write-Host "  ebm scan C:/Books/" -ForegroundColor White
    }
    
    # Test if commands are available in current session
    Write-Host "`nTesting installation..." -ForegroundColor Yellow
    
    $env:PATH += ";$scriptsDir"
    
    if (Get-Command "ebook-manager.exe" -ErrorAction SilentlyContinue) {
        Write-Host "✓ ebook-manager command is available!" -ForegroundColor Green
    } else {
        Write-Host "✗ ebook-manager command not found" -ForegroundColor Red
    }
    
    if (Get-Command "ebm.exe" -ErrorAction SilentlyContinue) {
        Write-Host "✓ ebm command is available!" -ForegroundColor Green
    } else {
        Write-Host "✗ ebm command not found" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure Python is installed and accessible from PATH" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
