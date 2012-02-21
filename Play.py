"""
Fast-loading file for starting up Tendrils.  (Gives quick "I'm loading" feedback)
"""
#from Utils import *
import pygame
import os
import sys

pygame.init()

Surface = pygame.display.set_mode((800,600))
#    return Font.render(str(Text),1,Color)
Name = os.path.join("fonts","saturno.ttf")
Font = pygame.font.Font(Name, 48)
Image = Font.render("Welcome to Tendrils!", 1, (255,255,255)) #TextImage("Welcome to Tendrils!", FontName = Fonts.Saturn, FontSize = 48)
Surface.blit(Image, (400 - Image.get_rect().width / 2, 200))
#Image = TextImage("Now loading...", FontName = Fonts.Saturn, FontSize = 48)
Image = Font.render("Now loading...", 1, (255,255,255))
Surface.blit(Image, (400 - Image.get_rect().width / 2, 300))
pygame.display.flip()

# MAGIC stuff:
import random
from Constants import *
import Resources
class Snowflake:
    pass
BlizzardSurface = pygame.Surface((300, 400))
Snowflakes = []
ImagesA = []
ImagesB = []
for Index in range(3):
    ImagePath = os.path.join("images","magic","work","Snow.0.%d.png"%(Index))
    Image = Resources.GetImage(ImagePath)
    Image.set_colorkey(Colors.Black)
    ImagesA.append(Image)
for Index in range(2):
    ImagePath = os.path.join("images","magic","work","Snow.1.%d.png"%(Index))
    Image = Resources.GetImage(ImagePath)
    Image.set_colorkey(Colors.Black)
    ImagesB.append(Image)
    
for Index in range(20):
    Flake = Snowflake()
    Flake.X = random.randrange(0, 300)
    Flake.Y = random.randrange(0, 400)
    Flake.XDir = random.randrange(-60, 0) / 2.0
    Flake.YDir = random.randrange(30, 90) / 2.0
    if random.random()>0.5:
        Flake.Images = ImagesA
        Flake.MaxImageNumber = 3
    else:
        Flake.Images = ImagesB
        Flake.MaxImageNumber = 2
    Flake.ImageDelay = random.randrange(0,3)
    Flake.ImageNumber = random.randrange(Flake.MaxImageNumber)
    Snowflakes.append(Flake)
    
for FrameIndex in range(50):
    BlizzardSurface.fill(Colors.Black)
    for Flake in Snowflakes:
        Flake.ImageDelay -= 1
        if Flake.ImageDelay<=0:
            Flake.ImageNumber = (Flake.ImageNumber + 1) % Flake.MaxImageNumber
            Flake.ImageDelay = 3
        Flake.X += Flake.XDir
        Flake.Y += Flake.YDir
        if Flake.Y > 400:
            Flake.Y = -20
        if Flake.X < -20:
            Flake.X = 320
        Image = Flake.Images[Flake.ImageNumber]
        BlizzardSurface.blit(Image, (Flake.X, Flake.Y))
        pygame.image.save(BlizzardSurface, "Bliz.%d.bmp"%FrameIndex)
sys.exit()
        

import Tendrils
if len(sys.argv)>1:
    Command = sys.argv[1].upper()
else:
    Command=Tendrils.CommandLines.Play
App = Tendrils.TendrilsApplication(Surface)
App.SetupTendrils(Command.lower())
import profile
profile.run("App.PlayTendrils()")
##App.PlayTendrils()
