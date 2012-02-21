"setup.py - Creates a re-distributable package of gaming goodness."
from distutils.core import setup
import glob
import py2exe
import os
import time
import sys

def ListWithExtension(Directory,DesiredExtensions):
    List=[]
    for FileName in os.listdir(Directory):
        Extension = os.path.splitext(FileName)[1]
        if not Extension:
            continue
        Extension = Extension[1:].upper()
        if DesiredExtensions.has_key(Extension):
            FilePath = os.path.join(Directory,FileName)
            List.append(FilePath)
    return List

DataFiles = [\
          (r".",glob.glob(r"*.txt")),
          (r".",glob.glob(r"*.nfo")),
          #(r".",glob.glob(r"*.dll")),
          (r".",glob.glob(r"*.py")),
          (r"Sounds",glob.glob(r"Sounds\*.wav")),
          (r"Sounds\Sinistar",glob.glob(r"Sounds\Sinistar\*.wav")),
          (r"Images",glob.glob(r"Images\*.png")),
          (r"Images\Background",glob.glob(r"Images\Background\*.png")),
          (r"Images\Background\Level1",glob.glob(r"Images\Background\Level1\*.png")),
          (r"Images\Background\Level2",glob.glob(r"Images\Background\Level2\*.png")),
          (r"Images\Background\Level3",glob.glob(r"Images\Background\Level3\*.png")),
          (r"Images\Background\Level4",glob.glob(r"Images\Background\Level4\*.png")),
          (r"Images\Background\Level5",glob.glob(r"Images\Background\Level5\*.png")),
          (r"Images\Background\Level6",glob.glob(r"Images\Background\Level6\*.png")),
          (r"Images\Background\Level7",glob.glob(r"Images\Background\Level7\*.png")),
          (r"Images\Background\Level8",glob.glob(r"Images\Background\Level8\*.png")),
          (r"Images\Background\Level9",glob.glob(r"Images\Background\Level9\*.png")),
          (r"Images\Background\Level10",glob.glob(r"Images\Background\Level10\*.png")),
          (r"Images\Item",glob.glob(r"Images\Item\*.png")),
          (r"Images\Critter",glob.glob(r"Images\Critter\*.png")),
          (r"Images\Walls",glob.glob(r"Images\Walls\*.png")),  # rocks and such
          (r"Images\Walls\1",glob.glob(r"Images\Walls\1\*.png")),
          (r"Images\Walls\2",glob.glob(r"Images\Walls\2\*.png")),
          (r"Images\Walls\3",glob.glob(r"Images\Walls\3\*.png")),
          (r"Images\Walls\4",glob.glob(r"Images\Walls\4\*.png")),
          (r"Images\Walls\5",glob.glob(r"Images\Walls\5\*.png")),
          (r"Images\Walls\6",glob.glob(r"Images\Walls\6\*.png")),
          (r"Images\Walls\7",glob.glob(r"Images\Walls\7\*.png")),
          (r"Images\Walls\8",glob.glob(r"Images\Walls\8\*.png")),
          (r"Images\Walls\9",glob.glob(r"Images\Walls\9\*.png")),
          (r"Images\Walls\10",glob.glob(r"Images\Walls\10\*.png")),
          (r"Images\Magic",glob.glob(r"Images\Magic\*.png")),
          (r"Images\NPC",glob.glob(r"Images\NPC\*.png")),
          (r"Images\Misc",glob.glob(r"Images\Misc\*.png")),
          (r"Images\Misc\BigMaze",glob.glob(r"Images\Misc\BigMaze\*.png")),
          (r"Images\Misc\Blezmon",glob.glob(r"Images\Misc\Blezmon\*.png")),
          (r"Images\Misc\Cards",glob.glob(r"Images\Misc\Cards\*.png")),
          (r"Images\Misc\Daleks",glob.glob(r"Images\Misc\Daleks\*.png")),
          (r"Images\Misc\JoustPong",glob.glob(r"Images\Misc\JoustPong\*.png")),
          (r"Images\Traps",glob.glob(r"Images\Traps\*.png")),
          (r"Images\Traps\LightsOut",glob.glob(r"Images\Traps\LightsOut\*.png")),
          (r"Images\Traps\RedGreen",glob.glob(r"Images\Traps\RedGreen\*.png")),
          (r"Images\Traps\Master",glob.glob(r"Images\Traps\Master\*.png")),
          (r"Images\Projectile",glob.glob(r"Images\Projectile\*.png")),
          (r"Fonts",glob.glob(r"Fonts\*.ttf")),
          (r"Mazes",glob.glob(r"Mazes\*.*")),
          (r"Music\Battle",glob.glob(r"Music\Battle\*.*")),
          (r"Music\Battle\0",glob.glob(r"Music\Battle\0\*.*")),
          (r"Music\Battle\1",glob.glob(r"Music\Battle\1\*.*")),
          (r"Music\Battle\2",glob.glob(r"Music\Battle\2\*.*")),
          (r"Music\Battle\3",glob.glob(r"Music\Battle\3\*.*")),
          (r"Music\Battle\4",glob.glob(r"Music\Battle\4\*.*")),
          (r"Music\Battle\5",glob.glob(r"Music\Battle\5\*.*")),
          (r"Music\Battle\6",glob.glob(r"Music\Battle\6\*.*")),
          (r"Music\Battle\7",glob.glob(r"Music\Battle\7\*.*")),
          (r"Music\Battle\8",glob.glob(r"Music\Battle\8\*.*")),
          (r"Music\Battle\9",glob.glob(r"Music\Battle\9\*.*")),
          (r"Music\Battle\10",glob.glob(r"Music\Battle\10\*.*")),
          (r"Music\Battle\Boss",glob.glob(r"Music\Battle\Boss\*.*")),
          
          (r"Music\BGM",glob.glob(r"Music\BGM\*.*")),
          (r"Music\BGM\1",glob.glob(r"Music\BGM\1\*.*")),
          (r"Music\BGM\2",glob.glob(r"Music\BGM\2\*.*")),
          (r"Music\BGM\3",glob.glob(r"Music\BGM\3\*.*")),
          (r"Music\BGM\4",glob.glob(r"Music\BGM\4\*.*")),
          (r"Music\BGM\5",glob.glob(r"Music\BGM\5\*.*")),
          (r"Music\BGM\6",glob.glob(r"Music\BGM\6\*.*")),
          (r"Music\BGM\7",glob.glob(r"Music\BGM\7\*.*")),
          (r"Music\BGM\8",glob.glob(r"Music\BGM\8\*.*")),
          (r"Music\BGM\9",glob.glob(r"Music\BGM\9\*.*")),
          (r"Music\BGM\10",glob.glob(r"Music\BGM\10\*.*")),
          (r"Music\BGM\Blocks",glob.glob(r"Music\BGM\Blocks\*.*")), 
          (r"NPC",glob.glob(r"NPC\*.txt")),
          (r"Summon",glob.glob(r"Summon\*.dat")),
                  ]
