import pygame, os, sys
from pygame.locals import *
from SeanMatrix import *
import time

EmptyColor = (255,255,255)

class Constants:
    X = 0
    Y = 1

class BBox:
    def __init__(self, corner, w, h):
        self.corner = corner
        self.width = w
        self.height = h

    def inside(self, point):
        if (point[Constants.X] >= self.corner[Constants.X] and
            point[Constants.X] < (self.corner[Constants.X] + self.width) and
            point[Constants.Y] >= self.corner[Constants.Y] and
            point[Constants.Y] < (self.corner[Constants.Y] + self.height)):
            return 1
        return 0

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

def shrink(source, width, height, brightness):
    output = pygame.transform.scale(source.image, (width, height))
    shader = pygame.Surface((width, height))
    shader.fill((0,0,0))
    shader.set_alpha(int((1 - brightness) * 255))
    output.blit(shader,(0,0))

    return output    

def skew(source, tl, tr, bl, br, background = (255,0,0), cliptl = None, clip_width = None, clip_height = None, near = 1, far = 1):
    # first remove the white space around the quad and shift values accordingly
    left = min(tl[Constants.X], bl[Constants.X])                        # find left most extreme
    right = max(tr[Constants.X], br[Constants.X]) + 1                   # find width of image
    top = min(tl[Constants.Y], tr[Constants.Y])                         # find upper most value
    bottom = max(bl[Constants.Y], br[Constants.Y]) + 1                  # find lower most value
    if left != 0:
        print "shifting left"
        tl[Constants.X] -= left
        bl[Constants.X] -= left
        tr[Constants.X] -= left
        br[Constants.X] -= left
        cliptl[Constants.X] -= left
    if top != 0:
        print "shifting down"
        tl[Constants.Y] -= top
        bl[Constants.Y] -= top
        tr[Constants.Y] -= top
        br[Constants.Y] -= top
        cliptl[Constants.Y] -= top

    # determine size of output image -- on clip if it exists, otherwise on bound        
    bound = None
    width = right - left                                                # find width of image
    height = bottom - top
    if (cliptl and clip_width and clip_height):
        bound = BBox(cliptl, clip_width, clip_height)                    # find clip bounding box    
    if bound:
        # if a clipping box exists, make it the size of the clipping rectangle
        output = pygame.Surface((clip_width, clip_height))
        brightness_delta = (near - far) / bound.width       # if clipping, shade over the clipped area
        shader = [(near - (i * brightness_delta)) for i in range(bound.width + 1)]
        print "BBox corner: (%d, %d)" % (bound.corner[0], bound.corner[1])
        print "Bbox size: (%d, %d)" % (bound.width, bound.height)
    else:
        output = pygame.Surface((width, height))                        # create surface to draw on
        print "No bounding box"
    output.fill(background)                                             # flood with white

    #print "Image size: (%d, %d)" % (width, height)
    
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
    owidth, oheight = source.image.get_size()               # get original image's height and width
    owidth -= 1
    oheight -= 1
    lx = tl[Constants.X]                                        # initialize values for for loop
    ly = tl[Constants.Y]
    rx = tr[Constants.X]
    ry = tr[Constants.Y]
    output.lock()
    for i in range(int(ysteps)):                                     # for each vertical parameter step
        xsteps = int(rx - lx) + 1                               # find the number of horizontal steps
        xsteps_inv = 1.0 / xsteps
        tdy = (ry - ly) * xsteps_inv                        # find the change in y for the target image
        if not bound:                                       # if there's no bound, brightness changes with line
            brightness_delta = (near - far) * xsteps_inv             # find the change in brightness
        brightness = near
        targety = ly                                            # set the starting target y-value
        targetx = int(lx)                                       # set the starting target x-value
        sourcey = int(oheight * i * ysteps_inv)              # find which row we're on from the source image
        sourcex = 0                                             # initialize source
        sdx = owidth * xsteps_inv                            # find the change in x in the SOURCE image
        for j in range(xsteps ):                                 # for each horizontal parameter step
            ty = int(round(targety))
            if bound:
                if (bound.inside((targetx, ty))):   # if the pixel is inside the clipped area
                    if indicator[targetx] < ty:              # Determine if this pixel has already been set
                        try:
                            horz = targetx - bound.corner[Constants.X] 
                            brightness = shader[horz]
                            read_color = source.image.get_at((int(sourcex),sourcey))
                            write_color = (int(read_color[0] * brightness), int(read_color[1] * brightness),int(read_color[2]) * brightness,read_color[3])
                            writex = targetx - bound.corner[0]
                            writey = ty - bound.corner[1]
                            output.set_at((writex,writey), write_color)                 # set the color in the new image
                            indicator[targetx] = ty
                            
                        except IndexError:
                            print "targetx: %d, targety: %d, sourcex: %d, sourcey: %d" % (targetx, ty, int(sourcex), sourcey)
            else:
                if indicator[targetx] < ty:              # Determine if this pixel has already been set
                    try:
                        read_color = source.image.get_at((int(sourcex),sourcey))
                        write_color = (int(read_color[0] * brightness), int(read_color[1] * brightness),int(read_color[2]) * brightness,read_color[3])
                        output.set_at((targetx,ty), write_color)                 # set the color in the new image
                        indicator[targetx] = ty
                        brightness -= brightness_delta
                    except IndexError:
                        print "targetx: %d, targety: %d, sourcex: %d, sourcey: %d" % (targetx, ty, int(sourcex), sourcey)
            targetx += 1                                        # increment target x value
            targety += tdy                                      # increment target y value
            sourcex += sdx                                      # increment source x value -- for this line it's all the same y value
            
        lx += deltaLX                                           # increment parameterized line values
        rx += deltaRX
        ly += deltaLY
        ry += deltaRY
    return output
  
    #f0s0 - Vector([0,0]), Vector([291,295]), Vector([0,936]), Vector([291,666])
    #   - clip (154,256), width = 138 height = 450
    #     - brightness: near = 1.0 (not full width), far = 0.513
    #f1s0 - Vector([0,0]), Vector([92,94]), Vector([0, 372]), Vector([92, 279])
    #     - brightness: near = 0.513, far = 0.507
    #f1s1 - Vector([0,0]), Vector([160,53]), Vector([0,290]), Vector([160,238])
    #     - clip (118, 39), width = 43, height = 215
    #     - brightness: near = 0.28 (not full width), far = 0.228
    #f2s0 - Vector([0,0]), Vector([30,31]), Vector([0, 185]), Vector([30, 153])
    #     - brightness: near = 0.507, far = 0.032
    #f2s1 - Vector([0,0]), Vector([92,30]), Vector([0, 185]), Vector([92, 154])
    #     - brightness: near = 0.228, far = 0.065
    #f2s2 - Vector([0,0]), Vector([133,28]), Vector([0,185]), Vector([133,151])
    #     - clip (124,27), width = 10, height = 127
    #     - brightness: near 0.2, far = 0.188
    #f3s0 - Vector([0,0]), Vector([14,14]), Vector([0, 123]), Vector([14, 108])
    #     - brightness: near 0.032, far = 0.008
    #f3s1 - Vector([0,0]), Vector([44,15]), Vector([0, 124]), Vector([44, 109])
    #     - brightness: near 0.065, far = 0.008
    #f3s2 - Vector([0,0]), Vector([74,14]), Vector([0, 123]), Vector([74, 108])
    #     - brightness: near 0.18, far = 0.008

    #flat0 - width = 374, height = 375
    #      - brightness 0.513
    #flat1 - width = 188, height = 186
    #      - brightness 0.507
    #flat2 - width = 126, height = 124
    #      - brightness 0.032
    #flat3 - width = 96, height = 96
    #      - brightness 0.008
    
