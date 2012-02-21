import pygame
import os
import sys
import types
from pygame.locals import *
from lock import *
import ChestScreen
import Resources
from Utils import *
import Global

DEBUG = 0
IMAGE_SIZE = 64
GRID_WIDTH = 3
GRID_HEIGHT = 3
OFF = 0
ON = 1
BLUE = 2
BLINK = 5
STROBE = 3
RETURN = 4

NINJA_MULTIPLIER = 1.3

LightsImages = {}
def GetLightImages():
    Dir = os.path.join("Images", "Traps", "LightsOut")
    LightsImages["Red"] = Resources.GetImage(os.path.join(Dir,"Red"))
    LightsImages["Green"] = Resources.GetImage(os.path.join(Dir,"Green"))
    LightsImages["Blue"] = Resources.GetImage(os.path.join(Dir,"Blue"))
    LightsImages["GR"] = []
    for Index in range(9):
        LightsImages["GR"].append(Resources.GetImage(os.path.join(Dir,"GR%d"%Index)))
    LightsImages["RB"] = []
    for Index in range(9):
        LightsImages["RB"].append(Resources.GetImage(os.path.join(Dir,"RB%d"%Index)))
    LightsImages["BG"] = []
    for Index in range(9):
        LightsImages["BG"].append(Resources.GetImage(os.path.join(Dir,"BG%d"%Index)))
    LightsImages[OFF] = LightsImages["Green"]
    LightsImages[ON] = LightsImages["Red"]
    LightsImages[BLUE] = LightsImages["Blue"]
    LightsImages[(OFF, ON)] = LightsImages["GR"]
    LightsImages[(ON, OFF)] = LightsImages["GR"][:]
    LightsImages[(ON, OFF)].reverse()
    LightsImages[(OFF, BLUE)] = LightsImages["RB"]
    LightsImages[(BLUE, OFF)] = LightsImages["RB"][:]
    LightsImages[(BLUE, OFF)].reverse()
    LightsImages[(BLUE, ON)] = LightsImages["BG"]
    LightsImages[(ON, BLUE)] = LightsImages["BG"][:]
    LightsImages[(ON, BLUE)].reverse()
    
class LightSprite(pygame.sprite.Sprite):
    """Simple light"""
    def __init__(self, size, IsTriState = 0, length = 9, speed = 1.0):
        global IMAGE_SIZE 
        IMAGE_SIZE = size
        self.IsTriState = IsTriState
        pygame.sprite.Sprite.__init__(self)
        self.images = LightsImages
        self.state = OFF
        self.nextstate = OFF
        self.BlinkFlag = 0
        self.framelength = float(speed)/length
        self.changing = 0
        self.currentframe = 0
        self.TotalFrames = length
        self.blinkdirection = 0
##        for index in range(length):
##            FilePath = os.path.join("Images", "Traps", "LightsOut", "button%d%d.png"%(size, index))
##            im = Resources.GetImage(FilePath)
##            #im, rec = load_image("button%d%d.png"%(size, index))
##            self.images.append(im)
        self.image = self.images["Green"]
        self.rect = self.image.get_rect()

    def toggle(self):
        if self.IsTriState:
            if (self.state == ON):
                self.nextstate = BLUE
                Diff = 0
            elif self.state == BLUE:
                self.nextstate = OFF
                Diff = -1
            else:
                self.nextstate = ON
                Diff = 1
        else:
            if (self.state == ON):
                self.nextstate = OFF
                Diff = -1
            else:
                self.nextstate = ON
                Diff = 1
        self.currentframe = 0
        return Diff
    def highlight(self):
        return #%%%
        self.nextstate = BLINK
        if self.state == ON:
            self.blinkdirection = -1
        else:
            self.blinkdirection = 1
        
    def ForceUpdate(self):
        self.image = self.images[self.state]
        Dirty(self.rect)    
        
    def update(self):
        if (self.state == self.nextstate):        # if there is no update for this
            return
        if self.currentframe >= self.TotalFrames - 1:
            self.state = self.nextstate
            self.image = self.images[self.state]
        else:
            if self.BlinkFlag:
                self.currentframe += self.BlinkDir
                if self.currentframe == 0:
                    self.BlinkDir = 1
                elif self.currentframe == 5:
                    self.BlinkDir = -1
            else:
                self.currentframe += 1
            self.image = self.images[(self.state, self.nextstate)][self.currentframe]
        Dirty(self.rect)    
