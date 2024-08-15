#define MyAppName "FFmpeg - TJSP"
#define MyAppVersion "4.5"
#define MyAppPublisher "Maurício Menon"
#define MyAppURL "https://github.com/mauriciomenon/"
#define MyAppExeName "FFmpeg - TJSP (inclui ffmpeg).exe" ; Substitua com o nome correto do seu executável
#define MyAppAssocName MyAppName + " File" ; Adicione esta linha para definir MyAppAssocName
#define MyAppAssocExt ".myp"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{8BE08B14-FAAE-43F7-B508-CCF2847DAD47}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputBaseFilename=mysetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
[Files]
; Inclua o executável principal
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Inclua a subpasta bin e todo o seu conteúdo
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs

; Inclua todas as outras pastas e arquivos (certifique-se de substituir * pelo caminho correto)
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\bcrypt\*"; DestDir: "{app}\bcrypt"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\certifi\*"; DestDir: "{app}\certifi"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\charset_normalizer\*"; DestDir: "{app}\charset_normalizer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\cryptography\*"; DestDir: "{app}\cryptography"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\cryptography-41.0.3.dist-info\*"; DestDir: "{app}\cryptography-41.0.3.dist-info"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\tcl\*"; DestDir: "{app}\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\tcl8\*"; DestDir: "{app}\tcl8"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\tk\*"; DestDir: "{app}\tk"; Flags: ignoreversion recursesubdirs createallsubdirs

; Inclua todos os outros arquivos na raiz
Source: "C:\Users\menon\git\aulascomad\WinFF\dist\FFmpeg - TJSP (inclui ffmpeg)\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCU; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