def main(WallFileName, Suffix):
    pygame.init()                                   # initialize pygame
    screen = pygame.display.set_mode((512,512))
    #load image
    im = Raster(WallFileName)
    totaltime = 0
    # f0s0
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([291,295]), Vector([0,936]), Vector([291,666]), EmptyColor, (154,256), 138, 450, near = 1, far = 0.513)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f0s0%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f1s0
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([92,94]), Vector([0, 372]), Vector([92, 279]), EmptyColor, near = 0.513, far = 0.507)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f1s0%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f1s1
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([160,53]), Vector([0,290]), Vector([160,238]), EmptyColor, (118,39), 43, 215, near = 0.28, far = 0.228)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f1s1%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f2s0
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([30,31]), Vector([0, 185]), Vector([30, 153]), EmptyColor, near = 0.507, far = 0.032)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f2s0%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f2s1
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([92,30]), Vector([0, 185]), Vector([92, 154]), EmptyColor, near = 0.228, far = 0.065)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f2s1%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f2s2
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([133,28]), Vector([0,185]), Vector([133,151]), EmptyColor, (124,27), 10, 127, near = 0.2, far = 0.188)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f2s2%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f3s0
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([14,14]), Vector([0, 123]), Vector([14, 108]), EmptyColor, near = 0.032, far = 0.008)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f3s0%s.bmp"%Suffix)
    totaltime += (stop-start)

    # f3s1
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([44,15]), Vector([0, 124]), Vector([44, 109]), EmptyColor, near = 0.065, far = 0.008)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f3s1%s.bmp"%Suffix)
    totaltime += (stop-start)
        
    # f3s2
    start = time.clock()
    im2 = skew(im, Vector([0,0]), Vector([74,14]), Vector([0, 123]), Vector([74, 108]), EmptyColor, near = 0.18, far = 0.008)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "f3s2%s.bmp"%Suffix)
    totaltime += (stop-start)

    # flat0
    start = time.clock()
    im2 = shrink(im, 374, 375, 0.513)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "flat0%s.bmp"%Suffix)
    totaltime += (stop-start)

    # flat1
    start = time.clock()
    im2 = shrink(im, 188, 186, 0.507)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "flat1%s.bmp"%Suffix)
    totaltime += (stop-start)

    # flat2
    start = time.clock()
    im2 = shrink(im, 126, 124, 0.032)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "flat2%s.bmp"%Suffix)
    totaltime += (stop-start)

    # flat3
    start = time.clock()
    im2 = shrink(im, 96, 96, 0.008)
    stop = time.clock()
    print "Time elapsed", (stop-start)
    pygame.image.save(im2, "flat3%s.bmp"%Suffix)
    totaltime += (stop-start)    

    print "Total time for all squishing: ", totaltime    

    return

if __name__ == "__main__":
    #main()
    main(sys.argv[1],"")
    main(sys.argv[2],"d")