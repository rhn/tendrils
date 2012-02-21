from Utils import *
from Options import *
import Screen
import Resources
import MazeRooms
import Global

MazeWidth = 30
MaxX = 29
MazeHeight = 30
MaxY = 29

RoomWidth = 20
RoomHeight = 20

DirectionNames = ["N", "S", "W", "E"]
OppositeDirections = [1, 0, 3, 2]

def GoToMazeLevel(Level):
    print "** --> GoToMazeLevel: %s"%Level
    Global.Party.Z = Level
    Global.Maze.Level = Level
    Global.Maze.Load()
    # Do start-of-level stuff:
    if Level == 1:
        import MazeLevel1
        MazeLevel1.EnterMazeLevel()
    elif Level == 4:
        import MazeLevel4
        MazeLevel4.EnterMazeLevel()
    elif Level == 5:
        import MazeLevel5
        MazeLevel5.EnterMazeLevel()
    elif Level == 6:
        import MazeLevel6
        MazeLevel6.EnterMazeLevel()
    elif Level == 7:
        import MazeLevel7
        MazeLevel7.EnterMazeLevel()
    elif Level == 10:
        import MazeLevel10
        MazeLevel10.EnterMazeLevel()

def GetContentsName(Contents):
    if Contents == 0:
        return "Empty"
    elif Contents == 1:
        return "Monsters"
    else:
        return "Special"

WallTypeNames = {0:"Clear", 1:"Wall", 2:"Door", 3:"Secret door", 4:"Glass wall"}

def GetWallName(WallType):
    return WallTypeNames.get(WallType, "Special")

def LooksLikeWall(WallType):
    if WallType == 1:
        return 1
    if WallType == 3:
        if Global.Party.CanSeeSecretDoors():
            return 0
        return 1

# 111 is generic LOCKED door.
def LooksLikeDoor(WallType):
    if WallType in [2,101,102,103,104,105,106,107,108,109,110, 111]:
        return 1
    if WallType == 3:
        if Global.Party.CanSeeSecretDoors():
            return 1
        return 0
        
class RoomType:
    Empty = 0
    Encounter = 1

class WallType:
    Clear = 0
    Wall = 1
    Door = 2
    SecretDoor = 3
    GlassWall = 4

