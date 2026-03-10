; omni_installer.iss
[Setup]
AppName=Omni HUD
AppVersion=1.0
DefaultDirName={autopf}\OmniHUD
DefaultGroupName=Omni HUD
UninstallDisplayIcon={app}\Omni_HUD.exe
Compression=lzma2/ultra64
InternalCompressLevel=ultra64
SolidCompression=yes
OutputDir=setup
OutputBaseFilename=Omni_HUD_Setup
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Apuntamos al ejecutable único comprimido
Source: "dist\Omni_HUD.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Omni HUD"; Filename: "{app}\Omni_HUD.exe"
Name: "{commondesktop}\Omni HUD"; Filename: "{app}\Omni_HUD.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Omni_HUD.exe"; Description: "Lanzar Omni HUD"; Flags: nowait postinstall skipifsilent
