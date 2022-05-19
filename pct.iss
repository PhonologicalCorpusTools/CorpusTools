#define MyAppName "Phonological CorpusTools"
#define MyDistName "PhonologicalCorpusTools"
#define MyAppVersion "1.5.1"
#define MyPlatform "win-amd64"
#define MyAppPublisher "PCT"
#define MyAppURL "http://PhonologicalCorpusTools.github.io/CorpusTools/"
#define MyAppExeName "pct.exe"

[Setup]
AppId={{9f3fd2c0-db11-4d9b-8124-2e91e6cfd19d}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2015 PCT
DefaultDirName={pf}\{#MyAppPublisher}
DefaultGroupName={#MyAppPublisher}
AllowNoIcons=yes
OutputBaseFilename={#MyDistName}_win64_{#MyAppVersion}
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
ShowLanguageDialog=no
LanguageDetectionMethod=none
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ChangesAssociations=True
MinVersion=0,6.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; x64 files
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\"; Flags: ignoreversion; Check: Is64BitInstallMode     
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\esky-files\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\esky-files\"; Flags: ignoreversion; Check: Is64BitInstallMode    
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\html\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\html\"; Flags: ignoreversion recursesubdirs; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\imageformats\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\imageformats\"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\mediaservice\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\mediaservice\"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\platforms\*"; DestDir: "{app}\appdata\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\platforms\"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\platforms\*.dll"; DestDir: "{app}\platforms"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\*.dll"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode

[Dirs]
name: "{app}\appdata\updates\ready"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall Phonological CorpusTools"; Filename: "{uninstallexe}"
Name: "{group}\Readme"; Filename: "{#MyAppURL}#phonological-corpustools"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Messages]
WelcomeLabel1=Welcome to the PCT Setup Wizard
FinishedHeadingLabel=Completing the PCT Setup Wizard

