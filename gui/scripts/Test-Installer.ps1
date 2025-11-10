# =============================================================================
# AiChemist Transmutation Codex - Installer Test & Verification Script
# =============================================================================
# This script helps test and verify installer, upgrade, and uninstall features
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('install', 'upgrade', 'uninstall', 'verify', 'all')]
    [string]$Action = 'verify',

    [Parameter(Mandatory=$false)]
    [string]$InstallerPath = "",

    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false
)

# Configuration
$AppName = "AiChemist Transmutation Codex"
$PublisherName = "AiChemist"
$DefaultInstallPath = "$env:LOCALAPPDATA\$AppName"
$UserDataPath = "$env:APPDATA\$AppName"
$RegistryPath = "HKCU:\Software\$AppName"
$UninstallRegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"

# Colors
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorInfo = "Cyan"
$ColorWarning = "Yellow"

# =============================================================================
# Helper Functions
# =============================================================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-ApplicationInstalled {
    $regExists = Test-Path $RegistryPath
    $uninstallRegExists = Test-Path $UninstallRegPath
    $filesExist = Test-Path "$DefaultInstallPath\$AppName.exe"

    return @{
        IsInstalled = $regExists -and $uninstallRegExists -and $filesExist
        RegistryExists = $regExists
        UninstallRegistryExists = $uninstallRegExists
        FilesExist = $filesExist
    }
}

function Get-InstalledVersion {
    try {
        $version = (Get-ItemProperty -Path $RegistryPath -Name "Version" -ErrorAction SilentlyContinue).Version
        return $version
    } catch {
        return $null
    }
}

function Get-InstallLocation {
    try {
        $location = (Get-ItemProperty -Path $RegistryPath -Name "InstallLocation" -ErrorAction SilentlyContinue).InstallLocation
        return $location
    } catch {
        return $null
    }
}

function Test-RegistryEntries {
    Write-ColorOutput "`nChecking Registry Entries..." $ColorInfo

    # Check application registry
    if (Test-Path $RegistryPath) {
        Write-ColorOutput "  ✓ Application registry key exists" $ColorSuccess

        $props = Get-ItemProperty -Path $RegistryPath
        Write-Host "    Version: $($props.Version)"
        Write-Host "    Install Location: $($props.InstallLocation)"
        Write-Host "    Install Date: $($props.InstallDate)"
    } else {
        Write-ColorOutput "  ✗ Application registry key not found" $ColorError
    }

    # Check uninstall registry
    if (Test-Path $UninstallRegPath) {
        Write-ColorOutput "  ✓ Uninstall registry key exists" $ColorSuccess

        $props = Get-ItemProperty -Path $UninstallRegPath
        Write-Host "    Display Name: $($props.DisplayName)"
        Write-Host "    Display Version: $($props.DisplayVersion)"
        Write-Host "    Publisher: $($props.Publisher)"
        Write-Host "    Install Location: $($props.InstallLocation)"
        Write-Host "    Estimated Size: $($props.EstimatedSize) KB"
        Write-Host "    Modify Enabled: $(if ($props.NoModify -eq 0) { 'Yes' } else { 'No' })"
        Write-Host "    Repair Enabled: $(if ($props.NoRepair -eq 0) { 'Yes' } else { 'No' })"
        Write-Host "    Uninstall String: $($props.UninstallString)"
        Write-Host "    URL Info: $($props.URLInfoAbout)"
        Write-Host "    Help Link: $($props.HelpLink)"
        Write-Host "    Update URL: $($props.URLUpdateInfo)"
    } else {
        Write-ColorOutput "  ✗ Uninstall registry key not found" $ColorError
    }
}

