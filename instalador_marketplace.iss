[Setup]
AppName=Marketplace AutoPro
AppVersion=1.0.0
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
Source: "dist\GestorTareasMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ExtraerCatalogo.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WizardMarketplace.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Publicador Marketplace"; Filename: "{app}\PublicadorMarketplace.exe"
Name: "{group}\Gestor de Tareas"; Filename: "{app}\GestorTareasMarketplace.exe"
Name: "{group}\Extraer Catálogo"; Filename: "{app}\ExtraerCatalogo.exe"
Name: "{group}\Configuración Inicial"; Filename: "{app}\WizardMarketplace.exe"
Name: "{commondesktop}\Marketplace AutoPro"; Filename: "{app}\PublicadorMarketplace.exe"; Tasks: desktopicon
Name: "{commondesktop}\Gestor Marketplace"; Filename: "{app}\GestorTareasMarketplace.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WizardMarketplace.exe"; Description: "Ejecutar configuración inicial"; Flags: nowait postinstall skipifsilent