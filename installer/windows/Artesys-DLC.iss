#define AppName "Artesys-DLC"
#ifndef AppVersion
#define AppVersion "2.1.5"
#endif
#define AppPublisher "Artesys-DLC"

[Setup]
AppId={{60D4A8B1-891B-43F8-9481-92586D6FD34C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir=Output
OutputBaseFilename=Artesys-DLC-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\.venv\Scripts\python.exe

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "..\..\run.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\tkinter_fix.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\modules\*"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\media\*"; DestDir: "{app}\media"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\models\instructions.txt"; DestDir: "{app}\models"; Flags: ignoreversion
Source: "install.ps1"; DestDir: "{app}\installer\windows"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\run.py"""; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\run.py"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoLogo -NoProfile -ExecutionPolicy Bypass -File ""{app}\installer\windows\install.ps1"" -SkipShortcut"; StatusMsg: "Installing prerequisites, Python packages, and models..."; Flags: waituntilterminated
Filename: "{app}\.venv\Scripts\pythonw.exe"; Parameters: """{app}\run.py"""; WorkingDir: "{app}"; Description: "Launch Artesys-DLC"; Flags: postinstall nowait skipifsilent; Check: FileExists(ExpandConstant('{app}\.venv\Scripts\pythonw.exe'))

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"
Type: files; Name: "{app}\models\gfpgan-1024.onnx"
Type: files; Name: "{app}\models\inswapper_128_fp16.onnx"