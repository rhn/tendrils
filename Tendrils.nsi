
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
OutFile "Tendrils.20110130.exe"

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
File "BGM.txt"
File "BigBrother.txt"
File "CombatLog.txt"
File "Critters.txt"
File "Encounters.txt"
File "Items.txt"
File "Map.txt"
File "Tendrils.txt"
File "Trivia.txt"
File "crack.nfo"
File "Bard.py"
File "BattleResults.py"
File "BattleScreen.py"
File "BattleSprites.py"
File "BlezmonScreen.py"
File "Blinkenlights.py"
File "BlockScreen.py"
File "Cacophany.py"
File "Cards.py"
File "CastleLock.py"
File "ChestScreen.py"
File "Constants.py"
File "CountLines.py"
File "Critter.py"
File "CRLF.py"
File "DalekScreen.py"
File "DancingScreen.py"
File "DialogScreen.py"
File "EquipScreen.py"
File "FadeScreen.py"
File "FirstScreen.py"
File "FreePlayScreen.py"
File "Global.py"
File "GrumbleCakes.py"
File "InnScreen.py"
File "Instructions.py"
File "ItemPanel.py"
File "JoustPongScreen.py"
File "JoyConfigScreen.py"
File "LevelUp.py"
File "LightsOutPanel.py"
File "lights_out.py"
File "lock.py"
File "Magic.py"
File "Mastermind.py"
File "MastermindScreen.py"
File "Maze.py"
File "MazeLevel1.py"
File "MazeLevel10.py"
File "MazeLevel2.py"
File "MazeLevel3.py"
File "MazeLevel4.py"
File "MazeLevel5.py"
File "MazeLevel6.py"
File "MazeLevel7.py"
File "MazeLevel8.py"
File "MazeLevel9.py"
File "MazeMaker.py"
File "MazeRooms.py"
File "MazeScreen.py"
File "MemoryCard.py"
File "MessagePanel.py"
File "modmatrix.py"
File "Music.py"
File "NewDialogScreen.py"
File "NPC.py"
File "NPCScreen.py"
File "Old wallSquish.py"
File "Options.py"
File "OptionsScreen.py"
File "Party.py"
File "PegScreen.py"
File "Play.py"
File "PracticeScreen.py"
File "Resources.py"
File "SaveScreen.py"
File "Screen.py"
File "SeanMatrix.py"
File "setup.py"
File "ShopScreen.py"
File "SnipeScreen.py"
File "SolitaireScreen.py"
File "SPCGrabber.py"
File "SPCMunger.py"
File "SpecialItems.py"
File "SpiralMeister.py"
File "SpriteGrab.py"
File "StatusPanel.py"
File "SummonPositions.py"
File "Temp2.py"
File "Tendrils.py"
File "Test.py"
File "TestMunger.py"
File "TowerScreen.py"
File "TriviaScreen.py"
File "Utils.py"
File "VictoryScreen.py"
File "WallGrab.py"
File "wallSquish.py"
File "WelcomeScreen.py"
File "WireLock.py"
File "WordDialTrap.py"
File "WordSquares.py"
File "WormScreen.py"
File "base.pyd"
File "bufferproxy.pyd"
File "bz2.pyd"
File "cdrom.pyd"
File "color.pyd"
File "constants.pyd"
File "display.pyd"
File "draw.pyd"
File "event.pyd"
File "fastevent.pyd"
File "font.pyd"
File "image.pyd"
File "imageext.pyd"
File "joystick.pyd"
File "key.pyd"
File "mask.pyd"
File "mixer.pyd"
File "mixer_music.pyd"
File "mouse.pyd"
File "movie.pyd"
File "overlay.pyd"
File "pixelarray.pyd"
File "rect.pyd"
File "rwobject.pyd"
File "scrap.pyd"
File "select.pyd"
File "surface.pyd"
File "surflock.pyd"
File "time.pyd"
File "transform.pyd"
File "unicodedata.pyd"
File "_arraysurfarray.pyd"
File "_numericsndarray.pyd"
File "_numericsurfarray.pyd"
File "_psyco.pyd"
File "_socket.pyd"
File "_ssl.pyd"
File "jpeg.dll"
File "libfreetype-6.dll"
File "libogg-0.dll"
File "libpng12-0.dll"
File "libtiff.dll"
File "libvorbis-0.dll"
File "libvorbisfile-3.dll"
File "MSVCR71.dll"
File "python25.dll"
File "SDL.dll"
File "SDL_image.dll"
File "SDL_mixer.dll"
File "SDL_ttf.dll"
File "smpeg.dll"
File "zlib1.dll"
File "Tendrils.exe"
File "w9xpopen.exe"
File "library.zip"
File /r Mazes
File /r Fonts
File /r NPC
File /r Summon
File /r Music
File /r Images
File /r Sounds


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
