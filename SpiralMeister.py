# Get spiral or circle coordinates
import math
from Utils import *
from Options import *
from BattleSprites import *
import Resources
import cPickle

def Spiral(TotalTicks, StartingRadius, TicksPerRevolution, CenterX = 0, CenterY = 0):
    Coords = []
    for Tick in range(TotalTicks):
        Angle = Tick * (math.pi * 2) / float(TicksPerRevolution)
        ##print "Tick %d angle %f (%f)"%(Tick, Angle, Angle * 180/math.pi)
        Radius = StartingRadius * (1 - (Tick / float(TotalTicks)))
        X = CenterX + Radius * math.cos(Angle)
        Y = CenterY - Radius * math.sin(Angle)
        Coords.append((int(X),int(Y)))
    return Coords

def Circle(TotalTicks, Radius, TicksPerRevolution, XMult = 1.0, YMult = 1.0, CenterX = 0, CenterY = 0):
    Coords = []
    for Tick in range(TotalTicks):
        Angle = Tick * (math.pi * 2) / float(TicksPerRevolution)
        ##print "Tick %d angle %f (%f)"%(Tick, Angle, Angle * 180/math.pi)
        ##Radius = StartingRadius * (1 - Tick / float(TotalTicks))
        X = CenterX + XMult * 0.7 * Radius * math.cos(Angle)
        Y = CenterY - YMult * 0.7 * Radius * math.sin(Angle)
        Coords.append((int(X),int(Y)))
    return Coords

def CutePrint(Coords):
    Str = "["
    for Coord in Coords:
        Str += str(Coord)+","
        if len(Str)>60:
            print Str
            Str = ""
    print Str+"]"

def CycleList(List, Count = 1):
    for Cycle in range(Count):
        X = List[0]
        del List[0]
        List.append(X)

def GetZergImages():
    Images = []    
    for ImageIndex in range(1,6):
        Image = Resources.GetImage(os.path.join(Paths.Images, "Magic", "work", "Zergling%d.png"%(ImageIndex)))
        Image.set_colorkey(Colors.Black) 
        Images.append(Image)
    ImagesB = []    
    for ImageIndex in range(1,6):
        Image = Resources.GetImage(os.path.join(Paths.Images, "Magic", "work", "Zergling%db.bmp"%(ImageIndex)))
        Image.set_colorkey(Colors.Black) 
        ImagesB.append(Image)
    return [Images, ImagesB]

ZergImageCount = 16

AnimationFrames = [0,1,2,3,4,3,2,1]    
# Zergling image work:
def Zergify(Screen, Index):
    (ZergImages, ZergImagesB) = GetZergImages()
    ZergCoords = []
    #
    Coords = Circle(ZergImageCount, 30, ZergImageCount)
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 30, ZergImageCount)
    CycleList(Coords, ZergImageCount/2)
    Coords.reverse()
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 40, ZergImageCount)
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 40, ZergImageCount)
    CycleList(Coords, ZergImageCount/2)
    Coords.reverse()
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 50, ZergImageCount)
    CycleList(Coords, ZergImageCount / 4)
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 50, ZergImageCount)
    CycleList(Coords, ZergImageCount / 3)    
    Coords.reverse()
    ZergCoords.append(Coords)    
    #
    Coords = Circle(ZergImageCount, 60, ZergImageCount)
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 60, ZergImageCount)
    CycleList(Coords, ZergImageCount / 2)
    CycleList(Coords)
    Coords.reverse()
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 70, ZergImageCount)
    CycleList(Coords, 2 * (ZergImageCount / 3))
    ZergCoords.append(Coords)    
    
    #
    Coords = Circle(ZergImageCount, 20, ZergImageCount)
    Coords.reverse()
    ZergCoords.append(Coords)
    #
    Coords = Circle(ZergImageCount, 40, ZergImageCount, 0.5, 2.0)
    ZergCoords.append(Coords)
    ##
    Coords = Circle(ZergImageCount, 40, ZergImageCount, 0.7, 1.8)
    Coords.reverse()
    ZergCoords.append(Coords)
    ##
    Coords = Circle(ZergImageCount, 40, ZergImageCount, 1.5, 0.2)
    CycleList(Coords)
    CycleList(Coords)
    CycleList(Coords)
    Coords.reverse()
    ZergCoords.append(Coords)
    ##
    Coords = Circle(ZergImageCount, 40, ZergImageCount, 1.3, 0.2)
    ZergCoords.append(Coords)
    
    for ZergIndex in range(len(ZergCoords)):
        Zerg = ZergCoords[ZergIndex]
        ##print "ZERG!", Zerg
        AnimationFrame = AnimationFrames[(Index + ZergIndex)%len(AnimationFrames)]
        Position = Zerg[Index % len(Zerg)]
        print "BLIT: %d,%d"%(Position[0]+100, Position[0]+100)
        ZergWidth = ZergImages[0].get_rect().width
        ZergHeight= ZergImages[0].get_rect().height
        if ZergIndex%2:
            Screen.blit(ZergImages[AnimationFrame],
                        (100 - ZergWidth/2 +Position[0], 100 - ZergHeight/2 +Position[1]))
        else:
            Screen.blit(ZergImagesB[AnimationFrame],
                        (100 - ZergWidth/2 +Position[0], 100 - ZergHeight/2 +Position[1]))


def GetShivaPositions():
    MaxIndex = 700
    List = []
    for Index in range(MaxIndex):
        Angle = Index * (math.pi / 95)
        X = 400 + 380 * math.cos(Angle)
        Y = 80 + Index * (450 / float(MaxIndex)) + 100 * math.sin(Angle)
        List.append((X, Y))
    File = open("Summon\\Shiva.dat", "wb")
    cPickle.dump(List, File)
    File.close()

if __name__ == "__main__":            
    GetShivaPositions()
    