function Test-InstalledFiles {
    Write-ColorOutput "`nChecking Installed Files..." $ColorInfo

    $installPath = Get-InstallLocation
    if (-not $installPath) {
        $installPath = $DefaultInstallPath
    }

    if (Test-Path $installPath) {
        Write-ColorOutput "  ✓ Installation directory exists: $installPath" $ColorSuccess

        # Check main executable
        $exePath = Join-Path $installPath "$AppName.exe"
        if (Test-Path $exePath) {
            Write-ColorOutput "  ✓ Main executable exists" $ColorSuccess
            $fileInfo = Get-Item $exePath
            Write-Host "    Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
            Write-Host "    Last Modified: $($fileInfo.LastWriteTime)"
        } else {
            Write-ColorOutput "  ✗ Main executable not found" $ColorError
        }

        # Check uninstaller
        $uninstallerPath = Join-Path $installPath "Uninstall $AppName.exe"
        if (Test-Path $uninstallerPath) {
            Write-ColorOutput "  ✓ Uninstaller exists" $ColorSuccess
        } else {
            Write-ColorOutput "  ✗ Uninstaller not found" $ColorError
        }

        # Check resources
        $resourcesPath = Join-Path $installPath "resources"
        if (Test-Path $resourcesPath) {
            Write-ColorOutput "  ✓ Resources directory exists" $ColorSuccess

            # Check for Python backend
            $pythonBackend = Join-Path $resourcesPath "python-backend"
            if (Test-Path $pythonBackend) {
                Write-ColorOutput "  ✓ Python backend exists" $ColorSuccess
            } else {
                Write-ColorOutput "  ✗ Python backend not found" $ColorWarning
            }
        } else {
            Write-ColorOutput "  ✗ Resources directory not found" $ColorError
        }

        # Calculate directory size
        $totalSize = (Get-ChildItem -Path $installPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
        Write-Host "    Total Size: $([math]::Round($totalSize / 1MB, 2)) MB"
    } else {
        Write-ColorOutput "  ✗ Installation directory not found" $ColorError
    }
}

function Test-Shortcuts {
    Write-ColorOutput "`nChecking Shortcuts..." $ColorInfo

    # Check desktop shortcut
    $desktopShortcut = Join-Path $env:USERPROFILE "Desktop\$AppName.lnk"
    if (Test-Path $desktopShortcut) {
        Write-ColorOutput "  ✓ Desktop shortcut exists" $ColorSuccess
    } else {
        Write-ColorOutput "  ✗ Desktop shortcut not found" $ColorWarning
    }

    # Check Start Menu shortcuts
    $startMenuPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$AppName"
    if (Test-Path $startMenuPath) {
        Write-ColorOutput "  ✓ Start Menu folder exists" $ColorSuccess

        $shortcuts = Get-ChildItem -Path $startMenuPath -Filter "*.lnk"
        foreach ($shortcut in $shortcuts) {
            Write-Host "    - $($shortcut.Name)"
        }
    } else {
        Write-ColorOutput "  ✗ Start Menu folder not found" $ColorWarning
    }
}

function Test-UserData {
    Write-ColorOutput "`nChecking User Data..." $ColorInfo

    if (Test-Path $UserDataPath) {
        Write-ColorOutput "  ✓ User data directory exists" $ColorSuccess

        $totalSize = (Get-ChildItem -Path $UserDataPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($totalSize) {
            Write-Host "    Size: $([math]::Round($totalSize / 1MB, 2)) MB"
        }

        # Check for specific files
        $configFile = Join-Path $UserDataPath "config.json"
        if (Test-Path $configFile) {
            Write-ColorOutput "  ✓ Configuration file exists" $ColorSuccess
        }

        $logsPath = Join-Path $UserDataPath "logs"
        if (Test-Path $logsPath) {
            Write-ColorOutput "  ✓ Logs directory exists" $ColorSuccess
            $logFiles = Get-ChildItem -Path $logsPath -Recurse -File
            Write-Host "    Log files: $($logFiles.Count)"
        }
    } else {
        Write-ColorOutput "  ℹ User data directory not found (not yet created)" $ColorInfo
    }
}

function Test-AddRemovePrograms {
    Write-ColorOutput "`nChecking Add/Remove Programs Entry..." $ColorInfo

    if (Test-Path $UninstallRegPath) {
        Write-ColorOutput "  ✓ Entry exists in Add/Remove Programs" $ColorSuccess

        $props = Get-ItemProperty -Path $UninstallRegPath

        # Verify critical properties
        if ($props.DisplayName) {
            Write-ColorOutput "  ✓ Display Name is set" $ColorSuccess
        }

        if ($props.UninstallString) {
            Write-ColorOutput "  ✓ Uninstall String is set" $ColorSuccess
        }

        if ($props.NoModify -eq 0) {
            Write-ColorOutput "  ✓ Modify/Repair is enabled" $ColorSuccess
        } else {
            Write-ColorOutput "  ✗ Modify/Repair is disabled" $ColorWarning
        }

        if ($props.NoRepair -eq 0) {
            Write-ColorOutput "  ✓ Repair is enabled" $ColorSuccess
        } else {
            Write-ColorOutput "  ✗ Repair is disabled" $ColorWarning
        }

        # Check support links
        if ($props.URLInfoAbout) {
            Write-ColorOutput "  ✓ Website link is set" $ColorSuccess
        }

        if ($props.HelpLink) {
            Write-ColorOutput "  ✓ Support link is set" $ColorSuccess
        }

        if ($props.URLUpdateInfo) {
            Write-ColorOutput "  ✓ Update link is set" $ColorSuccess
        }
    } else {
        Write-ColorOutput "  ✗ Entry not found in Add/Remove Programs" $ColorError
    }
}

# =============================================================================
# Action Functions
# =============================================================================

function Invoke-Install {
    Write-ColorOutput "`n=== Installing AiChemist Transmutation Codex ===" $ColorInfo

    if (-not $InstallerPath) {
        Write-ColorOutput "Error: Installer path not specified. Use -InstallerPath parameter." $ColorError
        return
    }

    if (-not (Test-Path $InstallerPath)) {
        Write-ColorOutput "Error: Installer not found at: $InstallerPath" $ColorError
        return
    }

    $status = Test-ApplicationInstalled
    if ($status.IsInstalled) {
        Write-ColorOutput "Warning: Application is already installed. This will be an upgrade." $ColorWarning
    }

    Write-ColorOutput "Starting installation..." $ColorInfo

    if ($Silent) {
        Start-Process -FilePath $InstallerPath -ArgumentList "/S" -Wait
    } else {
        Start-Process -FilePath $InstallerPath -Wait
    }

    Write-ColorOutput "Installation process completed." $ColorSuccess
    Write-ColorOutput "Run with -Action verify to check installation." $ColorInfo
}

function Invoke-Upgrade {
    Write-ColorOutput "`n=== Upgrading AiChemist Transmutation Codex ===" $ColorInfo

    $status = Test-ApplicationInstalled
    if (-not $status.IsInstalled) {
        Write-ColorOutput "Error: Application is not installed. Cannot upgrade." $ColorError
        Write-ColorOutput "Use -Action install instead." $ColorInfo
        return
    }

    $currentVersion = Get-InstalledVersion
    Write-ColorOutput "Current version: $currentVersion" $ColorInfo

    if (-not $InstallerPath) {
        Write-ColorOutput "Error: Installer path not specified. Use -InstallerPath parameter." $ColorError
        return
    }

    if (-not (Test-Path $InstallerPath)) {
        Write-ColorOutput "Error: Installer not found at: $InstallerPath" $ColorError
        return
    }

    Write-ColorOutput "Starting upgrade..." $ColorInfo

    if ($Silent) {
        Start-Process -FilePath $InstallerPath -ArgumentList "/S" -Wait
    } else {
        Start-Process -FilePath $InstallerPath -Wait
    }

    $newVersion = Get-InstalledVersion
    Write-ColorOutput "Upgrade completed. New version: $newVersion" $ColorSuccess
}

function Invoke-Uninstall {
    Write-ColorOutput "`n=== Uninstalling AiChemist Transmutation Codex ===" $ColorInfo

    $status = Test-ApplicationInstalled
    if (-not $status.IsInstalled) {
        Write-ColorOutput "Application is not installed." $ColorWarning
        return
    }

    $uninstallerPath = Join-Path (Get-InstallLocation) "Uninstall $AppName.exe"

    if (-not (Test-Path $uninstallerPath)) {
        Write-ColorOutput "Error: Uninstaller not found at: $uninstallerPath" $ColorError
        return
    }

    Write-ColorOutput "Starting uninstallation..." $ColorInfo

    if ($Silent) {
        Start-Process -FilePath $uninstallerPath -ArgumentList "/S" -Wait
    } else {
        Start-Process -FilePath $uninstallerPath -Wait
    }

    Write-ColorOutput "Uninstallation process completed." $ColorSuccess

    # Verify cleanup
    Start-Sleep -Seconds 2
    $status = Test-ApplicationInstalled

    if (-not $status.IsInstalled) {
        Write-ColorOutput "✓ Application successfully uninstalled" $ColorSuccess
    } else {
        Write-ColorOutput "⚠ Some components may still remain" $ColorWarning
    }
}

function Invoke-Verify {
    Write-ColorOutput "`n=== Verifying AiChemist Transmutation Codex Installation ===" $ColorInfo

    $status = Test-ApplicationInstalled

    Write-ColorOutput "`nInstallation Status:" $ColorInfo
    if ($status.IsInstalled) {
        Write-ColorOutput "  ✓ Application is installed" $ColorSuccess
        $version = Get-InstalledVersion
        if ($version) {
            Write-Host "    Version: $version"
        }
        $location = Get-InstallLocation
        if ($location) {
            Write-Host "    Location: $location"
        }
    } else {
        Write-ColorOutput "  ✗ Application is not installed" $ColorError
        Write-Host "    Registry: $(if ($status.RegistryExists) { 'Found' } else { 'Not Found' })"
        Write-Host "    Uninstall Registry: $(if ($status.UninstallRegistryExists) { 'Found' } else { 'Not Found' })"
        Write-Host "    Files: $(if ($status.FilesExist) { 'Found' } else { 'Not Found' })"
        return
    }

    # Run all verification tests
    Test-RegistryEntries
    Test-InstalledFiles
    Test-Shortcuts
    Test-UserData
    Test-AddRemovePrograms

    Write-ColorOutput "`n=== Verification Complete ===" $ColorSuccess
}

function Invoke-All {
    Write-ColorOutput "`n=== Running Complete Installation Test Suite ===" $ColorInfo

    if (-not $InstallerPath) {
        Write-ColorOutput "Error: Installer path required for 'all' action. Use -InstallerPath parameter." $ColorError
        return
    }

    # 1. Verify not installed
    Write-ColorOutput "`n1. Verifying clean state..." $ColorInfo
    Invoke-Verify

    # 2. Install
    Write-ColorOutput "`n2. Installing..." $ColorInfo
    Invoke-Install

    # 3. Verify installation
    Write-ColorOutput "`n3. Verifying installation..." $ColorInfo
    Invoke-Verify

    # 4. Test upgrade (reinstall same version)
    Write-ColorOutput "`n4. Testing upgrade..." $ColorInfo
    Invoke-Upgrade

    # 5. Verify after upgrade
    Write-ColorOutput "`n5. Verifying after upgrade..." $ColorInfo
    Invoke-Verify

    # 6. Uninstall
    Write-ColorOutput "`n6. Uninstalling..." $ColorInfo
    Invoke-Uninstall

    # 7. Verify uninstallation
    Write-ColorOutput "`n7. Verifying uninstallation..." $ColorInfo
    Invoke-Verify

    Write-ColorOutput "`n=== Test Suite Complete ===" $ColorSuccess
}

# =============================================================================
# Main Script
# =============================================================================

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║   AiChemist Transmutation Codex - Installer Test Script      ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

switch ($Action) {
    'install' { Invoke-Install }
    'upgrade' { Invoke-Upgrade }
    'uninstall' { Invoke-Uninstall }
    'verify' { Invoke-Verify }
    'all' { Invoke-All }
}

Write-ColorOutput "`nScript execution completed." $ColorInfo

