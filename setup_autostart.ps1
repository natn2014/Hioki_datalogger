# HIOKI Resistance Meter - Windows Auto-Startup Setup Script
# This script registers the application to automatically start after Windows boots
# Run this with administrator privileges: powershell -ExecutionPolicy Bypass -File setup_autostart.ps1

param(
    [switch]$Remove = $false
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Error "This script requires administrator privileges. Please run as administrator."
    exit 1
}

$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$autostartScript = Join-Path $scriptPath "autostart.bat"
$startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$shortcutPath = Join-Path $startupFolder "HIOKI_Resistance_Meter.lnk"

if ($Remove) {
    # Remove auto-start shortcut
    Write-Host "Removing auto-start shortcut..."
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "✓ Auto-start removed successfully" -ForegroundColor Green
    } else {
        Write-Host "! Shortcut not found" -ForegroundColor Yellow
    }
} else {
    # Create auto-start shortcut
    Write-Host "Setting up auto-start for HIOKI Resistance Meter..."
    
    # Verify autostart.bat exists
    if (-not (Test-Path $autostartScript)) {
        Write-Error "autostart.bat not found at: $autostartScript"
        exit 1
    }
    
    # Create WScript shell object
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $autostartScript
    $Shortcut.WorkingDirectory = $scriptPath
    $Shortcut.Description = "HIOKI Resistance Meter - Auto-start on boot"
    $Shortcut.WindowStyle = 3  # Minimized window
    $Shortcut.Save()
    
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($WshShell) | Out-Null
    
    Write-Host "✓ Auto-start configured successfully!" -ForegroundColor Green
    Write-Host "  Location: $shortcutPath" -ForegroundColor Cyan
    Write-Host "  Application will start automatically on next boot" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To remove auto-start later, run:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File setup_autostart.ps1 -Remove" -ForegroundColor Yellow
}
