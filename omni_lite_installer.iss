; omni_lite_installer.iss
#define MyAppName "Omni HUD Lite"
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
OutputBaseFilename=Omni_HUD_LiteSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Solo tus archivos de código
Source: "C:\Users\randy\code\Omni\*.py"; DestDir: "{app}\src"; Flags: ignoreversion
Source: "C:\Users\randy\code\Omni\setup_lite.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Code]
function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if CurPageID = wpReady then begin
    // Verificar si python está instalado
    if not Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then begin
      MsgBox('ERROR: Python no detectado. Por favor instale Python 3.11 siguiendo el tutorial de la web y marque "Add Python to PATH".', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

[Run]
Filename: "{app}\setup_lite.bat"; StatusMsg: "Instalando dependencias de IA (Requiere Python en PATH)..."; Flags: runhidden