class Maze:
    """
    The dungeon!  There are ten levels of dungeon, each of which has a 30x30 grid of rooms.  Each room
    has some contents (an integer - 0 for a blank square), and four sides which can be clear, a wall, a door,
    or something special like a secret door.
    The maze state can change during the course of the game - SORT of.  We change the state of a level while
    the party is exploring it, but once they leave the level, the level goes back to normal - monster groups
    are reset, boulders pushed back to their starting spot.  Scenario code can make various notes in the Party,
    which can change the appearance and effects of squares.
    Themes/references:
    1 - Wizardry maze quote
    2 - maze (pac-man)
    3 - 
    4 - fire
    5 - 
    6 - ice
    7 - Conway's game of Life
    8 - Playing cards
    9 - warp zones; zelda dungeon maps
    10 - 
    """
    LevelTitles = {1:"The Overworld", 2:"The Forest of Maze", 3:"The Unholy Cathedral",
                   4:"Ash and Flame", 5:"Dark Castle", 6:"World of Ice", 7:"Neo-Tokyo",
                   8:"You're Nothing but a Pack of Cards", 9:"Welcome To Warp Zone", 10:"Lurking Horror",
                   11:"Sengoku Fever", 12: "Welcome to Bonus Stage", 13: "Lurking Horror"}
    def __init__(self, Level = 1):
        # Dictionary: Maps (X,Y) to the room contents (as an integer)
        self.Rooms = {}
        # Array of dictionaries, one for each direction (N, S, W, E)
        self.Walls = [{},{},{},{}]
        self.Level = Level
    def RemoveWalls(self, X, Y):
        "Remove the walls surrounding one room"
        for Dir in range(4):
            self.Walls[Dir][(X,Y)] = WallType.Clear
    def GetLevelTitle(self):
        return self.LevelTitles.get(self.Level, "A Strange Place")
    def GetWall(self, X, Y, Dir):
        return self.Walls[Dir-1][(X,Y)]
    def GetFileName(self, Level):
        return os.path.join("Mazes","Level%d.txt"%Level)
    def Load(self):
        if Global.Party:
            print Global.Party, type(Global.Party)
            self.Level = Global.Party.Z
        FileName = self.GetFileName(self.Level)
        if not os.path.exists(FileName):
            # Huh...nothing to load.  Just start over:
            self.DigNewLevel()
            return
        File = open(FileName, "r")
        Y = MaxY
        try:
            for FileLine in File.xreadlines():
                FileLine = FileLine.strip()
                if not FileLine or FileLine[0]=="#":
                    continue
                X = 0
                for RoomData in FileLine.split("\t"):
                    Bits = RoomData.split(",")
                    self.Rooms[(X,Y)] = int(Bits[0])
                    for Dir in range(4):
                        self.Walls[Dir][(X,Y)] = int(Bits[Dir+1])
                    X += 1
                Y -= 1
        except:
            print "Error loading dungeon!  Was at %d, %d"%(X, Y)
            traceback.print_exc()
        File.close()
    def Save(self):
        FileName = self.GetFileName(self.Level)
        File = open(FileName, "w")
        for Y in range(MaxY, -1, -1):
            Str = ""
            for X in range(MazeWidth):
                RoomStr = "%d"%self.Rooms[(X, Y)]
                for Dir in range(4):
                    RoomStr += ",%d"%self.Walls[Dir][(X,Y)]
                Str += RoomStr + "\t"
            File.write(Str+"\n")
        File.close()
    def DigNewLevel(self):
        for X in range(MazeWidth):
            for Y in range(MazeHeight):
                self.Rooms[(X,Y)] = RoomType.Empty
                for Dir in range(4):
                    self.Walls[Dir][(X,Y)] = 1
    def GetRoom(self, X, Y):
        Contents = self.Rooms[(X,Y)]
        Walls = {}
        for Dir in range(4):
            Walls[Dir] = self.Walls[Dir][(X,Y)]
        Room = RoomClass(Contents, Walls)
        return Room
    def UpdateRoom(self, Room, X, Y):
        self.Rooms[(X,Y)] = Room.Contents
        for Dir in range(4):
            self.Walls[Dir][(X,Y)] = Room.Walls[Dir]
    def TryEnterNewRoom(self, Screen, X, Y, Heading):
        RoomContents = self.Rooms[(X,Y)]
        ##print "Entering room at (%d, %d) - found %d"%(X, Y, RoomContents)
        Code = MazeRooms.GetEnterRoomRoutine(RoomContents)
        if Code:
            return apply(Code, (Screen, self, X, Y))
        else:
            return 1
    def CanDescend(self, X, Y):
        RoomContents = self.Rooms[(X,Y)]
        if RoomContents in [5,6]:
            return 1
    def CanAscend(self, X, Y):
        RoomContents = self.Rooms[(X,Y)]
        if RoomContents in [4,6]:
            return 1
    def Ascend(self, Screen):
        """
        If there's a down-staircase on the next level with the same X and Y coordinate, go there.
        Otherwise, go to the first down-staircase you find on the next level, even if it has different X and Y.
        """
        GoToMazeLevel(self.Level - 1)
        #self.Level -= 1
        #Global.Party.Z -= 1
        #self.Load()
        Done = 0
        # HACK HACK HACK:
        if Global.Party.Z == 8 and Global.Party.X == 4 and Global.Party.Y == 24:
            Global.Party.X = 29
            Global.Party.Y = 29
        if not self.CanDescend(Global.Party.X, Global.Party.Y):
            for X in range(MazeWidth):
                if Done:
                    break
                for Y in range(MazeHeight):
                    if self.CanDescend(X, Y):
                        Global.Party.X = X
                        Global.Party.Y = Y
                        Done = 1
                        break
        self.TryEnterNewRoom(Screen, Global.Party.X, Global.Party.Y, Global.Party.Heading)
    def Descend(self, Screen):
        GoToMazeLevel(self.Level + 1)
        #self.Level += 1
        #Global.Party.Z += 1
        #self.Load()
        Done = 0
        if not self.CanAscend(Global.Party.X, Global.Party.Y):
            for X in range(MazeWidth):
                if Done:
                    break
                for Y in range(MazeHeight):
                    if self.CanAscend(X, Y):
                        Global.Party.X = X
                        Global.Party.Y = Y
                        Done = 1
                        break
        self.TryEnterNewRoom(Screen, Global.Party.X, Global.Party.Y, Global.Party.Heading)  
class RoomClass:
    def __init__(self, Contents, Walls):
        self.Contents = Contents
        self.Walls = Walls

def IsWanderingBattleOK(X,Y):
    Room = Global.Maze.Rooms[(X,Y)]
    if MazeRooms.WanderingMonstersOK.get(Room, 0):
        return 1
    return 0
