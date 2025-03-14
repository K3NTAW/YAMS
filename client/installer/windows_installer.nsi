; YAMS Windows Installer Script
!include "MUI2.nsh"

; General
Name "YAMS"
OutFile "YAMS_Setup.exe"
InstallDir "$PROGRAMFILES64\YAMS"
InstallDirRegKey HKCU "Software\YAMS" ""

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\icons\app.ico"
!define MUI_UNICON "..\assets\icons\app.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "YAMS" SecYAMS
  SetOutPath "$INSTDIR"
  
  ; Add files
  File /r "dist\YAMS\*.*"
  
  ; Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\YAMS"
  CreateShortCut "$SMPROGRAMS\YAMS\YAMS.lnk" "$INSTDIR\YAMS.exe"
  CreateShortCut "$SMPROGRAMS\YAMS\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\YAMS.lnk" "$INSTDIR\YAMS.exe"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Write registry keys
  WriteRegStr HKCU "Software\YAMS" "" $INSTDIR
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\YAMS" \
                   "DisplayName" "YAMS"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\YAMS" \
                   "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR\*.*"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\YAMS\*.*"
  RMDir "$SMPROGRAMS\YAMS"
  Delete "$DESKTOP\YAMS.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\YAMS"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\YAMS"
SectionEnd
