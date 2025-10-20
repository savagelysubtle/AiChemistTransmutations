; Inno Setup Script for AiChemist Transmutation Codex
; This script creates a Windows installer that includes bundled Tesseract and Ghostscript

#define MyAppName "AiChemist Transmutation Codex"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
#define MyAppExeName "aichemist_transmutation_codex.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{YOUR-GUID-HERE}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist\installer
OutputBaseFilename=AiChemistSetup_{#MyAppVersion}
SetupIconFile=resources\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files from PyInstaller output
Source: "dist\aichemist_transmutation_codex\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Bundled Tesseract (if not already in PyInstaller output)
; Source: "build\resources\tesseract\*"; DestDir: "{app}\resources\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs

; Ghostscript installer (bundled for automatic installation)
Source: "build\installers\gs10.04.0-win64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

; Pandoc installer (bundled for automatic installation)
Source: "build\installers\pandoc-3.1.11.1-windows-x86_64.msi"; DestDir: "{tmp}"; Flags: deleteafterinstall

; MiKTeX installer (bundled for optional installation)
Source: "build\installers\miktexsetup-x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: FileExists('build\installers\miktexsetup-x64.exe')

; Configuration files
Source: "config\default_config.yaml"; DestDir: "{app}\config"; Flags: ignoreversion

; Licenses
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\resources\tesseract\LICENSE"; DestDir: "{app}\licenses"; DestName: "TESSERACT_LICENSE.txt"; Flags: ignoreversion
Source: "build\resources\ghostscript\LICENSE"; DestDir: "{app}\licenses"; DestName: "GHOSTSCRIPT_LICENSE.txt"; Flags: ignoreversion
; Note: Pandoc license is included in the MSI installer itself

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "docs\TESSERACT_CONFIGURATION.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\BUNDLING_TESSERACT.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\GHOSTSCRIPT_BUNDLING.md"; DestDir: "{app}\docs"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Install Ghostscript silently (if not already installed)
Filename: "{tmp}\gs10.04.0-win64.exe"; Parameters: "/S /D=C:\Program Files\gs\gs10.04.0"; StatusMsg: "Installing Ghostscript..."; Flags: waituntilterminated; Check: not GhostscriptInstalled

; Install Pandoc silently (if not already installed)
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\pandoc-3.1.11.1-windows-x86_64.msi"" /qn /norestart"; StatusMsg: "Installing Pandoc..."; Flags: waituntilterminated; Check: not PandocInstalled

; Install MiKTeX (optional - only if user wants advanced PDF features)
; Note: This is a large download/install (~500MB+), so we make it optional
; Filename: "{tmp}\miktexsetup-x64.exe"; Parameters: "--shared=yes --package-set=basic --quiet"; StatusMsg: "Installing MiKTeX (optional)..."; Flags: waituntilterminated skipifdoesntexist; Check: not MiktexInstalled

; Verify Tesseract installation
Filename: "{app}\resources\tesseract\tesseract.exe"; Parameters: "--version"; Flags: runhidden; StatusMsg: "Verifying Tesseract installation...";

; Verify Ghostscript installation
Filename: "C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe"; Parameters: "--version"; Flags: runhidden; StatusMsg: "Verifying Ghostscript installation..."; Check: GhostscriptInstalled

; Launch application after install (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up logs and temporary files on uninstall
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"

[Code]
function GhostscriptInstalled(): Boolean;
var
  GsPath: String;
begin
  // Check if Ghostscript is already installed
  Result := FileExists('C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe');

  // Also check other common locations
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\GPL Ghostscript\10.04', 'GS_DLL', GsPath);
end;

function PandocInstalled(): Boolean;
var
  PandocPath: String;
begin
  // Check if Pandoc is already installed in common locations
  Result := FileExists('C:\Program Files\Pandoc\pandoc.exe');

  if not Result then
    Result := FileExists('C:\Program Files (x86)\Pandoc\pandoc.exe');

  if not Result then
    Result := FileExists(ExpandConstant('{localappdata}\Pandoc\pandoc.exe'));

  // Also check registry
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Pandoc', 'InstallLocation', PandocPath);
end;

function MiktexInstalled(): Boolean;
var
  MiktexPath: String;
begin
  // Check if MiKTeX is already installed in common locations
  Result := FileExists('C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe');

  if not Result then
    Result := FileExists('C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe');

  if not Result then
    Result := FileExists(ExpandConstant('{localappdata}\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe'));

  // Also check registry
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\MiKTeX.org\MiKTeX', 'Install Root', MiktexPath);
end;

procedure AddToPath(NewPath: String);
var
  CurrentPath: String;
begin
  // Add Ghostscript to user PATH
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
  begin
    // Check if already in PATH
    if Pos(NewPath, CurrentPath) = 0 then
    begin
      // Add to PATH
      if CurrentPath <> '' then
        CurrentPath := CurrentPath + ';' + NewPath
      else
        CurrentPath := NewPath;

      RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath);
    end;
  end
  else
  begin
    // Create PATH variable
    RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', NewPath);
  end;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Optional: Check for .NET runtime, Visual C++ redistributables, etc.
  // if not IsDotNetInstalled(net48, 0) then
  // begin
  //   MsgBox('This application requires .NET Framework 4.8 or later.', mbError, MB_OK);
  //   Result := False;
  // end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InstalledComponents: String;
begin
  if CurStep = ssPostInstall then
  begin
    InstalledComponents := '';

    // Add Ghostscript to PATH after installation
    if GhostscriptInstalled() then
    begin
      AddToPath('C:\Program Files\gs\gs10.04.0\bin');
      InstalledComponents := InstalledComponents + '  • Ghostscript' + #13#10;
    end;

    // Add Pandoc to PATH after installation (Pandoc MSI adds it automatically, but we verify)
    if PandocInstalled() then
    begin
      // Pandoc installer usually adds itself to PATH, but we can add it manually if needed
      if FileExists('C:\Program Files\Pandoc\pandoc.exe') then
        AddToPath('C:\Program Files\Pandoc')
      else if FileExists('C:\Program Files (x86)\Pandoc\pandoc.exe') then
        AddToPath('C:\Program Files (x86)\Pandoc')
      else if FileExists(ExpandConstant('{localappdata}\Pandoc\pandoc.exe')) then
        AddToPath(ExpandConstant('{localappdata}\Pandoc'));

      InstalledComponents := InstalledComponents + '  • Pandoc' + #13#10;
    end;

    // Show message if any components were installed
    if InstalledComponents <> '' then
    begin
      MsgBox('The following components have been installed and added to your PATH:' + #13#10 + #13#10 +
             InstalledComponents + #13#10 +
             'You may need to restart the application for changes to take effect.',
             mbInformation, MB_OK);
    end;
  end;
end;

