# NOTE: A lot of this file was taken from https://github.com/kichik/nsis/blob/master/Examples/Modern%20UI/Basic.nsi
# The original example was written by Joost Verburg

!include "MUI2.nsh"

Name "lintrans"
OutFile "install-lintrans-Windows.exe"
Unicode True

BrandingText " "

InstallDir "$APPDATA\lintrans"
InstallDirRegKey HKCU "Software\lintrans" ""

RequestExecutionLevel user

!define MUI_ABORTWARNING

!define MUI_ICON "lintrans.ico"
!define MUI_UNICON "lintrans.ico"

!define MUI_COMPONENTSPAGE_SMALLDESC

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\COPYING"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

# Default section
Section
	SetOutPath "$INSTDIR"

	File lintrans.exe

	WriteRegStr HKCU "Software\lintrans" "" "$INSTDIR"

	WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

# Sections to act as components on the MUI components page
Section "Add to Start Menu" AddToStartMenu
	CreateShortcut "$SMPROGRAMS\lintrans.lnk" "$INSTDIR\lintrans.exe"
SectionEnd

Section "Create Desktop shortcut" CreateDesktopShortcut
	CreateShortcut "$DESKTOP\lintrans.lnk" "$INSTDIR\lintrans.exe"
SectionEnd

Section "Associate with .lt files" AssociateWithLtFiles
	WriteRegStr HKCU "Software\Classes\.lt" "" "lintransSession"

	WriteRegStr HKCU "Software\Classes\lintransSession" "" "lintrans session save file"
	WriteRegStr HKCU "Software\Classes\lintransSession\shell\open\command" "" '"$INSTDIR\lintrans.exe" "%1"'
SectionEnd

# Describe the optional components
LangString DESC_AddToStartMenu ${LANG_ENGLISH} "Allow lintrans to be run from the Start Menu."
LangString DESC_CreateDesktopShortcut ${LANG_ENGLISH} "Create a shortcut to lintrans on your desktop."
LangString DESC_AssociateWithLtFiles ${LANG_ENGLISH} "Open .lt files (lintrans sessions save files) with lintrans when you double-click them."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${AddToStartMenu} $(DESC_AddToStartMenu)
	!insertmacro MUI_DESCRIPTION_TEXT ${CreateDesktopShortcut} $(DESC_CreateDesktopShortcut)
	!insertmacro MUI_DESCRIPTION_TEXT ${AssociateWithLtFiles} $(DESC_AssociateWithLtFiles)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

# The uninstaller section
Section "uninstall"
	Delete "$SMPROGRAMS\lintrans.lnk"
	Delete "$DESKTOP\lintrans.lnk"

	DeleteRegKey HKCU "Software\lintrans"
	DeleteRegKey HKCU "Software\Classes\.lt"
	DeleteRegKey HKCU "Software\Classes\lintransSession"

	Delete "$INSTDIR\uninstall.exe"
	Delete "$INSTDIR\lintrans.exe"

	# If the user chooses to install lintrans somewhere else,
	# then we need to delete the exes and lintrans' program data separately
	RMDir /r "$APPDATA\lintrans"
SectionEnd
