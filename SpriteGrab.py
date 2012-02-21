import Image
import os
import traceback
import random
import math
import sys
def GrabImages(Dir):
    for FileName in os.listdir(Dir):
        FullPath = os.path.join(Dir, FileName)
        TargetPath = os.path.splitext(FileName)[0] + ".png"
        try:
            GrabImage(FullPath, TargetPath)
        except:
            traceback.print_exc()


def OldGrabImage(FullPath, TargetPath):
    Im = Image.open(FullPath)
    (Width, Height) = Im.size
    Im = Im.convert("RGBA")
    for x in range(Width):
        for y in range(Height):
            p = Im.getpixel((x,y))
            #### print x, y, p #%%%
            if p[:3] == (0, 0, 0):
                p = (10, 10, 10, 255)
            if p == (255, 255, 255, 255) or p == (16, 248, 0, 255):
                p = (0,0,0,0)
##            if p[3]==0:
##                p = (0, 0, 0, 0)
            Im.putpixel((x,y), p)
    Im = Im.resize((50, 50))
    Im.save(TargetPath, "png")
        
def GrabImage(FullPath, TargetPath):
    Im = Image.open(FullPath)
    (Width, Height) = Im.size
    Im = Im.convert("RGBA")
    for x in range(Width):
        for y in range(Height):
            p = Im.getpixel((x,y))
            #### print x, y, p #%%%
            if p[:3] == (248, 252, 248):
                p = (255, 255, 255, 0)
##            if p == (255, 255, 255, 255) or p == (16, 248, 0, 255):
##                p = (0,0,0,0)
##            if p[3]==0:
##                p = (0, 0, 0, 0)
            Im.putpixel((x,y), p)
##    Im = Im.resize((50, 50))
    Im.save(TargetPath, "png")

def ReConvertItems(Dir):
    for FileName in os.listdir(Dir):
        FullPath = os.path.join(Dir, FileName)
        if os.path.isdir(FullPath):
            continue
        (Root, Extension) = os.path.splitext(FileName)
        TargetPath = os.path.join(Dir, "%s.png"%Root)
        if Extension.lower()!=".png":
            GrabImage(FullPath, TargetPath)

def BatchConvertItems():
    RootDirs = [#r"C:\research\Tendrils\SpriteMeister\Final Fantasy Tactics\Final Fantasy Tactics",
                #r"C:\research\Tendrils\SpriteMeister\Final Fantasy Tactics Advance\Final Fantasy Tactics Advance",
                #r"C:\research\Tendrils\SpriteMeister\Final Fantasy V\Final Fantasy V",
                #r"C:\research\Tendrils\SpriteMeister\Final Fantasy I\Final Fantasy I"
                r"C:\research\Tendrils\SpriteMeister\Final Fantasy IX\Final Fantasy IX"]
    for RootDir in RootDirs:
        for DirName in os.listdir(RootDir):
            Dir = os.path.join(RootDir, DirName)
            if os.path.isdir(Dir):
                GrabImages(Dir)
    ##GrabImages(r"C:\research\Tendrils\SpriteMeister\Final Fantasy Tactics\Final Fantasy Tactics\Guns")

def ConvertToPNG(FullPath):
    if not os.path.exists(FullPath):
        return
    if os.path.isdir(FullPath):
        return
    (Dir, FileName) = os.path.split(FullPath)
    (FileStem, Extension) = os.path.splitext(FullPath)
    if Extension.lower() == ".png":
        return
    Im = Image.open(FullPath)
    Im = Im.convert("RGBA")
    (Width, Height) = Im.size
    # Clean up off-white crapola:
    #print (Width, Height)
   
    for y in range(Height):
        for x in range(Width):
            p = Im.getpixel((x,y))
            #### print x, y, p #%%%
            #print x, y, p
            if p[:3] == (248, 252, 248):
                p = (255, 255, 255, 255)
                Im.putpixel((x,y),p)
                #print "*",
    TargetPath = os.path.join(Dir, "%s.png"%FileStem)
    print "Save:", TargetPath
    Im.save(TargetPath, "png")
    

def BatchConvertMonsters():
    RootDir = r"d:\tendrils\images\critter"
    for CritterDir in os.listdir(RootDir):
        CritterDirFullPath = os.path.join(RootDir, CritterDir)
        if not os.path.isdir(CritterDirFullPath):
            continue
        for FileName in os.listdir(CritterDirFullPath):
            FullPath = os.path.join(CritterDirFullPath, FileName)
            ConvertToPNG(FullPath)

def ConvertDir(Dir):
    for FileName in os.listdir(Dir):
        ConvertToPNG(os.path.join(Dir, FileName))

