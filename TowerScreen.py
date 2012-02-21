"""
Tower screen.  A 4D maze!
"""
from Utils import *
from Constants import *
import Screen
import BattleSprites
import ItemPanel
import Global
import Resources
import os
import time
import math
import string
import Party
import ChestScreen
import Music

class RunnerSprite(GenericImageSprite):
    def __init__(self, X, Y):
        self.LoadImages()
        self.Ticks = 0
        self.ImageIndex = 0
        self.State = "Stand"
        self.OldState = "Stand"
        GenericImageSprite.__init__(self, self.Images["Stand"][0], X, Y)
    def LoadImages(self):
        # Standing images:
        self.Images = {}
        self.LoadImageSet("Stand", 2)
        # Direction images:
        self.LoadImageSet("North", 6)
        self.LoadImageSet("South", 6)
        self.LoadImageSet("East", 6)
        self.Images["West"] = []
        for Image in self.Images["East"]:
            FlippedImage = pygame.transform.flip(Image, 1, 0)
            self.Images["West"].append(FlippedImage)
    def LoadImageSet(self, Name, MaxIndex):
        self.Images[Name] = []
        for Index in range(MaxIndex):
            Path = os.path.join(Paths.ImagesMisc, "BigMaze","%s.%s.png"%(Name, Index))
            Image = Resources.GetImage(Path)
            Image.set_colorkey((0,0,0))
            self.Images[Name].append(Image)
    def SwapImage(self):
        Center = self.rect.center
        self.image = self.Images[self.State][self.ImageIndex]
        self.rect = self.image.get_rect()
        self.rect.center = Center
    def Update(self, Cycle):
        self.Ticks += 1
        if self.State == "Stand":
            if self.Ticks == 500:
                self.ImageIndex = 1
                self.SwapImage()
            return
        if self.Ticks > 100:
            self.ChangeState("Stand")
            return
        if self.Ticks % 5 == 0:
            self.ImageIndex = (self.ImageIndex + 1)%6
            self.SwapImage()
    def ChangeState(self, NewState):
        if NewState == self.State:
            self.Ticks = self.Ticks % 6
            return
        self.State = NewState
        self.ImageIndex = 0
        self.Ticks = 0
        self.SwapImage()

class MazeDirs:
    North = (0,1,0,0)
    South = (0,-1,0,0)
    East = (1,0,0,0)
    West = (-1,0,0,0)
    Up = (0,0,1,0)
    Down = (0,0,-1,0)
    Znort = (0,0,0,1)
    Flurple = (0,0,0,-1)
    AllDirs = (North, South, East, West, Up, Down, Znort, Flurple)
    
    OppositeDir = {North:South, East:West, Up:Down, Znort:Flurple,
                   South:North, West:East, Down:Up, Flurple:Znort}

# Coords are x,y,z,w (the 'w' stands for 'weird')
KeysToDirs = {ord("n"):MazeDirs.North, ord("s"):MazeDirs.South,
              ord("e"):MazeDirs.East,ord("w"):MazeDirs.West,
              ord("u"):MazeDirs.Up,ord("d"):MazeDirs.Down,
              ord("z"):MazeDirs.Znort,ord("f"):MazeDirs.Flurple,
              }


class Contents:
    Wall = 0
    Space = 1
    DeadEnd = 2
    Exit = 3

# For screen display:
DirLetters = ("N", "S", "E", "W", "U", "D", "Z", "F")
XDirs = (0, 0, 1, -1, 1, -1, -1, 1)
YDirs = (-1, 1, 0, 0, -1, 1, -1, 1)

CenterX = 400
MainCenterY = 300
LineStart = 50

LineFar = 140
LineEnd = 180
LineMiddle = (LineStart + LineFar) / 2.0
    