##            
##        if ((self.nextstate == ON and self.currentframe == self.totalFrames - 1) or
##            (self.nextstate == OFF and self.currentframe == 0)):
##            self.state = self.nextstate
##            #self.kill()
##            return            
##        if (self.nextstate == ON):                  # Turn a light on
##            self.currentframe += 1
##            if (self.currentframe < 0):
##                self.currentframe = 0
##        elif (self.nextstate == OFF):               # Turn a light off
##            self.currentframe -= 1
##            if (self.currentframe > self.totalFrames - 1):
##                self.currentframe = self.totalFrames - 1
##        elif (self.nextstate == BLINK):             # cause the light to blink
##            self.currentframe += self.blinkdirection
##            if (self.currentframe == 5 or
##                self.currentframe == 0 or
##                self.currentframe == self.totalFrames - 1):
##                self.blinkdirection = -(self.blinkdirection)
##        elif (self.nextstate == RETURN):
##            if (self.state == ON):
##                target = 10
##                self.blinkdirection = 1
##            else:
##                target = 0
##                self.blinkdirection = -1
##            if (self.currentframe == 0 or self.currentframe == 10):
##                self.nextstate = self.state
##                #self.kill()
##                return
##            self.currentframe += self.blinkdirection
##        elif (self.nextstate == STROBE):
##            if DEBUG:
##                print "strobing light - current frame: %d" % (self.currentframe)
##            if (self.blinkdirection == 1 and self.currentframe == 10):    # reverse direction
##                self.blinkdirection = -1
##            self.currentframe += self.blinkdirection
##            if (self.blinkdirection == -1 and self.currentframe == 0):  # done strobing
##                if DEBUG:
##                    print "Resetting state: blinkdirection: %d, currentframe: %d" % (self.blinkdirection, self.currentframe)
##                #self.kill()
##                self.set(OFF)
##        self.image = self.images[self.currentframe]
##        Dirty(self.rect)
        
    def startStrobe(self):
        if (self.nextstate == OFF):
            self.blinkdirection = 1
            self.nextstate = STROBE
    
    def place(self, location, lock, x, y):
        self.number = location + 1
        row = location / lock.width
        col = location % lock.width
        self.rect.topleft = (col * IMAGE_SIZE + x, row * IMAGE_SIZE + y)

    def set(self, state):
        if (state == OFF):
            self.image = self.images[OFF]
        elif (state == ON):
            self.image = self.images[ON]
        elif (state == BLUE):
            self.image = self.images[BLUE]
        self.currentframe = 0
        self.state = state
        self.nextstate = state
            
WidthsByLevel = [1, 3, 3, 3, 4, 4,
                 4, 4, 5, 5, 5,
                 6, 6, 6]
HeightsByLevel = [1, 3, 3, 3, 3, 3,
                  4, 4, 4, 4, 5,
                  6, 6, 6]
EaseByLevel = [1, 0, 1, 0, 1, 0,
               1, 0, 1, 0, 1,
               6, 3, 0]

TimeByLevel = [1, 20, 30, 40, 50, 60,
               70, 80, 90, 100, 110,
               120, 130, 140]
                  