def ConvertColorSwap(FileName):
    Colors = ((255,0,238),(255,242,0),(0,255,0),(255,255,255))
    #SourceColors = {(231,95,11):0,(184,248,24):1,(255,163,71):2}
    SourceColors = {(72, 112, 208):0,(248,248,248):1}
    SourceImage = Image.open(FileName)
    (Width, Height) = SourceImage.size
    for Index in range(3):
        Im = SourceImage.convert("RGBA")
        for Y in range(Height):
            for X in range(Width):
                p = Im.getpixel((X,Y))[:3]
                if p == (0,0,0):
                    continue
                ColorIndex = SourceColors.get(p, 0)
                NewColor = Colors[(ColorIndex + Index) % len(Colors)]
                Im.putpixel((X,Y),NewColor)
        TargetPath = os.path.splitext(FileName)[0] + ".%d.png"%Index
        Im.save(TargetPath, "png")    
    
class Colors:
    White = (255,255,255)
    Green = (100,255,100)
    Blue = (100,100,255)
    Black = (0,0,0)
    
import pygame
class CelticPants:
    def __init__(self, Width, Height):
        
        pygame.init()

        self.Grid = {}
        self.Width = Width
        self.Height = Height
        for X in range(Width):
            for Y in range(Height):
                self.Grid[(X,Y)] = 0
        for X in range(Width):
            self.Grid[(X, 0)] = "h"
            self.Grid[(X, Height-1)] = "h"
        for Y in range(Height):
            self.Grid[(0, Y)] = "v"
            self.Grid[(Width-1, Y)] = "v"
            
    def BuildKnot(self):
        self.Surface = pygame.Surface((5*self.Width, 5*self.Height))
        for Y in range(self.Height):
            for X in range(self.Width):
                if (Y%2 and X%2) or (not Y%2 and not X%2):
                    # Corners:
                    E = self.Grid.get((X+1, Y))
                    W = self.Grid.get((X-1, Y))
                    N = self.Grid.get((X, Y-1))
                    S = self.Grid.get((X, Y+1))
                    if E=="v" and S=="h":
                        pygame.draw.line(self.Surface, Colors.White, (X*5 + 1, Y*5 + 4), (X*5 + 4, Y*5 + 1),)
                    if E=="v" and N=="h":
                        pygame.draw.line(self.Surface, Colors.White, (X*5 + 1, Y*5 - 4), (X*5 + 4, Y*5 - 1),)
                    if W=="v" and N=="h":
                        pygame.draw.line(self.Surface, Colors.White, (X*5 - 1, Y*5 - 4), (X*5 - 4, Y*5 - 1),)
                    if W=="v" and S=="h":
                        pygame.draw.line(self.Surface, Colors.White, (X*5 - 1, Y*5 + 4), (X*5 - 4, Y*5 + 1),)
                    continue
                ThisSquare = self.Grid[(X,Y)]
                if ThisSquare:
                    continue
                ####
                NE = self.Grid[(X+1, Y-1)]
                pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), (X*5 + 4, Y*5 - 4),)
                if NE == 0:
                    #pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), ((X+1)*5, (Y-1)*5,))
                    pass
                elif NE == "h":
                    #pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), (X*5 + 4, Y*5 - 4),)
                    pygame.draw.line(self.Surface, Colors.White, (X*5 + 4, Y*5 - 4),(X*5 + 5, Y*5 - 4))
                elif NE == "v":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 + 4, Y*5 - 4),(X*5 + 4, Y*5 - 5))
                #######
                SE = self.Grid[(X+1, Y+1)]
                pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), (X*5 + 4, Y*5 + 4),)
                if SE == 0:
                    pass
                elif SE == "h":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 + 4, Y*5 + 4),(X*5 + 5, Y*5 + 4))
                elif SE == "v":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 + 4, Y*5 + 4),(X*5 + 4, Y*5 + 5))
                ####
                NW = self.Grid[(X-1, Y-1)]
                pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), (X*5 - 4, Y*5 - 4),)
                if NW == 0:
                    pass
                elif NW == "h":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 - 4, Y*5 - 4),(X*5 - 5, Y*5 - 4))
                elif NW == "v":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 - 4, Y*5 - 4),(X*5 - 4, Y*5 - 5))
                #######
                SW = self.Grid[(X-1, Y+1)]
                pygame.draw.line(self.Surface, Colors.White, (X*5, Y*5), (X*5 - 4, Y*5 + 4),)
                if SW == 0:
                    pass
                elif SW == "h":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 - 4, Y*5 + 4),(X*5 - 5, Y*5 + 4))
                elif SW == "v":
                    pygame.draw.line(self.Surface, Colors.White, (X*5 - 4, Y*5 + 4),(X*5 - 4, Y*5 + 5))
        for Y in range(self.Height):
            for X in range(self.Width):
                if (Y%2 and X%2):
                    continue
                if (not Y%2 and not X%2):
                    continue
                ThisSquare = self.Grid[(X,Y)]
                if ThisSquare:
                    continue                
                if (Y%2):
                    pygame.draw.line(self.Surface, Colors.Black, (X*5 + 1, Y*5 - 1), (X*5 + 1, Y*5 - 1))
                    pygame.draw.line(self.Surface, Colors.Black, (X*5 - 1, Y*5 + 1), (X*5 - 1, Y*5 + 1))
                else:
                    pygame.draw.line(self.Surface, Colors.Black, (X*5 + 1, Y*5 + 1), (X*5 + 1, Y*5 + 1))
                    pygame.draw.line(self.Surface, Colors.Black, (X*5 - 1, Y*5 - 1), (X*5 - 1, Y*5 - 1))
                    
        pygame.image.save(self.Surface, "Knot.bmp")