class TowerScreen(Screen.TendrilsScreen):
    Size = 5
    def __init__(self, App):
        global TScreen
        TScreen = self
        Screen.TendrilsScreen.__init__(self,App)
        self.Coords = (0,0,0,0)
        self.BuildMaze()
        self.PlayerSprite = RunnerSprite(370, 260)
        self.AddAnimationSprite(self.PlayerSprite)
        self.WallSprites = pygame.sprite.Group()
        self.SummonSong("tower")
        self.DrawBackground()
        self.WallSprites = pygame.sprite.Group()
        self.DrawMaze()
        self.ShownInstructions = 0
    def Activate(self):
        if not self.ShownInstructions:
            self.ShownInstructions = 1
            Str = """<CENTER><CN:ORANGE>Tower Maze</C></CENTER>\n\nThe tower maze is laid out in a grid.  You can go \
<CN:GREEN>north</c> and <CN:green>south</c>, \
<CN:GREEN>east</c> and <CN:green>west</c>, \
<CN:GREEN>up</c> and <CN:green>down</c>, and \
<CN:GREEN>znort</c> and <CN:green>furple</c>.

Press keys or click on rooms to move around.  If you get lost, you can escape and return later..."""
            Global.App.ShowNewDialog(Str)
        Screen.TendrilsScreen.Activate(self)
    def DrawBackground(self):
        Sprite = GenericTextSprite("The Dark Tower", 400, 5, Colors.Grey, CenterFlag = 1, FontSize = 32)
        self.AddBackgroundSprite(Sprite)
        BackImage = pygame.Surface((800, 400))
        BackImage.fill(Colors.Black)
        BackSprite = GenericImageSprite(BackImage, 0, 100)
        self.AddBackgroundSprite(BackSprite)
        # Hilite player
        pygame.draw.rect(BackSprite.image, Colors.White, (360, 160, 80, 80),1)
        #Sprite = BoxSprite(380, 230, 40, 40)
        #self.AddBackgroundSprite(Sprite)
        # Lines in each direction:
        
        CenterY = 200
        for Index in range(len(DirLetters)):
            #Sprite = LineSprite(CenterX + LineStart*XDirs[Index], CenterY + LineStart*YDirs[Index],
            #                    CenterX + LineEnd*XDirs[Index], CenterY + LineEnd*YDirs[Index], Colors.Grey)
            pygame.draw.line(BackSprite.image, Colors.Grey,
                             (CenterX + LineStart*XDirs[Index], CenterY + LineStart*YDirs[Index]),
                             (CenterX + LineFar*XDirs[Index], CenterY + LineFar*YDirs[Index]))
            Image = TextImage(DirLetters[Index], Colors.LightGrey, 24)
            Rect = Image.get_rect()
            BackSprite.image.blit(Image, (CenterX + LineMiddle*XDirs[Index] - Rect.width/2, CenterY + LineMiddle*YDirs[Index] - Rect.height/2))
            
            #LetterSprite = GenericTextSprite(DirLetters[Index], 400 + LineMiddle*XDirs[Index], 250 + LineMiddle*YDirs[Index], CenterFlag = 1)
            #self.AddBackgroundSprite(LetterSprite)
        self.ButtonSprites = pygame.sprite.Group()
        ButtonSprite = FancyAssBoxedSprite("Escape!", 700, 550)
        self.AddBackgroundSprite(ButtonSprite)
        self.ButtonSprites.add(ButtonSprite)
    def CanDig(self, X, Y, Z, W, Dir):
        if X + (Dir[0]*2) < 0 or X + (Dir[0]*2) >= self.Size:
            return 0
        if Y + (Dir[1]*2) < 0 or Y + (Dir[1]*2) >= self.Size:
            return 0
        if Z + (Dir[2]*2) < 0 or Z + (Dir[2]*2) >= self.Size:
            return 0
        if W + (Dir[3]*2) < 0 or W + (Dir[3]*2) >= self.Size:
            return 0
        Contents1 = self.Maze[(X+Dir[0],Y+Dir[1],Z+Dir[2],W+Dir[3])]
        NextSquare = (X+Dir[0]*2,Y+Dir[1]*2,Z+Dir[2]*2,W+Dir[3]*2)
        Contents2 = self.Maze[NextSquare]
        if (Contents2 == Contents.DeadEnd):
            return 0
        if (Contents1 != Contents.Space and Contents2 == Contents.Space):
            return 0
        # If you're moving to an empty space, you must move against the backtrack chain:
        if Contents2 == Contents.Space and MazeDirs.OppositeDir[Dir] != self.Backtrack[NextSquare]:
            return 0
        return 1
    def BuildMaze(self):
        "Fill in a 4D maze!"
        # Initialize:
        self.Maze = {}
        self.Backtrack = {}
        Distance = {}
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.W = 0
        FarthestPoint = None
        FarthestDistance = 0
        for X in range(self.Size):
            for Y in range(self.Size):
                for Z in range(self.Size):
                    for W in range(self.Size):
                        self.Maze[(X,Y,Z,W)] = Contents.Wall
                        self.Backtrack[(X,Y,Z,W)] = None
        X = 0
        Y = 0
        Z = 0
        W = 0
        Distance[(X,Y,Z,W)] = 0
        self.Maze[(X,Y,Z,W)] = Contents.Space
        # Main loop:
        Moved = 0
        while (1):
            ##print X, Y, Z, W, Distance[(X, Y, Z, W)],
            # Teleport to a random old square, sometimes:
            if random.random() < 0.05:
                SanityCount = 0
                while (1):
                    TestX = random.randrange(self.Size/2) * 2
                    TestY = random.randrange(self.Size/2) * 2
                    TestZ = random.randrange(self.Size/2) * 2
                    TestW = random.randrange(self.Size/2) * 2
                    if self.Maze[(TestX,TestY,TestZ,TestW)]==Contents.Space:
                        X = TestX
                        Y = TestY
                        Z = TestZ
                        W = TestW
                        break
                    SanityCount += 1
                    if SanityCount > 50:
                        break
            Moved = 0
            OldDistance = Distance[(X, Y, Z, W)]
            # Try to move forward!
            Dirs = list(MazeDirs.AllDirs)
            random.shuffle(Dirs)
            while (1):
                Dir = Dirs[0]
                if self.CanDig(X, Y, Z, W, Dir):
                    # You hear a grinding sound. --more--
                    X += Dir[0]
                    Y += Dir[1]
                    Z += Dir[2]
                    W += Dir[3]
                    self.Maze[(X,Y,Z,W)] = Contents.Space
                    Distance[(X,Y,Z,W)] = OldDistance + 1
                    X += Dir[0]
                    Y += Dir[1]
                    Z += Dir[2]
                    W += Dir[3]
                    self.Maze[(X,Y,Z,W)] = Contents.Space
                    NewDistance = OldDistance + 2
                    Distance[(X,Y,Z,W)] = NewDistance 
                    if (NewDistance > FarthestDistance):
                        FarthestPoint = (X, Y, Z, W)
                        FarthestDistance = NewDistance
                    self.Backtrack[(X, Y, Z, W)] = MazeDirs.OppositeDir[Dir]
                    Moved = 1
                    ##print "Forward!  Moved:", Dir
                    break
                else:
                    Dirs = Dirs[1:]
                    if len(Dirs)==0:
                        # Dead end!
                        self.Maze[(X, Y, Z, W)] = Contents.DeadEnd
                        break
            if Moved:
                continue
            # Ok: We've been forced to BACKTRACK.
            Dir = self.Backtrack[(X, Y, Z, W)]
            if Dir==None:
                break # we're back home!
            X += Dir[0]*2
            Y += Dir[1]*2
            Z += Dir[2]*2
            W += Dir[3]*2
            ##print "Back!"
        # Place the exit:
        print "Exit goes at the farthest point:", FarthestPoint, FarthestDistance
        self.Maze[FarthestPoint] = Contents.Exit
    def ExitMaze(self):
        Music.FadeOut()
        Str = "At last!  You find the High Priestess, and - after dispatching her non-euclidean guards - \
        release her from her shackles.  She quickly opens a phase gate back to the palace.  \n\nYou use \
        <CN:YELLOW>Ariadne's Thread as a shortcut back out of the tower."
        try:
            del Global.Party.KeyItemFlags["Ariadne's Thread"]
        except:
            pass
        Global.Party.EventFlags["L8Tower"] = 1
        Global.App.ShowNewDialog(Str)
        Global.App.PopScreen(self)
    def HandleKeyPressed(self, Key):
        # Called when the player presses a key.
        Dir = KeysToDirs.get(Key, None)
        if Dir==None:
            return
        self.TryMove(Dir)
    def TryMove(self, Dir):
        NextContents = self.Maze.get((self.X + Dir[0], self.Y + Dir[1],
                                      self.Z + Dir[2], self.W + Dir[3]), Contents.Wall)
        NextContents2 = self.Maze.get((self.X + Dir[0]*2, self.Y + Dir[1]*2,
                                      self.Z + Dir[2]*2, self.W + Dir[3]*2), Contents.Wall)
        
        if NextContents2 == Contents.Exit and NextContents == Contents.Space:
            self.ExitMaze()
            return
        if NextContents in (Contents.Space, Contents.DeadEnd):
            # Move!
            if Dir in (MazeDirs.North, MazeDirs.Up, MazeDirs.Znort):
                self.PlayerSprite.ChangeState("North")
            elif Dir in (MazeDirs.South, MazeDirs.Down, MazeDirs.Flurple):
                self.PlayerSprite.ChangeState("South")
            elif Dir == MazeDirs.East:
                self.PlayerSprite.ChangeState("East")
            elif Dir == MazeDirs.West:
                self.PlayerSprite.ChangeState("West")
            self.X += Dir[0]*2
            self.Y += Dir[1]*2
            self.Z += Dir[2]*2
            self.W += Dir[3]*2
