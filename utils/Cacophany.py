import threading
import winsound
import time
import os
import sys
import random

Dir = "c:\\tendrils\\sounds"
RarePaths = []
SoundPaths = []
SoundPaths.append(os.path.join(Dir, "DigDugDragon.wav"))
SoundPaths.append(os.path.join(Dir, "dp_superpac_wakka.wav"))
SoundPaths.append(os.path.join(Dir, "RatingC.wav"))
SoundPaths.append(os.path.join(Dir, "RatingD.wav"))
SoundPaths.append(os.path.join(Dir, "RatingAAA.wav"))
SoundPaths.append(os.path.join(Dir, "Fireball.wav"))
SoundPaths.append(os.path.join(Dir, "GolgoM16.wav"))
SoundPaths.append(os.path.join(Dir, "DoorOpen.wav"))
SoundPaths.append(os.path.join(Dir, "Cure.wav"))
SoundPaths.append(os.path.join(Dir, "2600Dragon.wav"))
SoundPaths.append(os.path.join(Dir, "Boop5.wav"))
SoundPaths.append(os.path.join(Dir, "Boop4.wav"))
SoundPaths.append(os.path.join(Dir, "Boop3.wav"))
SoundPaths.append(os.path.join(Dir, "RatingA.wav"))
SoundPaths.append(os.path.join(Dir, "RatingB.wav"))
#SoundPaths.append(os.path.join(Dir, "XXXXXXXXXXXXXXXXX"))
SoundPaths.append(os.path.join(Dir, "Happy.wav"))
SoundPaths.append(os.path.join(Dir, "Sad.wav"))
SoundPaths.append(os.path.join(Dir, "Heartbeat.wav"))
SoundPaths.append(os.path.join(Dir, "Kill.wav"))
SoundPaths.append(os.path.join(Dir, "Hit.wav"))
SoundPaths.append(os.path.join(Dir, "Hit2.wav"))
SoundPaths.append(os.path.join(Dir, "Hit3.wav"))
SoundPaths.append(os.path.join(Dir, "Hit4.wav"))
SoundPaths.append(os.path.join(Dir, "jou_pter.wav"))
SoundPaths.append(os.path.join(Dir, "MegamanNoise.wav"))
SoundPaths.append(os.path.join(Dir, "PowerUp.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep1.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep2.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep3.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep4.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep5.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep6.wav"))
SoundPaths.append(os.path.join(Dir, "Bleep7.wav"))

Dir = r"C:\Documents and Settings\swt\Desktop\Disgaea-SndPak\Disgaea-SndPak"
#SoundPaths.append(os.path.join(Dir, "Disgaea Exit Windows.wav"))

SoundPaths.append(os.path.join(Dir, "Disgaea Asterisk.wav"))
SoundPaths.append(os.path.join(Dir, "Disgaea Critical Stop.wav"))
SoundPaths.append(os.path.join(Dir, "Disgaea Menu Command.wav"))
SoundPaths.append(os.path.join(Dir, "Disgaea Menu Popup.wav"))
SoundPaths.append(os.path.join(Dir, "Disgaea Exit Windows (Alternate).wav"))
RarePaths.append(os.path.join(Dir, "Disgaea Exit Windows (Alternate).wav"))
ThreadCount = 0

def PlayThread():
    SoundList = []
    Index = 0
    while (1):
        if len(SoundList)<2 or (len(SoundList)<5 and random.random()<0.04):
            SoundList.append(random.choice(SoundPaths))
        elif len(SoundList)>1 and random.random()<0.02:
            del SoundList[0]
        print SoundList, Index
        Index = (Index+1) % len(SoundList)
        #winsound.PlaySound(SoundList[Index], winsound.SND_FILENAME)
        print pygame.mixer.get_busy()
        while pygame.mixer.get_busy()>=ThreadCount:
            time.sleep(0.1)
        Resources.PlaySound(SoundList[Index])
        if SoundList[Index] in RarePaths:
            del SoundList[Index]
        time.sleep(0.5)

import pygame
import Resources
import Critter
import Party
import Global
import ItemPanel
Global.Party = Party.GetTestParty()
pygame.init()
Surface = pygame.display.set_mode((800,600))

Bob = threading.Thread(None, PlayThread)
Bob.start()
ThreadCount += 1
time.sleep(30)
######
Bob2 = threading.Thread(None, PlayThread)
Bob2.start()
ThreadCount += 1
time.sleep(30)
####
ThreadCount += 1
PlayThread()        