def SaveSine(Max):
    Image = pygame.Surface((Max*2+1, 700))
    for Y in range(700):
        X = math.sin(Y * math.pi / 100)
        pygame.draw.line(Image, Colors.White, (X*Max + Max, Y), (X*Max + Max, Y))
    pygame.image.save(Image, "Sine.bmp")

def Chase():
    Size = 100
    Image = pygame.Surface((Size, Size))
    Pos = ((0,0), (Size, 0), (Size/2, Size))
    
    for Tick in range(12):
        NewPos = []
        for Index in range(len(Pos)):
            if Index:
                NextPos = Pos[Index-1]
            else:
                NextPos = Pos[-1]
            X1 = Pos[Index][0]
            X2 = NextPos[0]
            X = (X1 + (X2-X1)*0.15)
            Y1 = Pos[Index][1]
            Y2 = NextPos[1]
            Y = (Y1 + (Y2-Y1)*0.15)
            NewPos.append((X,Y))
            Color = (111-Tick*9, 111-Tick*9, 111-Tick*9)
            if Tick:
                pygame.draw.line(Image, Color, (X1, Y1), (X2, Y2))
        Pos = NewPos
    pygame.image.save(Image, "Chase.bmp")
if __name__ == "__main__":
    pygame.init()
    #SaveSine(70)
    #Chase()
    #sys.exit()
##    Glarble = CelticPants(13, 13)
##    for X in range(1):
##        for Y in range(1):
##            Glarble.Grid[(X*14 + 2,Y*14 + 3)] = "v"
##            Glarble.Grid[(X*14 + 2,Y*14 + 9)] = "v"
##            Glarble.Grid[(X*14 + 10,Y*14 + 3)] = "v"
##            Glarble.Grid[(X*14 + 10,Y*14 + 9)] = "v"
##            Glarble.Grid[(X*14 + 5,Y*14 + 4)] = "v"
##            Glarble.Grid[(X*14 + 7,Y*14 + 4)] = "v"
##            Glarble.Grid[(X*14 + 5,Y*14 + 8)] = "v"
##            Glarble.Grid[(X*14 + 7,Y*14 + 8)] = "v"
##            Glarble.Grid[(X*14 + 4,Y*14 + 5)] = "h"
##            Glarble.Grid[(X*14 + 8,Y*14 + 5)] = "h"
##            Glarble.Grid[(X*14 + 4,Y*14 + 7)] = "h"
##            Glarble.Grid[(X*14 + 8,Y*14 + 7)] = "h"
####            #
####            Glarble.Grid[(X*14 + 12,Y*14 + 3)] = "v"
####            Glarble.Grid[(X*14 + 12,Y*14 + 7)] = "v"
####            Glarble.Grid[(X*14 + 12,Y*14 + 11)] = "v"
####            Glarble.Grid[(X*14 + 3,Y*14 + 12)] = "h"
####            Glarble.Grid[(X*14 + 7,Y*14 + 12)] = "h"
####            Glarble.Grid[(X*14 + 11,Y*14 + 12)] = "h"
##    #Glarble.BuildKnot()
    
    #for Pooky in ("Up","Down","Left","Right","NW","NE", "SE","SW"):
    #    ConvertColorSwap("Defense%s.png"%Pooky)
    #BatchConvertMonsters()
    #ConvertDir(r"D:\Tendrils\images\misc")
    #ConvertDir(r"D:\Tendrils\images\background")
    #ConvertDir(r"D:\Tendrils\images\critter")
    #ConvertDir(r"D:\Tendrils\images\projectile")
    #ConvertDir(r"D:\Tendrils\images\Traps\LightsOut")
    #ConvertDir(r"D:\Tendrils\images\Traps\RedGreen")
    #ConvertDir(r"C:\research\Tendrils\images")
    #ConvertDir(r"C:\research\Tendrils\images\magic")
    #ConvertDir(r"C:\research\Tendrils\images\walls\1")
    #ConvertDir(r"D:\Tendrils\images\item")
    #ConvertDir(r"D:\Tendrils\images\npc")
    #ConvertDir(r"D:\Tendrils\images\background\level1")
    #ReConvertItems(r"d:\tendrils\images\item")
    ConvertDir(".")    
    #ConvertToPNG("f0s0.bmp")
##    GrabImage(r"d:\tendrils\images\item\Assassin's Dagger.gif",
##              r"d:\tendrils\images\item\Assassin's Dagger.png")
##    GrabImage(r"d:\tendrils\images\item\Bamboo Stick.gif",
##              r"d:\tendrils\images\item\Bamboo Stick.png")
    