class PlayingBoard(ChestScreen.TrapPanel):
    "Lights out" # docstring is displayed to user on Calfo
    def __init__(self, *args, **kw):
        ChestScreen.TrapPanel.__init__(self, *args, **kw)
        self.lightsGroup = pygame.sprite.RenderPlain()
        self.lights = []
        self.Tick = 0
        GetLightImages()
        self.clock = pygame.time.Clock()
        self.blinkingLight = -1
        self.strobing = -1
        self.lightson = 0
        self.IsTriState = 0
        if type(self.DungeonLevel) == types.IntType:
            self.InitFromDungeonLevel(self.DungeonLevel)
        else:
            self.InitFromPuzzle(self.DungeonLevel)
        LightsWidth = IMAGE_SIZE * self.GridWidth
        self.LightsX = (self.Width - LightsWidth) / 2
        LightsHeight = IMAGE_SIZE * self.GridHeight
        self.LightsY = (self.Height - LightsWidth) / 2
        if self.HasNinja:
            self.TimeLimit *= NINJA_MULTIPLIER
        self.UpdateLightsFromGrid()
    def UpdateLightsFromGrid(self):
        "Kill any existing lightsprites, and create lightsprites in synch with the lock."
        for Light in self.lightsGroup.sprites():
            Light.kill()
        self.lights = []
        self.lightson = 0
        for i in range(self.GridWidth*self.GridHeight):
            light = LightSprite(IMAGE_SIZE, self.IsTriState)
            light.place(i, self.lock, self.LightsX, self.LightsY)
            st = self.lock.getLight(i+1)
            light.set(st)
            self.lightson += min(st,1)
            self.lights.append(light)
            self.lightsGroup.add(light)
            self.AddForegroundSprite(light)
    def InitFromDungeonLevel(self, Level):
        self.GridWidth = WidthsByLevel[self.DungeonLevel]
        self.GridHeight = HeightsByLevel[self.DungeonLevel]
        self.lock = Grid(self.GridWidth,self.GridHeight)
        Ease = EaseByLevel[self.DungeonLevel]        
        self.lock.randomize(Ease)
        self.TimeLimit = TimeByLevel[self.DungeonLevel]
    def GetPuzzleState(self):
        Grid = {}
        for X in range(self.GridWidth):
            for Y in range(self.GridHeight):
                Grid[(X,Y)] = self.lock.getLight(1 +Y*self.GridWidth + X)
        return Grid
    def InitFromPuzzle(self, Puzzle):
        self.GridWidth = Puzzle.Width
        self.GridHeight = Puzzle.Height
        self.lock = Grid(Puzzle.Width, Puzzle.Height)
        if Puzzle.Type == "RGB":
            self.IsTriState = 1
        for X in range(Puzzle.Width):
            for Y in range(Puzzle.Height):
                self.lock.setLight(1 + Y*Puzzle.Width + X, Puzzle.InitialLights[(X, Y)])
    def ShowInstructions(self):
        Global.App.ShowNewDialog("Turn all of the lights to green.  Click a light to toggle it, and the 4 lights next to it.", Callback = self.Start)

        return
    def Start(self):            
        self.Redraw()
        self.Update()
        self.lightsGroup.draw(self.BackgroundSurface)
        self.lightsGroup.empty()
        Dirty((self.BlitX,self.BlitY,self.Width,self.Height))        
        self.Master.StartTimer()
    
    def setLights(self):
        for i in range(len(self.lights)):
            self.lights[i].set(self.lock.getLight(i+1))
            
    def blinkLight(self, number):
        self.clearBlink()
        number -= 1
        self.lights[number].highlight()
        self.blinkingLight = number
        self.lightsGroup.add(self.lights[number])

    def clearBlink(self):
        if (self.blinkingLight != -1):              # i.e. already have a light blinking
            blight = self.lights[self.blinkingLight]
            blight.nextstate = RETURN
            self.blinkingLight = -1

    def InitTrap(self):
        pass    
    
    def Update(self):
        self.Tick = (self.Tick+1)%1000
        if self.Tick%2==0:
            self.lightsGroup.update()
    def HandleMouseClickedHere(self, Position, Button):
        (x, y) = Position
        if DEBUG:
            print x, y
        self.clearBlink()                           # stop blinking
        for lt in self.lightsGroup.sprites():       # for all of the current groups
            if (lt.nextstate != RETURN):
                #lt.state = lt.nextstate
                lt.currentframe = lt.TotalFrames # jump to the next color
                lt.state = lt.nextstate #%%%
                lt.ForceUpdate() 
                #lt.nextstate = RETURN #%%%
        row = (y - self.LightsY) / IMAGE_SIZE
        col = (x - self.LightsX) / IMAGE_SIZE
        if DEBUG:
            print col, row
        if (row<0 or row>=self.lock.height):
            return
        if (col<0 or col>=self.lock.width):
            return
        location = self.lock.width * row + col + 1
        changed = self.lock.evalClick(location)
        #print "Lights on was:", self.lightson
        for light in changed:
            lt = self.lights[light-1]
            self.lightson += lt.toggle()
            self.lightsGroup.add(lt)
        #print "Lights on is now:", self.lightson    
        return 1 # Yes, a move!
        if DEBUG:
            print self.lock
            print

    def IsDisarmed(self):
        return (self.lightson == 0) #and (len(self.lightsGroup.sprites()) == 0))
    def kill(self):
        "Cleanup!"
        for Sprite in self.BackgroundSprites.sprites():
            Sprite.kill()
        for Sprite in self.ForegroundSprites.sprites():
            Sprite.kill()

def main():
    pygame.init()

    if len(sys.argv) == 2:
        GRID_WIDTH = int(sys.argv[1])
        GRID_HEIGHT = int(sys.argv[1])
    elif len(sys.argv) == 3:
        GRID_WIDTH = int(sys.argv[1])
        GRID_HEIGHT = int(sys.argv[2])

    screen = pygame.display.set_mode(((GRID_WIDTH * IMAGE_SIZE),(GRID_HEIGHT * IMAGE_SIZE)))
    myboard = PlayingBoard(screen, GRID_WIDTH, GRID_HEIGHT)
    
    while (not(myboard.cleared())):
        myboard.clock.tick(30)
        for event in pygame.event.get():
            if event.type is QUIT:
                return
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    move, movesLeft = myboard.lock.nextMove(0)
                else:
                    move, movesLeft = myboard.lock.nextMove()
                #print "Next move: %d with %d moves left." % (move, movesLeft)
                myboard.blinkLight(move)
            if event.type is MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                myboard.receiveClick(x,y)
        myboard.draw()
    print "Solved in %d clicks." % (myboard.lock.clicks)
        
if __name__=='__main__':
    main()



