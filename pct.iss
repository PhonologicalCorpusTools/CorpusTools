#define MyAppName "Phonological CorpusTools"
#define MyDistName "PhonologicalCorpusTools"
#define MyAppVersion "1.0.1"
#define MyPlatform "win-amd64"
#define MyAppPublisher "PCT"
#define MyAppURL "http://kchall.github.io/CorpusTools/"
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
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
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
Source: "dist\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\*"; DestDir: "{app}\{#MyDistName}-{#MyAppVersion}.{#MyPlatform}\"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Readme"; Filename: "https://github.com/kchall/CorpusTools#phonological-corpustools"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Messages]
WelcomeLabel1=Welcome to the PCT Setup Wizard
FinishedHeadingLabel=Completing the PCT Setup Wizard

