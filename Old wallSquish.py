import pygame, os, sys
from pygame.locals import *
from SeanMatrix import *
import time

class Constants:
    X = 0
    Y = 1

class Raster(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        if isinstance(name, pygame.Surface):
            self.image = name
            self.rect = self.image.get_rect()
        else:
            self.image,self.rect = load_image(name)
        
def load_image(name):
    fullname = os.path.join('data',name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    return image, image.get_rect() 

def skew(source, tl, tr, bl, br, background = (255,0,0), ctl = None, ctr = None, cbl = None, cbr = None, near = 1, far = 1):
    left = min(tl[Constants.X], bl[Constants.X])                        # find left most extreme
    right = max(tr[Constants.X], br[Constants.X]) + 1                   # find width of image
    top = min(tl[Constants.Y], tr[Constants.Y])                         # find upper most value
    bottom = max(bl[Constants.Y], br[Constants.Y]) + 1                  # find lower most value
    width = right - left                                                # find width of image
    height = bottom - top                                               # find height of image
    output = pygame.Surface((width, height))                            # create surface to draw on
    output.fill(background)                                             # flood with white
    # shift coords to clipped area
    if left != 0:
        tl[Constants.X] -= left
        bl[Constants.X] -= left
        tr[Constants.X] -= left
        br[Constants.X] -= left
    if top != 0:
        tl[Constants.Y] -= top
        bl[Constants.Y] -= top
        tr[Constants.Y] -= top
        br[Constants.Y] -= top
    indicator = [-1 for i in range(width)]                              # tells us if pixel has been set
    l = tl - bl                                                         # left-side vector
    r = tr - br                                                         # right-side vector
    l_len = l.magnitude()                                               # find the length of the two vectors
    r_len = r.magnitude()
    ysteps = (max(l_len, r_len) + 1)                                    # number of parameter steps is the length of the longer vector
    ysteps_inv = 1.0 / ysteps
    deltaLX = (bl[Constants.X] - tl[Constants.X]) * ysteps_inv          # change in left-side x per parameter step
    deltaLY = (bl[Constants.Y] - tl[Constants.Y] + 1) * ysteps_inv  # change in left-side x per parameter step
    deltaRX = (br[Constants.X] - tr[Constants.X]) * ysteps_inv      # change in right-side x per parameter step
    deltaRY = (br[Constants.Y] - tr[Constants.Y] + 1) * ysteps_inv  # change in right-side x per parameter step
    if not ctr:
        owidth, oheight = source.image.get_size()               # get original image's height and width
    owidth -= 1
    oheight -= 1
    lx = tl[Constants.X]                                        # initialize values for for loop
    ly = tl[Constants.Y]
    rx = tr[Constants.X]
    ry = tr[Constants.Y]
    output.lock()
    for i in range(ysteps):                                     # for each vertical parameter step
        xsteps = int(rx - lx) + 1                               # find the number of horizontal steps
        xsteps_inv = 1.0 / xsteps
        tdy = (ry - ly) * xsteps_inv                        # find the change in y for the target image
        brightness_delta = (near - far) * xsteps_inv             # find the change in brightness
        brightness = near
        targety = ly                                            # set the starting target y-value
        targetx = int(lx)                                       # set the starting target x-value
        sourcey = int(oheight * i * ysteps_inv)              # find which row we're on from the source image
        sourcex = 0                                             # initialize source
        sdx = owidth * xsteps_inv                            # find the change in x in the SOURCE image
        for j in range(xsteps ):                                 # for each horizontal parameter step
            ty = int(round(targety))
            if indicator[targetx] < ty:              # Determine if this pixel has already been set
                try:
                    #%%%
                    #read_color = Vector(source.image.get_at((int(sourcex),sourcey)))
                    #WriteColor = (int(read_color.elements[0] * brightness), int(read_color.elements[1] * brightness),int(read_color.elements[2]) * brightness,read_color.elements[3])
                    ReadColor = source.image.get_at((int(sourcex),sourcey))
                    WriteColor = (int(ReadColor[0] * brightness), int(ReadColor[1] * brightness), int(ReadColor[2] * brightness), int(ReadColor[3]))
                    output.set_at((targetx,ty), WriteColor)                 # set the color in the new image
                    indicator[targetx] = ty
                except IndexError:
                    print "targetx: %d, targety: %d, sourcex: %d, sourcey: %d" % (targetx, ty, int(sourcex), sourcey)
            targetx += 1                                        # increment target x value
            targety += tdy                                      # increment target y value
            sourcex += sdx                                      # increment source x value -- for this line it's all the same y value
            brightness -= brightness_delta
        lx += deltaLX                                           # increment parameterized line values
        rx += deltaRX
        ly += deltaLY
        ry += deltaRY
    return output
  
    #f0s0 - can't do
    #     - brightness: near = 0.502 (not full width), far = 0.251
    #f1s0 - Vector([0,0]), Vector([92,94]), Vector([0, 372]), Vector([92, 279])
    #     - brightness: near = 0.251, far = 0.059
    #f1s1 - can't do
    #     - brightness: near = 0.137 (not full width), far = 0.114
    #f2s0 - Vector([0,0]), Vector([30,31]), Vector([0, 185]), Vector([30, 153])
    #     - brightness: near = 0.059, far = 0.016
    #f2s1 - Vector([0,0]), Vector([92,30]), Vector([0, 185]), Vector([92, 154])
    #     - brightness: near = 0.114, far = 0.027
    #f2s3 - can't do
    #     - brightness: near 0.098, far = 0.094
    #f3s0 - Vector([0,0]), Vector([14,14]), Vector([0, 123]), Vector([14, 108])
    #     - brightness: near 0.016, far = 0.004
    #f3s1 - Vector([44,15]), Vector([0, 124]), Vector([44, 109])
    #     - brightness: near 0.027, far = 0.004
    #f3s2 - Vector([0,0]), Vector([74,14]), Vector([0, 123]), Vector([74, 108])
    #     - brightness: near 0.09, far = 0.004


    
def main():
    pygame.init()                                   # initialize pygame
    screen = pygame.display.set_mode((512,512))
    
    im = Raster("wall.bmp")
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([92,94]), Vector([0, 372]), Vector([92, 279]), near = 1, far = .5)
    stop = time.clock()
    print "TIme elapsed", (stop-start)
    pygame.image.save(im2, "temp.bmp")
    return

WallCoords = [("f1s0", ((0,0), (92,94), (0,372), (92, 279)), 0.502, 0.251),
              ("f2s0", ((0,0), (30,31), (0,185), (30, 153)), 0.059, 0.016),
              ("flat1", ((138,38), (138+374,38), (139+374, 38+375), (138, 38+375)), 0.5, 0.5),
    ]

def SquishWalls(FileName):
    
    DirName = os.path.splitext(FileName)[0]
    try:
        os.makedirs(DirName)
    except:
        pass
    im = Raster("wall.bmp")
    for (Name, Coords, Near, Far) in WallCoords:
        im2 = skew(im, Vector(Coords[0]), Vector(Coords[1]), Vector(Coords[2]), Vector(Coords[3]), near = Near, far = Far)
        pygame.image.save(im2, os.path.join(DirName, "%s.bmp"%Name))

if __name__ == "__main__":
    #main()
    pygame.init()                                   # initialize pygame
    screen = pygame.display.set_mode((512,512))
    #import profile
    #profile.run("SquishWalls(sys.argv[1])")
    print time.clock()
    SquishWalls(sys.argv[1])
    print time.clock()