import cPickle
import os

def GetPositions(Name):
    File = open(os.path.join("Summon", "%s.dat"%Name),"r")
    Positions = cPickle.load(File)
    File.close()
    return Positions
ZergPositions = GetPositions("ZergRush") # reused by phoenix
AngelPositions = GetPositions("Angel") # also used by Metroid
# Chocobo is random bouncing (with almost-realistic rubber-ball physics); no path is saved
BowserPositions = GetPositions("Bowser") # reused by bahamut
SandmanPositions = GetPositions("Sandman")
# Note: Yoshi has randomized positions (he blinks around; he's the teleporter after all!); no path is saved
IfritPositions = GetPositions("Ifrit")
ArgonPositions = GetPositions("Argon")
ShivaPositions = GetPositions("Shiva")