##            print "After the step:"
##            print self.X, self.Y, self.Z, self.W
            Resources.PlayStandardSound("Step.wav")
            self.DrawMaze()
        else:
            Resources.PlayStandardSound("Bonk.wav")
    def DrawMaze(self):
        for Sprite in self.WallSprites.sprites():
            Sprite.kill()
        for Index in range(len(XDirs)):
            Dir = MazeDirs.AllDirs[Index]
            NextContents = self.Maze.get((self.X + Dir[0], self.Y + Dir[1],
                                          self.Z + Dir[2], self.W + Dir[3]), Contents.Wall)
            NextContents2 = self.Maze.get((self.X + Dir[0]*2, self.Y + Dir[1]*2,
                                          self.Z + Dir[2]*2, self.W + Dir[3]*2), Contents.Wall)
            ##print Dir, NextContents
            if NextContents == Contents.Wall:
                Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "BigMaze", "Wall.png"))
            elif NextContents2 == Contents.Exit:
                print "WE SEE AN EXIT!!"
                Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "BigMaze", "Exit.png"))
                
            elif NextContents in (Contents.Space, Contents.DeadEnd):
                Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "BigMaze", "Floor.png"))
            else:
                Image = Resources.GetImage(os.path.join(Paths.ImagesMisc, "BigMaze", "Wall.png"))
            X = 400 + XDirs[Index] * LineEnd
            Y = MainCenterY + YDirs[Index] * LineEnd
            Sprite = GenericImageSprite(Image, X, Y)
            Sprite.rect.top -= Sprite.rect.height / 2
            Sprite.rect.left -= Sprite.rect.width / 2
            Sprite.Dir = Dir
            self.AddForegroundSprite(Sprite)
            self.WallSprites.add(Sprite)
        self.Redraw()
    def HandleMouseClickedHere(self, Position, Button):
        if Button != EVENT_BUTTON_LEFT_CLICK:
            return
        Dummy = DummySprite(pygame.Rect(Position[0],Position[1],1,1))
        # First, look for equipment taking-off:
        Sprite = pygame.sprite.spritecollideany(Dummy,self.ButtonSprites)
        if Sprite:
            Global.App.ShowNewDialog("You look at out Ariadne's thread, and consider escaping this place of lies...\n\nGive up?", ButtonGroup.YesNo, Callback = self.FleeCallback)
            return
        # Look for clicks on the floors:
        Sprite = pygame.sprite.spritecollideany(Dummy, self.WallSprites)
        if Sprite:
            self.TryMove(Sprite.Dir)
    def FleeCallback(self):
        Global.App.ShowNewDialog("You tug on the thread, and are magically whisked back out of the tower.\n\n(You hear a <CN:RED>horrid grinding noise</C> behind you.  It seems the maze has shifted around again...)")
        Global.App.PopScreen(self)
        