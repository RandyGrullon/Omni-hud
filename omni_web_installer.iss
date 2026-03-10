; omni_web_installer.iss
#define MyAppName "Omni HUD"
#define MyAppVersion "1.0"
#define MyAppPublisher "Randy Grullon"
#define MyAppExeName "run_omni.bat"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=setup
OutputBaseFilename=Omni_HUD_WebSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
Source: "C:\Users\randy\code\Omni\*.py"; DestDir: "{app}\src"; Flags: ignoreversion
Source: "C:\Users\randy\code\Omni\setup_env.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Code]
// Simplificamos el código para evitar errores de identificadores
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

[Run]
Filename: "{app}\setup_env.bat"; StatusMsg: "Iniciando descarga de componentes (10MB)..."; Flags: runhidden
