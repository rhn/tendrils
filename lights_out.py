import pygame, os, sys
from pygame.locals import *
from lock import *
import time

class Constants:
    DEBUG = 0
    IMAGE_SIZE = 64
    GRID_WIDTH = 3
    GRID_HEIGHT = 3
    OFF = 0
    ON = 1
    BLINK = 2
    STROBE = 3
    UNCHANGED = 4

def load_image(name):
    fullname = os.path.join('data',name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    return image, image.get_rect()


class LightSprite(pygame.sprite.Sprite):
    """Simple light"""

    images = []                                                         # Class-wide list of image objects
    totalFrames = 0                                                     # class-wide length of animation sequence
    def __init__(self, size, length = 11, speed = 1.0):
        pygame.sprite.Sprite.__init__(self)                             # initialize sprite object
        self.state = Constants.OFF                                      # initially set to OFF
        self.nextstate = Constants.UNCHANGED                            # initially set next state to UNCHANGED
        self.timeToKill = 1                                             # Value for determining how many frames before killing from sprite group
        self.currentframe = 0                                           # index of current OFF image
        self.direction = 1                                              # sets the light to blink upwards
        self.number = -1                                                # this value gets assigned a light number when the light is placed.
        if not self.images:                                             # if we haven't already loaded the images
            LightSprite.totalFrames = length                            # total number of frames in sequence
            for index in range(length):                                 # load images
                im, rec = load_image("button%d%d.bmp"%(size, index))
                self.images.append(im)
        self.image = self.images[0]                                     # set the image to off
        self.rect = self.images[0].get_rect()                           # set the rectangle to the image's rectangle

    def highlight(self):
        self.nextstate = Constants.BLINK        # set next state to BLINK
        if self.state == Constants.ON:          # if the light is on, 
            self.direction = -1                 # blinking (initially) goes down
        else:
            self.direction = 1                                          # otherwise blinking (initially) goes up
        self.timeToKill = -1                                            # set timeToKill to -1, so it NEVER reaches 0

    def place(self, location, lock):
        """Receives 0-indexed light location and
           the lock object to determine grid size"""
        self.number = location + 1                                      # assign the light number to the light object
        row = location / lock.width                                     # calculate which row the light is on
        col = location % lock.width                                     # calculate which col the light is in
        self.rect.topleft = (col * Constants.IMAGE_SIZE, row * Constants.IMAGE_SIZE)    # Move rectangle
        
    def set(self, state):
        if (state == Constants.OFF):                        # if target state is OFF
            self.image = self.images[0]                     # set frame to off (first) frame
            self.currentframe = 0                           # indicate current frame value
            self.direction = 1                              # direction of change is increased frame values
        elif (state == Constants.ON):                       # if target state is ON
            self.image = self.images[LightSprite.totalFrames - 1]  # set frame to on (last) frame
            self.currentframe = LightSprite.totalFrames - 1        # indicate current frame value
            self.direction = -1                             # direction of change is decreased frame values
        self.state = state                                  # set the current state to target state
        self.nextstate = Constants.UNCHANGED                # set next state to UNCHANGED
        self.timeToKill = 1                                 # force a drawing (one frame before kill)
        
    def startStrobe(self):
        self.currentframe = 0                       # set initial frame to 0
        self.nextstate = Constants.STROBE           # set state to strobe
        self.timeToKill = 21                        # set number of frames to refresh
        self.direction = 1
    
    def toggle(self):
        if (self.state == Constants.ON):                    # if current state is ON
            self.currentframe = LightSprite.totalFrames - 1        # force current frame to initial frame value
            self.image = self.images[LightSprite.totalFrames - 1]  # force image to jump to initial image in sequence
            self.nextstate = Constants.OFF                  # set next state to off
        else:                                               # current state is OFF
            self.currentframe = 0                           # force current frame to initial frame value
            self.image = self.images[0]                     # force image to jump to initial image in sequence
            self.nextstate = Constants.ON                   # otherwise set nextstate to on
        self.timeToKill = 10                                # set time to kill to animation length
        self.direction = -(self.direction)                  # reverse the direction
        
    def update(self):
        if self.timeToKill == 0:                        # if it's time to kill
            self.kill()                                 # remove from group
            if (self.nextstate == Constants.OFF or
                self.nextstate == Constants.ON):        # if next state is OFF or ON
                self.state = self.nextstate             # change state to target state
                self.nextstate == Constants.UNCHANGED   # change next state to UNCHANGED
            if (self.nextstate == Constants.BLINK):     # if the next state is blink
                self.nextstate = Constants.UNCHANGED    # set to unchanged
            if (self.nextstate == Constants.STROBE):    # If next state is STROBE
                self.nextstate = Constants.OFF          # if done strobing, set to off
            return
        if self.nextstate == Constants.UNCHANGED:       # if state is unchanged
            self.timeToKill = 0                         # set it to kill next refresh
            return
        if self.nextstate == Constants.OFF:             # if target state is off
            self.currentframe -= 1                      # move frame down
        elif self.nextstate == Constants.ON:            # if target state is ON
            self.currentframe += 1                      # move frame up
        elif self.nextstate == Constants.BLINK:         # if we're in BLINK mode
            self.currentframe += self.direction         # shift the current frame in blinkdirection
            if (self.currentframe == 5 or               # if we hit middle, or either appropriate end
                self.currentframe == 0  or
                self.currentframe == LightSprite.totalFrames - 1):
                self.direction = -(self.direction)      # reverse blink direction
        elif self.nextstate == Constants.STROBE:        # if we're in STROBE mode
            if (self.direction == 1 and self.currentframe == 10):  # reverse direction at the end
                self.direction = -1
            if (self.direction == -1 and self.currentframe == 0):    # end of cycle
                self.timeToKill = 1
                self.nextstate = Constants.OFF
            else:
                self.currentframe += self.direction
        self.image = self.images[self.currentframe]     # reassign image based on new current frame
        self.timeToKill -= 1                            # decrement number of refreshes
            

class PlayingBoard:
    def __init__(self, screen, w = 3, h = 3):
        self.screen = screen                                # define the board's canvas to draw to
        self.lock = Grid(w,h)                               # create a lock object
        self.lock.randomize()                               # randomize the lock
        self.lightsGroup = pygame.sprite.RenderPlain()      # create the light rendering group
        self.lights = []                                    # create list of lights
        self.blinkingLight = -1                             # index of currently blinking light (-1 implies no blinking light)
        self.strobing = -1                                  # determines strobing state: if we're strobing, this value is the index of the LAST light triggered
        self.lightson = 0                                   # counts the number of lights on
        for i in range(self.lock.size):                     # for each light
            light = LightSprite(Constants.IMAGE_SIZE)       # create a light
            light.place(i, self.lock)                       # place the light at the appropriate location
            st = self.lock.getLight(i+1)                    # get the state from the lock
            light.set(st)                                   # set the light to the acquired state
            self.lightson += st                             # (ON = 1, OFF = 0), increment number of lights on
            self.lights.append(light)                       # add the lights to the list of lights
            self.lightsGroup.add(light)                     # add the lights to the light rendering group
    
    def strobe(self):
        self.strobing = 0                                   # set the first light as the next light to strobe
        self.lights[0].startStrobe()                        # grab the first light and set it to strobing
        self.lightsGroup.add(self.lights[0])                # add strobing light to render group
        
    def blinkLight(self, number):
        if (self.blinkingLight == (number - 1)):        # if we need to blink the same light
            return                                      # do nothing
        self.clearBlink()                               # otherwise, clear the currently blinking light
        number -= 1                                     # get the zero-indexed light number
        self.lights[number].highlight()                 # set the light at that index to blink
        self.blinkingLight = number                     # set the board's blinking light to this light
        self.lightsGroup.add(self.lights[number])       # add the light to the rendering group

    def clearBlink(self):
        if (self.blinkingLight != -1):                  # i.e. already have a light blinking
            blight = self.lights[self.blinkingLight]    # grab the blinking light
            blight.set(blight.state)
            self.blinkingLight = -1                     # indicate we have no blinking light
            
    def draw(self):
        if (self.strobing != -1):                                       # check to see if we're strobing
            sl = self.lights[self.strobing]                             # grab the last light triggered
            if (sl.currentframe >= 3 and sl.direction == 1):       # light is three (or more) frames into the transition
                
                self.strobing = (self.strobing + 1) % self.lock.size    # grab the next light in the list
                self.lights[self.strobing].startStrobe()                # start that light strobing
                self.lightsGroup.add(self.lights[self.strobing])        # add the newly strobing light to the render group
        self.lightsGroup.update()                                       # call update on all sprites in group
        self.lightsGroup.draw(self.screen)                              # draw group to screen
        pygame.display.flip()                                           # flip the display

    def receiveClick(self, x, y):
        self.clearBlink()                           # stop blinking, force the light to jump to natural state
        for lt in self.lightsGroup.sprites():       # for all of the current groups
            if lt.nextstate == Constants.ON or lt.nextstate == Constants.OFF:
                lt.state = lt.nextstate
        row = y / Constants.IMAGE_SIZE              # find the row that was clicked on
        col = x / Constants.IMAGE_SIZE              # find the column that was clicked on
        location = self.lock.width * row + col + 1  # calculate the light number of the light clicked on
        changed = self.lock.evalClick(location)     # evaluate the click and receive a list of the changed lights
        for light in changed:                       # for each changed light number
            lt = self.lights[light-1]               # grab the light from the light list
            if (lt.state == Constants.ON):          # if the light WAS ON
                diff = -1                           # we'll be subtracting an "on" light
            else:                                   # if the light WAS OFF
                diff = 1                            # we'll be adding an "on" light
            self.lightson += diff                   # change the number of lights on
            self.lightsGroup.add(lt)                # add the changed light to the render group
            lt.toggle()                             # toggle the state of that light

    def cleared(self):
        # board is cleared if there are no lights on, and the sprite group is done drawing
        return ((self.lightson == 0) and (len(self.lightsGroup.sprites()) == 0))
        
def main():
    pygame.init()                                   # initialize pygame

    # read command line arguments for grid size
    if len(sys.argv) == 2:
        Constants.GRID_WIDTH = int(sys.argv[1])
        Constants.GRID_HEIGHT = int(sys.argv[1])
    elif len(sys.argv) == 3:
        Constants.GRID_WIDTH = int(sys.argv[1])
        Constants.GRID_HEIGHT = int(sys.argv[2])

    # initialize screen object and playing board object
    screen = pygame.display.set_mode(((Constants.GRID_WIDTH * Constants.IMAGE_SIZE),(Constants.GRID_HEIGHT * Constants.IMAGE_SIZE)))
    myboard = PlayingBoard(screen, Constants.GRID_WIDTH, Constants.GRID_HEIGHT)
    myboard.draw()                                                                  # force a draw to screen
    gameclock = pygame.time.Clock()                                                 # create pygame clock
    start = time.clock()                                                            # begin timing length of game
    while (not(myboard.cleared())):                                                 # while there are still things to d on the board
        gameclock.tick(30)                                                          # no faster than 30 ticks/sec
        for event in pygame.event.get():                                            # grab events
            if event.type is QUIT:                                                  # close program
                return
            if event.type is KEYDOWN:                                               # keyboard stroke
                if not(myboard.lock.solved()):                                      # make sure board isn't solved (catches fast double-click at end of game)
                    if event.key is K_ESCAPE:                                       # ninja help key
                        move, movesLeft = myboard.lock.nextMove(0)                  # returns ordered help
                    else:                                                           # normal help
                        move, movesLeft = myboard.lock.nextMove()                   # returns random help
                    #print "Next move: %d with %d moves left." % (move, movesLeft)   # output help
                    #print myboard.lock                                              # print matrix for grid
                    myboard.blinkLight(move)                                        # cause the appropriate light to blink
            if event.type is MOUSEBUTTONDOWN:                                       # if there's a click
                x,y = pygame.mouse.get_pos()                                        # grab the mouse position info
                myboard.receiveClick(x,y)                                           # pass it to the board for evaluation
        myboard.draw()                                                              # refresh drawing
    stop = time.clock()                                                             # stop timer for game length
    # output games stats
    print "Time to solve:", (stop - start)
    print "Calls to help:", myboard.lock.helps
    print "Total clicks:" , myboard.lock.clicks
    
    gameclock.tick(5)                                                               # slight pause
    myboard.strobe()                                                                # begin strobing
    while (1):                                                                      # continuously strobe
        gameclock.tick(45)                                                          # slow strobe
        for event in pygame.event.get():
            if event.type is QUIT:                                                  # allow graceful quit
                return
        myboard.draw()                                                              # refresh board
    
        
if __name__=='__main__':
    main()



