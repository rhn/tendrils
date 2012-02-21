from Utils import *
from Constants import *
import Screen
import Resources
import Party
import Maze
import Music
import StatusPanel
import Global
import Bard
import sys

SpriteWidth = 92
HeightPerSprite = 64

RightTurns = {1:4, 2:3, 3:1, 4:2}
LeftTurns = {1:3, 2:4, 3:2, 4:1}
AboutFaces = {1:2, 2:1, 3:4, 4:3}

def GetMovedX(X, Heading, Squares = 1):
    if (Heading == Directions.Left):
        X -= Squares
    elif (Heading == Directions.Right):
        X += Squares
    if (X<0):
        X += Maze.MaxX + 1
    if (X>Maze.MaxX):
        X -= (Maze.MaxX + 1)
    return X

def GetMovedY(Y, Heading, Squares = 1):
    if (Heading == Directions.Down):
        Y -= Squares
    elif (Heading == Directions.Up):
        Y += Squares
    if (Y<0):
        Y += Maze.MaxY + 1
    if (Y>Maze.MaxY):
        Y -= (Maze.MaxY + 1)
    return Y
    
Verbose = 0

LHSBack = None

class HelperSprite(GenericImageSprite):
    DefaultLines = ["Welcome to Tendrils.", "Use arrow keys to explore the maze.","Press space to open doors.", "Good luck!"]
    TicksPerLine = 160
    def __init__(self, Screen, Lines = None):
        self.Screen = Screen
        self.Lines = Lines
        if not self.Lines:
            self.Lines = self.DefaultLines
        self.Tick = 0
        GenericImageSprite.__init__(self,Global.NullImage, 0, 0) # invisible
    def Update(self, Dummy):
        if self.Tick % self.TicksPerLine == 0:
            NewLineIndex = self.Tick / self.TicksPerLine
            if NewLineIndex >= len(self.Lines):
                self.kill()
                return
            Sprite = GlowingTextSprite(self.Screen, self.Lines[NewLineIndex],475, 150 + 60*NewLineIndex, Colors.Green)
            self.Screen.AddAnimationSprite(Sprite)
        self.Tick += 1
        
class MazeScreen(Screen.TendrilsScreen):
    LeftPanelWidth = 150
    MazeDisplayHeight = 450
    def __init__(self, App):
        Screen.TendrilsScreen.__init__(self,App)
        self.SongY = 450
        self.PauseFlag = 0
        self.PauseSprite = None
        Global.MazeScreen = self
##        self.StatusPanel = StatusPanel.StatusPanel(self, self.LeftPanelWidth + 1, self.MazeDisplayHeight + 1,
##            self.Width - self.LeftPanelWidth - 1, self.Height - self.MazeDisplayHeight - 1)
        self.StatusPanel = StatusPanel.StatusPanel(self, 149, 448, 638, 138)        
        self.StatusPanel.IsBattle = 0
        self.SubPanes.append(self.StatusPanel)
        # A sprite to show nice glowy text like "Level 1: A Cool Title"
        self.HelperSprite = None
        # Sprites showing position and heading:
        self.CompassSprite = None
        self.CompassSprite2 = None
        # Rooms can have a description.  If set, it's displayed in the maze area, on the ceiling.  Useful for
        # signs, hints, stuff like that.
        self.SignText = ""
        # If SummonSprite is non-null, then a summoning is in progress.  (No other clicking
        # or keypress will work during the animation)
        self.SummonSprite = None
        self.SummonStartCycle = None
        self.MousePosition = (0,0)
        # Build the sprite that our maze is drawn upon:
        Image = pygame.Surface((650, 435))
        self.MazeSprite = GenericImageSprite(Image, 150, 0)
        self.BackgroundSprites.add(self.MazeSprite)
        self.LHSSprites = pygame.sprite.Group()
        self.DeepSprites =  pygame.sprite.RenderUpdates()
        self.ButtonSprites = pygame.sprite.Group()
        self.EnterNewLevel()
        self.LHSBackSprite = None
        self.RenderLHS()
        self.RenderMaze()
        #self.PlayMazeMusic()
    def AddLHSButton(self, Text, X, Y):
        "Helper for RenderLHS: Adds a button"
        Sprite = GenericImageSprite(FancyAssBoxedText(Text, BackColor = (11,11,11)), X, Y)
        Sprite.Command = Text
        Sprite.rect.left -= Sprite.rect.width / 2
        self.ButtonSprites.add(Sprite)
        self.LHSSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
##    def RedrawBackground(self):
##        self.BackgroundSurface.fill(Colors.Black)
##        self.DeepSprites.draw(self.BackgroundSurface)
##        self.BackgroundSprites.draw(self.BackgroundSurface)
##        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
    def RenderLHSBack(self):
        TileNumber = Resources.Tiles.get(Global.Maze.Level, 1)
        Image1 = Resources.GetImage(os.path.join(Paths.ImagesBackground, "Tile%s.png"%TileNumber))
        Surface = GetTiledImage(140, 600, Image1)
