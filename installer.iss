[Setup]
AppName=stoke
AppVersion=0.7.2
AppPublisher=dvdsvds
AppPublisherURL=https://github.com/dvdsvds/stoke
DefaultDirName={localappdata}\Programs\stoke
DefaultGroupName=stoke
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=stoke-setup-0.7.2
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Files]
Source: "dist\stoke\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Tasks]
Name: "addtopath"; Description: "{cm:AddToPath}"; GroupDescription: "{cm:Options}"

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}'); Tasks: addtopath

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

[CustomMessages]
english.AddToPath=Add stoke to PATH environment variable
korean.AddToPath=stoke를 PATH 환경 변수에 추가
english.Options=Additional options:
korean.Options=추가 옵션:

[Run]
Filename: "{app}\stoke.exe"; Parameters: "--help"; Description: "Test stoke installation"; Flags: postinstall skipifsilent runhidden