for FileName in os.listdir(os.path.join("Images","Critter")):
    FullPath = os.path.join("Images","Critter", FileName)
    if os.path.isdir(FullPath):
        DataFiles.append(("Images\Critter\%s"%FileName, glob.glob("Images\Critter\%s\*.png"%FileName)))

def BuildDistribution():
    import py2exe
    setup(name="Tendrils",
          windows=("Tendrils.py",), ##glob.glob("*.py"), ##ListWithExtension(".",{"PY":1},
          data_files = DataFiles,      
    )

def BuildNSI():
    NSIScript = """
; Tendrils.nsi
;
; Modified from the example script

!include "MUI.nsh"

;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------

; The name of the installer
Name "Tendrils"

; The file to write
OutFile "Tendrils.%s.exe"

; The default installation directory
InstallDir $PROGRAMFILES\Tendrils

;--------------------------------

; Pages

;Page instfiles

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Modern UI Test" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

Page directory
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_UNPAGE_CONFIRM

;--------------------------------

; The stuff to install
Section "" ;No components page, name is not important

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put files there
%s

  ;Store install folder
  WriteRegStr HKCU "Software\Tendrils" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Tendrils.lnk" "$INSTDIR\Tendrils.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END
  
SectionEnd ; end the section

Section "Uninstall"
  Delete "$INSTDIR"
  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall.lnk"
  
  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"
 
  startMenuDeleteLoop:
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."
    
    IfErrors startMenuDeleteLoopDone
  
    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey /ifempty HKCU "Software\Tendrils"
  
SectionEnd ; end of uninstall
"""
    #####################
    # Write NSIS script:
    FileListStr = ""
    DataFiles.append((".", glob.glob("*.pyd")))
    DataFiles.append((".", glob.glob("*.dll")))
    DataFiles.append((".", glob.glob("*.exe")))
    DataFiles.append((".", glob.glob("*.zip")))
    DirDict = {}
    for (Directory, FileList) in DataFiles:
        Pos = Directory.find("\\")
        print Directory, Pos
        if Directory == ".":
            for FileName in FileList:
                print "Directory %s, File %s"%(Directory, FileName)
                FileListStr += r'File "%s"'%(FileName) + "\n" # Note: Filename is a full (relative) path

        else:
            if Pos==-1:
                FirstDirectory = Directory
            else:
                FirstDirectory = Directory[:Pos]
            DirDict[FirstDirectory] = 1
    for Dir in DirDict.keys():
        FileListStr += "File /r %s\n"%Dir
##        for FileName in FileList:
##            print "Directory %s, File %s"%(Directory, FileName)
##            FileListStr += r'File "%s"'%(FileName) + "\n" # Note: Filename is a full (relative) path
    
    File = open("Tendrils.nsi","w")
    Date = time.strftime("%Y%m%d", time.localtime())
    File.write(NSIScript%(Date, FileListStr))
    File.close()

if __name__ == "__main__":
    if len(sys.argv)>1:
        BuildDistribution()
    else:
        BuildNSI() # run this in dist\tendrils