WallColors = ((10,10,10), Colors.White, Colors.Green, Colors.Blue)

def GetWallColor(WallType):
    if WallType >= len(WallColors):
        return Colors.Red
    return WallColors[WallType]
        
class RoomSpriteClass(GenericImageSprite):
    def __init__(self, ScreenX, ScreenY, MazeX, MazeY):
        self.image = pygame.Surface((RoomWidth,RoomHeight))
        self.MazeX = MazeX
        self.MazeY = MazeY
        GenericImageSprite.__init__(self, self.image, ScreenX, ScreenY)
        #self.image.set_colorkey((1,1,1)) # NOT transparent
        self.UpdateImage(1)
        #print "Room sprite at (%d, %d)"%(ScreenX, ScreenY)
    def UpdateImage(self,Start=0):        
        self.image.fill((10,10,10)) # Black does NOT work here.  Not 100% sure why not.
        Room = Global.Maze.GetRoom(self.MazeX, self.MazeY)
        Font = GetFont(Fonts.Zelda,16)
        if Room.Contents != 0:
            TextImage = Font.render(str(Room.Contents),1,Colors.Green)
            TextX = max(1, (RoomWidth/2) - (TextImage.get_width()/2))
            self.image.blit(TextImage,(TextX, 2))
        Color = GetWallColor(Room.Walls[0])
        pygame.draw.line(self.image, Color, (0,0), (RoomWidth-1, 0))
        Color = GetWallColor(Room.Walls[1])
        pygame.draw.line(self.image, Color, (0,RoomHeight-1), (RoomWidth-1, RoomHeight-1))
        Color = GetWallColor(Room.Walls[2])        
        pygame.draw.line(self.image, Color, (0,0), (0, RoomHeight-1))
        Color = GetWallColor(Room.Walls[3])
        pygame.draw.line(self.image, Color, (RoomWidth-1,0), (RoomWidth-1, RoomHeight-1))        
        
        TheMapScreen.BackgroundSurface.fill(Colors.Green, self.rect)
        TheMapScreen.BackgroundSurface.blit(self.image, (self.rect.left, self.rect.top))
        TheMapScreen.Surface.blit(self.image, (self.rect.left, self.rect.top))
        Dirty(self.rect)
##        if not Start:
##            print self.rect
##            pygame.display.update(self.rect)

TheMapScreen = None
       
