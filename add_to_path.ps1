# Add Python Scripts to PATH for ebook-manager
# Run this script to add the Python Scripts directory to your PATH

Write-Host "Adding Python Scripts directory to PATH..." -ForegroundColor Green

# Get the Python Scripts directory dynamically
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
            } elseif ($path -like "*python*") {
                $null = & $path --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pythonCmd = $path
                    break
                }
            }
        } catch {
            continue
        }
    }
    
    Write-Host "Using Python: $pythonCmd" -ForegroundColor Yellow
    
    # Try to get the correct Scripts directory by detecting Python version
    $pythonOutput = & $pythonCmd -c "import site; import sys; import os; user_base = site.USER_BASE; python_version = f'Python{sys.version_info.major}{sys.version_info.minor}'; versioned_scripts = os.path.join(user_base, python_version, 'Scripts'); generic_scripts = os.path.join(user_base, 'Scripts'); print(versioned_scripts if os.path.exists(versioned_scripts) else generic_scripts)"
    $scriptsDir = $pythonOutput.Trim()
    
    Write-Host "Python Scripts directory: $scriptsDir" -ForegroundColor Yellow
    
    # Check if directory exists
    if (-not (Test-Path $scriptsDir)) {
        Write-Host "Error: Scripts directory does not exist: $scriptsDir" -ForegroundColor Red
        Write-Host "Please install ebook-manager first with: pip install -e ." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check if ebook-manager executables exist
    $ebookManagerExe = Join-Path $scriptsDir "ebook-manager.exe"
    $ebmExe = Join-Path $scriptsDir "ebm.exe"
    
    if (-not (Test-Path $ebookManagerExe)) {
        Write-Host "Error: ebook-manager.exe not found in Scripts directory!" -ForegroundColor Red
        Write-Host "Please reinstall with: pip install -e ." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Check if already in PATH
    if ($currentPath -like "*$scriptsDir*") {
        Write-Host "Python Scripts directory is already in user PATH!" -ForegroundColor Green
    } else {
        # Add to user PATH
        $newPath = "$currentPath;$scriptsDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        Write-Host "Success! Python Scripts directory added to user PATH." -ForegroundColor Green
    }
    
    # Update current session PATH
    Write-Host "`nUpdating current session PATH..." -ForegroundColor Yellow
    $env:PATH += ";$scriptsDir"
    
    # Test if commands are available in current session
    Write-Host "`nTesting installation..." -ForegroundColor Yellow
    
    # Test ebook-manager command
    try {
        $result = & $ebookManagerExe "--help" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ebook-manager command is working!" -ForegroundColor Green
        } else {
            Write-Host "✗ ebook-manager command failed: $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ ebook-manager command error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test ebm command
    try {
        $result = & $ebmExe "--help" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ebm command is working!" -ForegroundColor Green
        } else {
            Write-Host "✗ ebm command failed: $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ ebm command error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test if commands are available via PATH
    Write-Host "`nTesting PATH availability..." -ForegroundColor Yellow
    
    try {
        if (Get-Command "ebook-manager" -ErrorAction SilentlyContinue) {
            Write-Host "✓ ebook-manager is available in PATH!" -ForegroundColor Green
        } else {
            Write-Host "⚠ ebook-manager not found in PATH (restart terminal to use)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ ebook-manager PATH test failed (restart terminal to use)" -ForegroundColor Yellow
    }
    
    try {
        if (Get-Command "ebm" -ErrorAction SilentlyContinue) {
            Write-Host "✓ ebm is available in PATH!" -ForegroundColor Green
        } else {
            Write-Host "⚠ ebm not found in PATH (restart terminal to use)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ ebm PATH test failed (restart terminal to use)" -ForegroundColor Yellow
    }
    
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "INSTALLATION SUMMARY" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    Write-Host "✓ ebook-manager package is installed" -ForegroundColor Green
    Write-Host "✓ Executables are available at: $scriptsDir" -ForegroundColor Green
    Write-Host "✓ PATH has been updated for future sessions" -ForegroundColor Green
    Write-Host "`nTo use in THIS session:" -ForegroundColor Yellow
    Write-Host "  & '$ebookManagerExe' scan C:/Books/" -ForegroundColor White
    Write-Host "  & '$ebmExe' scan C:/Books/" -ForegroundColor White
    Write-Host "`nTo use in NEW sessions (restart terminal):" -ForegroundColor Yellow
    Write-Host "  ebook-manager scan C:/Books/" -ForegroundColor White
    Write-Host "  ebm scan C:/Books/" -ForegroundColor White
    Write-Host "="*60 -ForegroundColor Cyan
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure Python is installed and accessible from PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "You can now use 'ebook-manager' and 'ebm' commands!" -ForegroundColor Green
Read-Host "Press Enter to exit"