##        Surface = pygame.Surface((140, 600))
##        Y = -5
##        X = -5
##        while (Y<600):
##            X = -5
##            while (X<138):
##                Surface.blit(Image1, (X,Y))
##                X += Image1.get_rect().width
##            Y += Image1.get_rect().height
        self.LHSBackSprite = GenericImageSprite(Surface, 0, 0)
        self.DeepSprites.add(self.LHSBackSprite)
        Image = Resources.GetImage(os.path.join(Paths.ImagesMisc,"StatusPanel.png"))
        BigBiff = GenericImageSprite(Image, 135, 0)
        self.DeepSprites.add(BigBiff) 
    def RenderLHS(self):
        "Renders the Left-Hand-Swath"
        for Sprite in self.LHSSprites.sprites():
            Sprite.kill()
        if not self.LHSBackSprite:
            self.RenderLHSBack()
            
        Sprite = GenericTextSprite("TENDRILS", 70, 2, Colors.LightGrey, CenterFlag = 1, FontSize = 36)
        self.LHSSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        Sprite = GenericTextSprite("Level %d"%Global.Maze.Level, 70, 45, Colors.LightGrey, CenterFlag = 1)
        self.LHSSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        # Buttons:
        self.AddLHSButton("Options", 70, 75)
        self.AddLHSButton("Special Items", 70, 115)
        self.AddLHSButton("Inventory", 70, 155)
        self.AddLHSButton("Help", 30, 195)
        self.AddLHSButton("Quit", 110, 195)
        ###self.AddLHSButton("SendBetaStats", 75, 495) #%%%
        self.RenderLHSSpells()
        # Virtual pet lives at the bottom left: %%%
        self.Redraw()
    def RenderLHSSpells(self):
        "Called by RenderLHS"
        # SPELLS:
        Sprite = GenericTextSprite("Spells:", 10, 250, Colors.Blue)
        self.LHSSprites.add(Sprite)
        self.AddBackgroundSprite(Sprite)
        Y = 270
        # List of active spells:
        if len(Global.Party.ActiveSpells.keys())==0:
            Sprite = GenericTextSprite("(none)", 20, Y, Colors.LightGrey)
            self.LHSSprites.add(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += 20            
        if Global.Party.ActiveSpells.get("Repel",0):
            Sprite = GenericTextSprite("(repel)", 20, Y)
            self.LHSSprites.add(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += 20
        if Global.Party.ActiveSpells.get("Eye of Argon",0):
            Sprite = GenericTextSprite("(Eye of Argon)", 20, Y)
            self.LHSSprites.add(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += 20
        if Global.Party.ActiveSpells.get("Thief",0):
            Sprite = GenericTextSprite("(Thief)", 20, Y)
            self.LHSSprites.add(Sprite)
            self.AddBackgroundSprite(Sprite)
            Y += 20
        if self.CompassSprite:
            self.CompassSprite.kill()
            self.CompassSprite = None
            self.CompassSprite2.kill()
            self.CompassSprite2 = None
        if Global.Party.ActiveSpells.get("Compass",0):
            Sprite = GenericTextSprite("Magic Compass:", 20, Y)
            self.LHSSprites.add(Sprite)
            self.AddForegroundSprite(Sprite)
            Y += 20
            self.CompassSprite = GenericTextSprite("", 40, Y, Colors.DarkGreen)
            self.LHSSprites.add(self.CompassSprite)
            self.AddForegroundSprite(self.CompassSprite)
            Y += 20
            self.CompassSprite2 = GenericTextSprite("", 40, Y, Colors.DarkGreen)
            self.LHSSprites.add(self.CompassSprite2)
            self.AddForegroundSprite(self.CompassSprite2)
            Y += 20
            self.RenderCompass()
    def RenderCompass(self):
        if self.CompassSprite:
            Image = TextImage("%d E, %d N"%(Global.Party.X, Global.Party.Y),Colors.DarkGreen)
            self.CompassSprite.image = Image
            HeadingStr = ["", "North", "South", "West", "East"][Global.Party.Heading]
            Image = TextImage("Heading: %s"%HeadingStr, Colors.DarkGreen)
            self.CompassSprite2.image = Image
    def Activate(self):
        Screen.TendrilsScreen.Activate(self)
        self.StatusPanel.State = StatusPanel.PanelStates.Status
        self.StatusPanel.ReRender()
        self.RenderMaze()
        self.PlayMazeMusic()
    def PlayMazeMusic(self):
        Songs = Global.MusicLibrary.MazeSongs[Global.Maze.Level - 1]
        if not Songs:
            return
        self.SummonSong(random.choice(Songs))
        #SongName = Resources.GetMazeSongName(Global.Maze.Level) #random.choice(Resources.MazeSongNames)
        #self.SummonSong(SongName)
    def EnterNewLevel(self):
        # Load image cache for the maze level:
        self.Images = {}
    def GetWallImage(self, Name):
        #Image = self.Images.get(Name, None)
        Image = None
        if not Image:
            Path = os.path.join("Images","Walls","%s"%Global.Maze.Level, "%s.png"%Name)
            if Name == "floorceil" and not os.path.exists(Path):
                Path = os.path.join("Images","Walls", "%s.png"%Name)
            try:
                Image = Resources.GetImage(Path)
                Image.set_colorkey(Colors.White)
                self.Images[Name] = Image
            except:
                traceback.print_exc()
        return Image
    def RenderMaze(self, RenderHLS = 0):
        self.RenderCompass()
        if RenderHLS:
            self.RenderLHS()
        self.MazeSprite.image.blit(self.GetWallImage("floorceil"), (0,0))
        CurrentX = Global.Party.X
        CurrentY = Global.Party.Y
        Heading = Global.Party.Heading
        WallTop3 = 177
        WallWidth3 = 96
        X = 277
        # Flat walls at depth 3:
        self.RenderOneWall((X - (WallWidth3 * 3), WallTop3),
                           CurrentX, CurrentY, "FLFLFL", Heading, Heading, "Flat3")
        self.RenderOneWall((X - (WallWidth3 * 2), WallTop3),
                            CurrentX, CurrentY, "FLFLF", Heading, Heading, "Flat3")
        self.RenderOneWall((X - WallWidth3, WallTop3),
                           CurrentX, CurrentY, "FLFF", Heading, Heading, "Flat3")
        self.RenderOneWall((X, WallTop3),
                           CurrentX, CurrentY, "FFF", Heading, Heading, "Flat3")
        self.RenderOneWall((X + WallWidth3, WallTop3),
                           CurrentX, CurrentY, "FRFF", Heading, Heading, "Flat3")
        self.RenderOneWall((X + WallWidth3*2, WallTop3),
                           CurrentX, CurrentY, "FRFRF", Heading, Heading, "Flat3")
        self.RenderOneWall((X + WallWidth3*3, WallTop3),
                           CurrentX, CurrentY, "FRFRFR", Heading, Heading, "Flat3")
        # Non-flat walls at depth 3:
        self.RenderOneWall((10, 163),
                           CurrentX, CurrentY, "FFFLL", Heading, LeftTurns[Heading], "f3s2")
        self.RenderOneWall((136, 162),
                           CurrentX, CurrentY, "FFFL", Heading, LeftTurns[Heading], "f3s1")
        self.RenderOneWall((262, 164),
                           CurrentX, CurrentY, "FFF", Heading, LeftTurns[Heading], "f3s0")
        self.RenderOneWall((325 + (325-262) - 15, 164),
                           CurrentX, CurrentY, "FFF", Heading, RightTurns[Heading], "f3s0", 1)        
        self.RenderOneWall((325 + (325-136) - 45, 162),
                           CurrentX, CurrentY, "FFFR", Heading, RightTurns[Heading], "f3s1", 1)
        self.RenderOneWall((325 + (325-10) - 75, 163),
                           CurrentX, CurrentY, "FFFRR", Heading, RightTurns[Heading], "f3s2", 1)
        # Contents at level 3:
        self.RenderContents((X - WallWidth3*3, WallTop3), CurrentX, CurrentY, "FLFLFL", 3)
        self.RenderContents((X - WallWidth3*2, WallTop3), CurrentX, CurrentY, "FLFLF", 3)
        self.RenderContents((X - WallWidth3, WallTop3), CurrentX, CurrentY, "FLFF", 3)
        self.RenderContents((X, WallTop3), CurrentX, CurrentY, "FFF", 3)
        self.RenderContents((X + WallWidth3, WallTop3), CurrentX, CurrentY, "FRFF", 3)
        self.RenderContents((X + WallWidth3*2, WallTop3), CurrentX, CurrentY, "FRFRF", 3)
        self.RenderContents((X + WallWidth3*3, WallTop3), CurrentX, CurrentY, "FRFRFR", 3)
        
        Y = 163
        X = 262
        Width = 126
        # Flat walls at depth 2: 
        self.RenderOneWall((X - Width*3, Y),
                            CurrentX, CurrentY, "FLFLL", Heading, Heading, "Flat2")
        self.RenderOneWall((X - Width*2, Y),
                           CurrentX, CurrentY, "FLFL", Heading, Heading, "Flat2")
        self.RenderOneWall((X - Width, Y),
                           CurrentX, CurrentY, "FFL", Heading, Heading, "Flat2")
        self.RenderOneWall((X, Y),
                           CurrentX, CurrentY, "FF", Heading, Heading, "Flat2")
        self.RenderOneWall((X + Width, Y),
                           CurrentX, CurrentY, "FFR", Heading, Heading, "Flat2")
        self.RenderOneWall((X + Width*2, Y),
                           CurrentX, CurrentY, "FRFR", Heading, Heading, "Flat2")
        self.RenderOneWall((X + Width*3, Y),
                           CurrentX, CurrentY, "FRFRR", Heading, Heading, "Flat2")
        # Non-flat walls part 2:
        self.RenderOneWall((0, 162),
                           CurrentX, CurrentY, "FFLL", Heading, LeftTurns[Heading], "f2s2") #"LeftM")
        
        self.RenderOneWall((42, 132),
                           CurrentX, CurrentY, "FFL", Heading, LeftTurns[Heading], "f2s1") #"LeftN")


        self.RenderOneWall((231, 133),
                           CurrentX, CurrentY, "FF", Heading, LeftTurns[Heading], "f2s0") #"LeftO")
        
        self.RenderOneWall((325 + (325 - 231) - 31, 133),
                           CurrentX, CurrentY, "FF", Heading, RightTurns[Heading], "f2s0",1) #"RightO")
        self.RenderOneWall((325 + (325-42) - 93, 132),
                           CurrentX, CurrentY, "FFR", Heading, RightTurns[Heading], "f2s1", 1) # "RightP")

        self.RenderOneWall((325 + 325 - 31, 162),
                           CurrentX, CurrentY, "FFRR", Heading, RightTurns[Heading], "f2s2", 1) #"RightQ")
        # Contents at depth 2:
        self.RenderContents((X - Width*3, Y), CurrentX, CurrentY, "FLFLL", 2)
        self.RenderContents((X - Width*2, Y), CurrentX, CurrentY, "FLFL", 2)
        self.RenderContents((X - Width, Y), CurrentX, CurrentY, "FFL", 2)
        self.RenderContents((X, Y), CurrentX, CurrentY, "FF", 2)
        self.RenderContents((X + Width, Y), CurrentX, CurrentY, "FFR", 2)
        self.RenderContents((X + Width*2, Y), CurrentX, CurrentY, "FRFR", 2)
        self.RenderContents((X + Width*3, Y), CurrentX, CurrentY, "FRFRR", 2)

        # Flat walls at depth 1:
        Y = 133
        X = 231
        Width = 188
        self.RenderOneWall((X - Width*2, Y),
                            CurrentX, CurrentY, "FLL", Heading, Heading, "Flat1")
        self.RenderOneWall((X - Width, Y),
                            CurrentX, CurrentY, "FL", Heading, Heading, "Flat1")
        self.RenderOneWall((X, Y),
                            CurrentX, CurrentY, "F", Heading, Heading, "Flat1")
        self.RenderOneWall((X + Width, Y),
                            CurrentX, CurrentY, "FR", Heading, Heading, "Flat1")
        self.RenderOneWall((X + Width*2, Y),
                            CurrentX, CurrentY, "FRR", Heading, Heading, "Flat1")
        # Non-flat walls depth 1:
        self.RenderOneWall((0, 117),
                           CurrentX, CurrentY, "FL", Heading, LeftTurns[Heading], "f1s1") #"LeftR")
        
        self.RenderOneWall((138, 39),
                           CurrentX, CurrentY, "F", Heading, LeftTurns[Heading], "f1s0")# "LeftS")
        self.RenderOneWall((325 + (325-138) - 93, 39),
                           CurrentX, CurrentY, "F", Heading, RightTurns[Heading], "f1s0", 1) #"RightS")
        
        self.RenderOneWall((325 + (325) - 43, 117),
                           CurrentX, CurrentY, "FR", Heading, RightTurns[Heading], "f1s1", 1) #"RightT")
        # Contents at depth 1:
        self.RenderContents((X - Width*2, Y), CurrentX, CurrentY, "FLL", 1)
        self.RenderContents((X - Width, Y), CurrentX, CurrentY, "FL", 1)
        self.RenderContents((X, Y), CurrentX, CurrentY, "F", 1)
        self.RenderContents((X + Width, Y), CurrentX, CurrentY, "FR", 1)
        self.RenderContents((X + Width*2, Y), CurrentX, CurrentY, "FRR", 1)
        
        # Flat walls depth 0:
        Y = 38
        X = 138
        Width = 374
        self.RenderOneWall((X - Width, Y),
                            CurrentX, CurrentY, "L", Heading, Heading, "Flat0")
        self.RenderOneWall((X, Y),
                            CurrentX, CurrentY, "", Heading, Heading, "Flat0")
        self.RenderOneWall((X + Width, Y),
                            CurrentX, CurrentY, "R", Heading, Heading, "Flat0")
        # Non-flat walls depth 0:
        self.RenderOneWall((0, 0),
                           CurrentX, CurrentY, "", Heading, LeftTurns[Heading], "f0s0") #"LeftU")
        self.RenderOneWall((650 - 138, 0),
                           CurrentX, CurrentY, "", Heading, RightTurns[Heading], "f0s0", 1) #"RightU")
        # Contents at depth 0:
        self.RenderContents((X - Width, Y), CurrentX, CurrentY, "L", 0)
        self.RenderContents((X, Y), CurrentX, CurrentY, "", 0)
        self.RenderContents((X + Width, Y), CurrentX, CurrentY, "R", 0)
        

        #self.RedrawBackground()
        ##############################
        # Walls are all rendered.  Now do special text:
        self.RenderSignText()
        # Note: Normally, we'd call the Redraw() method here.  However, that can make the glowy sprites look bad if
        # the player walks around while they're fading out.  So, we duplicate bits of the Redraw() method, and we
        # do NOT draw the foreground sprites an extra time (that happens every tick, anyway!)
        ##self.Redraw() #%%% Not that.  Not now.
        self.RedrawBackground()
        self.Surface.fill(Colors.Black)
        self.Surface.blit(self.BackgroundSurface,(0,0))
        for Pane in self.SubPanes:
            Pane.Redraw()
        Dirty(self.Surface.get_rect())
        return
    #self.RenderContents((X, WallTop3), CurrentX, CurrentY, "FFF", 3)
    def RenderContents(self, Coords, X, Y, Moves, Depth):
        ContentsImages = {306:"Rock", 308:"Rock"}
        (X,Y) = self.FollowMoves(X, Y, Global.Party.Heading, Moves)
        Contents = Global.Maze.Rooms[(X,Y)]
        ImageName = ContentsImages.get(Contents, None)
        if not ImageName:
            return
        # Here is some hacky magic, to put rocks in the right place:
        InfoForMoves = {"": ("f0", 45, 189),
                        "FL": ("f1l1", 0, 213),
                        "F": ("f1r1", 238, 213),
                        "FR": ("f1r1", 475, 213),
                        "FLFL": ("f2l2", 0, 218),
                        "FFL": ("f2l1", 107, 218),
                        "FF": ("f2s0", 276,218),
                        "FFR": ("f2r1", 415, 218),
                        "FRFR": ("f2r2", 560, 218),
                        "FLFLFL": ("f3l3", 0, 223),
                        "FLFLF": ("f3l2", 63, 220),
                        "FLFF": ("f3l1", 179, 220),
                        "FFF": ("f3s0", 292, 220),
                        "FRFF": ("f3r1", 391, 220),
                        "FRFRF": ("f3r2", 491, 220),
                        "FRFRFR": ("f3r3", 595, 220),
                        }
        Tuple = InfoForMoves.get(Moves, None)
        if not Tuple:
            return
        Image = Resources.GetImage(os.path.join("Images", "Walls", "%s.png"%Tuple[0]))
        Image.set_colorkey(Colors.White)
        self.MazeSprite.image.blit(Image, (Tuple[1], Tuple[2]))
        return
##        f0	501	261	45	189
##        f1l1	168	164	0	213
##        f1s0	175	164	238	213
##        f1r1	175	164	475	213
##        f2l2	84	90	0	218
##        f2l1	112	91	107	218
##        f2s0	101	91	276	218
##        f2r1	127	91	415	218
##        f2r2	90	91	560	218
##        f3l3	47	58	0	223
##        f3l2	85	62	63	220
##        f3l1	74	62	179	220
##        f3s0	71	62	292	220
##        f3r1	84	62	391	220
##        f3r2	97	62	491	220
##        f3r3	55	61	595	220        
        ImageName += "%s"%Depth
        Image = Resources.GetImage(os.path.join("Images", "Walls", "%s.png"%ImageName))
        Image.set_colorkey(Colors.White)
        self.MazeSprite.image.blit(Image, Coords)
    def RenderSignText(self):
        if self.SignText:
            TextImage = TaggedRenderer.RenderToImage(self.SignText, self.MazeSprite.rect.width - 50)
            Width = TextImage.get_rect().width
            Height = TextImage.get_rect().height
            X = (self.MazeSprite.rect.width / 2) - (Width/2)
            # Blit a cute highlighting rectangle:
            Highlight = pygame.Surface((Width+18, Height+18))
            pygame.draw.rect(Highlight, Colors.DarkGreen, (0, 0, Width+18, Height+18), 0)
            pygame.draw.rect(Highlight, Colors.White, (4, 4, Width+10, Height+10), 1)
            self.MazeSprite.image.blit(Highlight, (X-9, 0))
            # Blit text:
            self.MazeSprite.image.blit(TextImage, (X, 9))
    def RenderOneWall(self, Coords, X, Y, Moves, Heading, WallHeading, ImageFile, FlipFlag = 0):
        (X,Y) = self.FollowMoves(X, Y, Heading, Moves)
        Wall = Global.Maze.GetWall(X, Y, WallHeading)
        (BlitX, BlitY) = Coords        
        if Maze.LooksLikeDoor(Wall):
            Image = self.GetWallImage(ImageFile+"d")
            if FlipFlag and Image:
                Image = pygame.transform.flip(Image, 1, 0)
            if Image != None:
                self.MazeSprite.image.blit(Image, (BlitX, BlitY))
            else:
                pass
        elif Maze.LooksLikeWall(Wall):
            Image = self.GetWallImage(ImageFile)
            if FlipFlag and Image:
                Image = pygame.transform.flip(Image, 1, 0)
            if Image != None:
                self.MazeSprite.image.blit(Image, (BlitX, BlitY))
            else:
                pass
        return
    def FollowMoves(self, X, Y, Heading, Moves):
        for Move in Moves:
            if Move == "L":
                MoveHead = LeftTurns[Heading]
            elif Move == "R":
                MoveHead = RightTurns[Heading]
            else:
                MoveHead = Heading
            X = GetMovedX(X, MoveHead)
            Y = GetMovedY(Y, MoveHead)
        return (X,Y)
    def HandleKeyPressed(self, Key):        
        if self.SummonSprite:
            return
        if Key == pygame.K_ESCAPE:
            if self.PauseFlag:
                self.Unpause()
            else:
                self.Pause()
        if self.PauseFlag:
            return
        if Key == 32:
            # Open a door:
            Room = Global.Maze.GetRoom(Global.Party.X, Global.Party.Y)        
            Wall = Room.Walls[Global.Party.Heading - 1]
            if Wall == Maze.WallType.Clear:
                Resources.PlayStandardSound("Step.wav")
                self.MoveOneStep(Global.Party.Heading)
                return
            if Wall in (Maze.WallType.Door, Maze.WallType.SecretDoor):
                Resources.PlayStandardSound("DoorOpen.wav")
                self.MoveOneStep(Global.Party.Heading)
                return
            if Wall in (Maze.WallType.Wall, Maze.WallType.GlassWall):
                for Player in Global.Party.Players:
                    if Player.Name.lower() == "idspispopd":
                        # Cheat code for passwall!
                        Resources.PlayStandardSound("Step.wav")
                        self.MoveOneStep(Global.Party.Heading)
                        return
                Resources.PlayStandardSound("Bonk.wav")
                return
            self.HandleOpenSpecialDoor(Wall)
        if Key in (280, 265): # pgUp - ascend
            if Global.Maze.CanAscend(Global.Party.X, Global.Party.Y):
                Global.Maze.Ascend(self)
                Lines = ["Level %d"%Global.Maze.Level, "%s"%Global.Maze.GetLevelTitle()]
                self.ShowHelperSprite(Lines)
                self.RenderLHS()
                self.RenderMaze()
            else:
                Resources.PlayStandardSound("Bonk.wav")
            return
        if Key in (281, 259): # pgDown - descend
            if Global.Maze.CanDescend(Global.Party.X, Global.Party.Y):
                Global.Maze.Descend(self)
                Lines = ["Level %d"%Global.Maze.Level, "%s"%Global.Maze.GetLevelTitle()]
                self.ShowHelperSprite(Lines)
                self.RenderLHS()
                self.RenderMaze()
            else:
                Resources.PlayStandardSound("Bonk.wav")
            return
        else:
            self.StatusPanel.HandleKeyPressed(Key)
    def Pause(self):
        Resources.PlayStandardSound("Pause.wav")
        self.PauseFlag = 1
        Music.PauseSong()
        PausedImage = FancyAssBoxedText("Paused (press ESC)", Fonts.PressStart, 24, Spacing = 6)
        self.PauseSprite = GenericImageSprite(PausedImage, 475 - PausedImage.get_rect().width / 2,
                                              225 - PausedImage.get_rect().height / 2)
        self.AddAnimationSprite(self.PauseSprite)
        
    def Unpause(self):
        Resources.PlayStandardSound("Pause.wav")
        self.PauseFlag = 0
        Music.UnpauseSong()
        self.PauseSprite.kill()
        
    def ShowHelperSprite(self, Lines):
        if self.HelperSprite:
            self.HelperSprite.kill()
        self.HelperSprite = HelperSprite(self, Lines)
        self.AddAnimationSprite(self.HelperSprite)            
    def HandleOpenSpecialDoor(self, WallType):
        KeyItems = {101:"Copper Key",
                    102:"Blue Key",
                    103:"Orange Key",
                    104:"Purple Key",
                    105:"Green Key",
                    106:"Red Key",
                    107:"White Key",
                    108:"Silver Key"}
        KeyName = KeyItems.get(WallType, None)
        if KeyName:
            if Global.Party.KeyItemFlags.get(KeyName, None):
                if KeyName == "Copper Key":
                    # Drop Key:
                    del Global.Party.KeyItemFlags[KeyName]
                    # Mark door opened:
                    Global.Party.EventFlags["L1DoorUnlock"] = 1
                    # Unlock door:
                    Global.Maze.Walls[Global.Party.Heading - 1][(Global.Party.X, Global.Party.Y)] = 2
                    # And show dialog:
                    Global.App.ShowNewDialog("You unlock the door with the <CN:YELLOW>copper key</C>.")
                    return
                elif KeyName == "Silver Key":
                    # Drop Key:
                    del Global.Party.KeyItemFlags[KeyName]
                    # Mark door opened:
                    Global.Party.EventFlags["L4DoorUnlock"] = 1
                    # Unlock door:
                    Global.Maze.Walls[Global.Party.Heading - 1][(Global.Party.X, Global.Party.Y)] = 2
                    # And show dialog:
                    Global.App.ShowNewDialog("You unlock the door with the <CN:YELLOW>silver key</C>.")
                    return
                
                else:
                    # Color-keys: Open the door, keep the key
                    Resources.PlayStandardSound("DoorOpen.wav")
                    self.MoveOneStep(Global.Party.Heading)
                    return
            Resources.PlayStandardSound("Bonk.wav")
            self.Redraw()
            Global.App.ShowNewDialog("<CENTER>It's locked!", Width = 150)
            return
        else:
            # Generic LOCKED door
            Global.App.ShowNewDialog("<CENTER>It's locked!", Width = 150)
        
    def MoveTick(self):
        # Bard power:
        Bard.ApplyBardPower(Global.Party)
        # Spells:
        ChangeFlag = Global.Party.DecrementActiveSpells()
        if ChangeFlag:
            self.RenderLHS()
        self.RenderCompass()
        # Conditions:
        for Player in Global.Party.Players:
            if Player.IsAlive():
                Player.MitigateConditions()
                if Player.Perks.get("Poison"):
                    Player.HP -= Player.GetPoisonDamage()
                    if Player.HP <= 0:
                        Player.Die()
                        Maze.CheckForAllDead()
                if Player.HasPerk("Regen"):
                    HealHP = Player.HP / 300.0
                    if HealHP<1.0:
                        if random.random() < HealHP:
                            HealHP = 1.0
                    HealHP = int(HealHP)
                    Player.HP = min(Player.MaxHP, Player.HP + HealHP)
        self.StatusPanel.ReRender()
    def MoveOneStep(self, Heading):
        MovedX = GetMovedX(Global.Party.X, Heading, 1)
        MovedY = GetMovedY(Global.Party.Y, Heading, 1)
        OldX = Global.Party.X
        OldY = Global.Party.Y
        OldSignText = self.SignText
        self.SignText = ""
        Success = Global.Maze.TryEnterNewRoom(self, MovedX, MovedY, Heading)
        if Success:
            Global.Party.X = MovedX
            Global.Party.Y = MovedY
            self.MoveTick()
            self.RenderMaze()
        else:
            # Maybe we moved.  But if not, keep the same sign:
            if Global.Party.X == OldX and Global.Party.Y == OldY:
                self.SignText = OldSignText # ??? WHY or WHY NOT!? %%%
        # Wandering monsters:
        Global.Party.StepsUntilWanderingMonster -= 1
        if Global.Party.StepsUntilWanderingMonster <= 0:
            if self.App.ScreenStack[-1]==self and Maze.IsWanderingBattleOK(Global.Party.X, Global.Party.Y):
                # Repel spell effet:
                if (not Global.Party.ActiveSpells.get("Repel",0)) or (random.random() > 0.8):
                    # Wandering monsters SOMETIMES leave chests:
                    LeaveChest = 0
                    if random.random() > 0.7:
                        LeaveChest = 1
                    self.App.BeginRandomBattle(LeaveChest)
            Global.Party.GetNextRandomBattle()
    def HandleArrowKeys(self, KeyList):
        if self.PauseFlag:
            return 
        if len(KeyList)<1:
            return
        if self.SummonSprite:
            return
        if (Directions.Up in KeyList):
            Room = Global.Maze.GetRoom(Global.Party.X, Global.Party.Y)        
            Wall = Room.Walls[Global.Party.Heading - 1]
            if Wall:
                Resources.PlayStandardSound("Bonk.wav")
                return
            Resources.PlayStandardSound("Step.wav")
            self.MoveOneStep(Global.Party.Heading)
            return
        if (Directions.Left in KeyList):
            NewHeading = LeftTurns[Global.Party.Heading]
            Global.Party.Heading = NewHeading
            self.RenderMaze()
        if (Directions.Right in KeyList):
            NewHeading = RightTurns[Global.Party.Heading]
            Global.Party.Heading = NewHeading
            self.RenderMaze()
        if (Directions.Down in KeyList):
            NewHeading = RightTurns[Global.Party.Heading]
            NewHeading = RightTurns[NewHeading]
            Global.Party.Heading = NewHeading
            self.RenderMaze()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        if self.SummonSprite:
            return
        if self.PauseFlag:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if not Sprite:
            return
        if Sprite.Command == "Options":
            self.App.DoOptions()
        if Sprite.Command == "Help":
            self.App.DoMazeHelp()
        if Sprite.Command == "Special Items":
            self.App.DoSpecialItems()
        if Sprite.Command == "Quit":
            Str = "<CENTER><CN:BRIGHTRED>REALLY</C> quit?\n\n<CN:GREY>Note: You can save your game at Save Shrines"
            self.App.ShowNewDialog(Str, ButtonGroup.YesNo, Callback=self.ReallyQuit)
        elif Sprite.Command == "Inventory":
            Player = self.StatusPanel.Player
            if not Player:
                Player = Global.Party.Players[2]
            Global.App.ShowEquipScreen(Player)
        elif Sprite.Command == "SendBetaStats": # %%%
            print Global.BigBrother
            print dir(Global.BigBrother)
            try:
                Result = Global.BigBrother.ReportBetaStats()
                if not Result:
                    Result="No response."
            except:
                Result = ""
                ResultLines = traceback.format_exception(*sys.exc_info())
                for Line in ResultLines:
                    Result += Line+"\r\n"
            Global.App.ShowNewDialog(Result)
    def ReallyQuit(self):
        Global.App.ReturnToTitle()
    def StartSummon(self, SummonSprite):
        self.SummonSprite = SummonSprite
        self.AddAnimationSprite(self.SummonSprite)
        # Kick off motion in a few moments, but first show some glowy text o' doom:
        self.SummonStartCycle = (self.AnimationCycle + 200)%MaxAnimationCycle
        self.ShowGlowingText("Summoned %s!"%SummonSprite.Name, 250)
        self.ShowGlowingText("Follow with the mouse pointer!", 300)
    def HandleMouseMoved(self,Position,Buttons,LongPause = 0):
        self.MousePosition = Position
    def ShowGlowingText(self, Text, Y = None):
        if not Y:
            Y = self.Height / 2
        Sprite = GlowingTextSprite(self, Text, self.Width / 2, Y)
        self.AddAnimationSprite(Sprite)
    def Update(self):
        if self.AnimationCycle == self.SummonStartCycle:
            self.SummonStartCycle = None
            self.SummonSprite.StartedFlag = 1            
        if self.SummonSprite and self.SummonSprite.Done:
            self.FinishSummoning()
        if self.PauseFlag:
            time.sleep(0.05)
    def FinishSummoning(self):
        Damage = self.SummonSprite.GetDamage()
        if self.SummonSprite.Spell.Name == "Angel":
            for Player in Global.Party.Players:
                if Player.IsAlive():
                    Player.HP = min(Player.MaxHP, Player.HP + abs(Damage))
            Resources.PlayStandardSound("Heal.wav")
        elif self.SummonSprite.Spell.Name == "Yoshi":
            # Warp home...IF successful.
            if Damage <= 20: # should be a little tricky...
                self.ShowGlowingText("Failed.")
            else:
                Resources.PlayStandardSound("MegamanNoise.wav")
                self.ShowGlowingText("Zoom!")
                Global.Party.X = Global.Party.InnX
                Global.Party.Y = Global.Party.InnY
                if Global.Maze.Level != Global.Party.InnZ:
                    Global.Maze.Level = Global.Party.InnZ
                    Global.Maze.Load()
                self.RenderLHS()
                self.RenderMaze()
                self.Redraw()
        elif self.SummonSprite.Spell.Name == "Eye of Argon":
            Global.Party.ActiveSpells["Eye of Argon"] = int(Damage)
            Resources.PlayStandardSound("MagicDodge.wav")
        elif self.SummonSprite.Spell.Name == "Thief":
            Global.Party.ActiveSpells["Thief"] = int(Damage)
            Resources.PlayStandardSound("MagicDodge.wav")
        self.RenderLHS()
        self.StatusPanel.ReRender()
        self.SummonSprite = None


if PSYCO_ON:
    psyco.bind(MazeScreen.FollowMoves)
    psyco.bind(MazeScreen.RenderMaze)
    psyco.bind(MazeScreen.RenderOneWall)        