class MapScreen(Screen.TendrilsScreen):
    def __init__(self, App, Argv):
        global TheMapScreen
        TheMapScreen = self
        Screen.TendrilsScreen.__init__(self,App)
        self.CurrentX = 0
        self.CurrentY = 0
        # This flag is set to determine whether we will ADD TO or REPLACE the room contents
        # when a digit is typed.
        self.TypedInRoom = 0
        try:
            Level = int(Argv[2])
            GoToMazeLevel(Level)
            #Global.Maze.Level = Level
            #Global.Party.Z = Level
            #Global.Maze.Load()
            ##print "Editing level %d"%Level
        except:
            pass
        self.RoomSprites = {}
        self.CreateSprites()
        self.PlayMapMusic()
    def PlayMapMusic(self):
        ##Resources.PlayBGMSong("MarioCave.xm")
        pass
    def CreateSprites(self):
        #ScreenX = 0
        #ScreenY = self.Height - RoomHeight
        for X in range(MazeWidth):
            for Y in range(MazeHeight):
                RoomSprite = RoomSpriteClass(self.GetScreenX(X), self.GetScreenY(Y), X, Y) 
                self.RoomSprites[(X,Y)] = RoomSprite
                self.AddBackgroundSprite(RoomSprite)
                #self.AddForegroundSprite(RoomSprite)
        # Content info:
        self.CreateContentSprites()
        self.PrintContents()
        # Instructions:
        self.CreateInstructionSprites()
        # And the curor:
        self.CursorSprite = CursorSprite(self, self.GetScreenX(self.CurrentX), self.GetScreenY(self.CurrentY),
                                         Colors.White, RoomWidth, RoomHeight)
        self.AddAnimationSprite(self.CursorSprite)
    def CreateInstructionSprites(self):
        self.PrintInstructions(300, "Use arrow keys to move.")
        self.PrintInstructions(320, "Type digits to fill rooms.")
        self.PrintInstructions(340, "Shift+arrow digs tunnels.")
        self.PrintInstructions(360, "Ctrl+arrow cycles walls.")
        self.PrintInstructions(380, "Ctrl+S saves the level.")
        self.PrintInstructions(400, "Ctrl+L loads the level.")
    def PrintInstructions(self, Y, Text):
        Sprite = GenericTextSprite(Text, 610, Y, Colors.Blue)
        self.AddBackgroundSprite(Sprite)
    def CreateContentSprites(self):
        self.ContentSprites = []
        for Row in range(7):
            Image = pygame.Surface((180,25))
            ContentSprite = GenericImageSprite(Image, 610, 50 + Row*26)
            self.ContentSprites.append(ContentSprite)
            self.AddForegroundSprite(ContentSprite)
    def PrintContents(self):
        "Re-render the room info at the far right"
        Room = Global.Maze.GetRoom(self.CurrentX, self.CurrentY)
        self.PrintContent(0, "Level %d"%Global.Maze.Level)
        self.PrintContent(1, "X: %d Y: %d"%(self.CurrentX, self.CurrentY))
        self.PrintContent(2, "Content: %d (%s)"%(Room.Contents, GetContentsName(Room.Contents)))
        for Direction in range(4):
            WallType = Room.Walls[Direction]
            self.PrintContent(3 + Direction, "%s: %s"%(DirectionNames[Direction],GetWallName(WallType)))
    def PrintContent(self, RowNumber, Text):
        "Print one of the rows at the far right listing the room we're cursored on"
        Font = GetFont(Fonts.Zelda, 16)
        TextImage = Font.render(str(Text),1,Colors.White)
        self.ContentSprites[RowNumber].image.fill(Colors.Black)
        self.ContentSprites[RowNumber].image.blit(TextImage,(0, 0))
    def GetScreenX(self, RoomX):
        return RoomX * RoomWidth
    def GetScreenY(self, RoomY):
        return self.Height - (RoomY + 1) * RoomHeight
    def HandleArrowKeys(self, KeyList):
        if len(KeyList)<1:
            return
        OldX = self.CurrentX
        OldY = self.CurrentY
        OldRoom = Global.Maze.GetRoom(self.CurrentX, self.CurrentY)
        # Move the cursor:
        if Directions.Up in KeyList:
            Direction = 0
            self.CurrentY += 1
        elif Directions.Down in KeyList:
            Direction = 1
            self.CurrentY -= 1
        elif Directions.Left in KeyList:
            Direction = 2
            self.CurrentX -= 1
        elif Directions.Right in KeyList:
            Direction = 3
            self.CurrentX += 1
        # Wrap on edges:
        if self.CurrentY > MaxY:
            self.CurrentY = 0
        if self.CurrentY < 0:
            self.CurrentY = MaxY
        if self.CurrentX > MaxX:
            self.CurrentX = 0
        if self.CurrentX < 0:
            self.CurrentX = MaxX
        if (self.CurrentX == OldX and self.CurrentY == OldY):
            return
        OppositeDirection = OppositeDirections[Direction]
        # Handle shift-arrow (dig tunnel) or ctrl-arrow (cycle wall):
        NewRoom = Global.Maze.GetRoom(self.CurrentX, self.CurrentY)
        KeyMods = pygame.key.get_mods()
        if (KeyMods & pygame.KMOD_LCTRL) or (KeyMods & pygame.KMOD_LALT):
            # Cycle wall:
            NextWall = (OldRoom.Walls[Direction] + 1) % 5
            OldRoom.Walls[Direction] = NextWall
            if not (KeyMods & pygame.KMOD_LALT):
                ##print "Update new room too!"
                NewRoom.Walls[OppositeDirection] = NextWall
                self.UpdateRoom(NewRoom, self.CurrentX, self.CurrentY)
            else:
                print "Update only the old"
            # Move back:
            self.CurrentX = OldX
            self.CurrentY = OldY                
            self.UpdateRoom(OldRoom, OldX, OldY)
            return
        if (KeyMods & pygame.KMOD_LSHIFT):
            # DIG empty space between the rooms:
            OldRoom.Walls[Direction] = 0
            #self.UpdateRoom(OldRoom, OldX, OldY)
            NewRoom.Walls[OppositeDirection] = 0
            ##print "Direction",Direction,"Opposite",OppositeDirection
            self.UpdateRoom(NewRoom, self.CurrentX, self.CurrentY)
            self.UpdateRoom(OldRoom, OldX, OldY)
        self.EnterNewRoom()
        ##self.UpdateRoom(OldRoom, OldX, OldY)
    def UpdateRoom(self, Room, X, Y):
        ##print "Update room at %d, %d"%(X, Y)
        Global.Maze.UpdateRoom(Room, X, Y)
        self.RoomSprites[(X,Y)].UpdateImage()
        self.PrintContents()
    def RefreshAll(self):
        # Called when the maze is reloaded.  Update ALL our sprites:
        for X in range(MazeWidth):
            for Y in range(MazeHeight):
                self.RoomSprites[(X,Y)].UpdateImage()
        self.PrintContents()
    def EnterNewRoom(self):
        self.TypedInRoom = 0
        self.PrintContents()
        # %%% Scroll, if needed!
        # Move the cursor's sprite:
        self.CursorSprite.rect.left = self.GetScreenX(self.CurrentX)
        self.CursorSprite.rect.top = self.GetScreenY(self.CurrentY)
    def ShowWeirdWalls(self):
        for X in range(30):
            for Y in range(30):
                for Direction in (0, 1, 2, 3):
                    if (Direction == 0):
                        OtherX = X
                        OtherY = (Y + 1)%30
                    elif Direction == 1:
                        OtherX = X
                        OtherY = Y-1
                        if OtherY<0:
                            OtherY=29
                    if (Direction == 3):
                        OtherY = Y
                        OtherX = (X + 1)%30
                    elif Direction == 2:
                        OtherY = Y
                        OtherX = X-1
                        if OtherX<0:
                            OtherX=29
                    OppositeDirection = OppositeDirections[Direction]
                    Wall1 = Global.Maze.Walls[Direction][(X, Y)]
                    Wall2 = Global.Maze.Walls[OppositeDirection][(OtherX, OtherY)]
                    if Wall1!=Wall2:
                        print "from (%s, %s) to (%s, %s): %s!=%s"%(X, Y, OtherX, OtherY, Wall1, Wall2)
                
    def HandleKeyPressed(self, Key):
        ##print Key, type(Key)
        KeyMods = pygame.key.get_mods()
        if Key == ord("z"):
            self.ShowWeirdWalls()
        # Teleporting around the maze:
        if Key == 280: # pgup
            Global.Maze.Level -= 1
            Global.Party.Z -= 1
            self.PrintContents()
        if Key == 281: # pgup
            Global.Maze.Level += 1
            Global.Party.Z += 1
            self.PrintContents()
            
        if Key == 265:
            self.CurrentY = MaxY
            self.EnterNewRoom()
            return
        if Key == 259:
            self.CurrentY = 0
            self.EnterNewRoom()
            return
        if Key == 263:
            self.CurrentX = 0
            self.EnterNewRoom()
            return
        if Key == 257:
            self.CurrentX = MaxX
            self.EnterNewRoom()
            return
        # Saving/loading:
        if Key == 108: #"L"
            if (KeyMods & pygame.KMOD_LCTRL):
                Global.Maze.Load()
                self.RefreshAll()
                return
        if Key == 115: #"S"
            if (KeyMods & pygame.KMOD_LCTRL):
                Global.Maze.Save()
                Resources.PlayStandardSound("Pause.wav")
                return           
        # Room edits:
        CurrentRoom = Global.Maze.GetRoom(self.CurrentX, self.CurrentY)
        RoomChanged = 0
        if Key == 32:
            CurrentRoom.Contents = 0
            RoomChanged = 1
        elif Key in (DigitKeys):            
            if self.TypedInRoom:
                if CurrentRoom.Contents < 100:
                    CurrentRoom.Contents = CurrentRoom.Contents * 10 + DigitKeys.index(Key)
                    Resources.PlayStandardSound("CursorMove.wav")
                    RoomChanged = 1
                else:
                    Resources.PlayStandardSound("Error.wav")
            else:
                CurrentRoom.Contents = DigitKeys.index(Key)
                RoomChanged = 1
                self.TypedInRoom = 1
                Resources.PlayStandardSound("CursorMove.wav")
        if RoomChanged:
            self.UpdateRoom(CurrentRoom, self.CurrentX, self.CurrentY)
            #self.RoomSprites[(self.CurrentX, self.CurrentY)].UpdateImage()
            #self.PrintContents()
            #Global.Maze.UpdateRoom(self.CurrentX, self.CurrentY, CurrentRoom)
        
DigitKeys = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        
##Global.Maze = Maze()
##Global.Maze.DigNewLevel()

def CheckForAllDead():
    for Player in Global.Party.Players:
        if Player.IsAlive():
            return
    Str = "<CN:BRIGHTRED><CENTER>YOU    HAVE    DIED!</C>\n\nYour party of adventurers has perished, and with them die \
the hopes of a thousand worlds..."
    Global.App.ShowNewDialog(Str, Callback = Global.App.ReturnToTitle)
    return 1