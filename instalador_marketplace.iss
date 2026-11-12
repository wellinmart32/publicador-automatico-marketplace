[Setup]
AppName=Marketplace AutoPro
AppVersion=2.0.0
AppPublisher=AutomaPro
AppPublisherURL=https://automapro.com
DefaultDirName={userdocs}\AutomaPro\Marketplace
DefaultGroupName=AutomaPro\Marketplace
OutputDir=installer_output
OutputBaseFilename=InstaladorMarketplace
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el Escritorio"; GroupDescription: "Iconos adicionales:"

[Files]
Source: "dist\PublicadorMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PanelControl.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WizardMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ConfiguradorMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\GestorArticulos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\GestorTareasMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config_global.ejemplo.txt"; DestDir: "{app}"; DestName: "config_global.txt"; Flags: onlyifdoesntexist
Source: "config_global.ejemplo.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "plantillas-atencion\plantillas.ejemplo.txt"; DestDir: "{app}\plantillas-atencion"; Flags: ignoreversion
Source: "compartido\*"; DestDir: "{app}\compartido"; Excludes: "__pycache__"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "publicadores\*"; DestDir: "{app}\publicadores"; Excludes: "__pycache__"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: files; Name: "{app}\ExtraerCatalogo.exe"
Type: filesandordirs; Name: "{app}\compartido\__pycache__"
Type: filesandordirs; Name: "{app}\publicadores\__pycache__"

[Dirs]
Name: "{app}\ArticulosMarketplace"
Name: "{app}\plantillas-atencion"
Name: "{app}\perfiles"

[Icons]
Name: "{autoprograms}\Marketplace AutoPro\Marketplace AutoPro"; Filename: "{app}\PublicadorMarketplace.exe"
Name: "{autoprograms}\Marketplace AutoPro\Panel de Control"; Filename: "{app}\PanelControl.exe"
Name: "{autoprograms}\Marketplace AutoPro\Configurador"; Filename: "{app}\ConfiguradorMarketplace.exe"
Name: "{autodesktop}\Marketplace AutoPro"; Filename: "{app}\PublicadorMarketplace.exe"; Tasks: desktopicon
Name: "{autodesktop}\Panel de Control Marketplace"; Filename: "{app}\PanelControl.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WizardMarketplace.exe"; Description: "Configurar Marketplace AutoPro"; Flags: nowait postinstall skipifsilent; Check: EsInstalacionNueva

[Code]
var
  InstalacionNueva: Boolean;

// Se evalúa antes de copiar archivos: si ya hay configuración, es una actualización y no se tocan los datos del cliente
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
    InstalacionNueva := not FileExists(ExpandConstant('{app}\config_global.txt'));
end;

function EsInstalacionNueva: Boolean;
begin
  Result := InstalacionNueva;
end;
