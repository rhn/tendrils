from Utils import *
from Constants import *
import os
import time
import traceback
import random
import Music
import Global

BattleImagesByLevel = [0, 3, 3, 3, 3, 3,
                          3, 3, 3, 3, 3]
def GetBattleBackground(Level = None):
    if not Level:
        Level = Global.Maze.Level
    if Level >= len(BattleImagesByLevel):
        Level = random.randrange(1, len(BattleImagesByLevel))
    Name = random.randrange(1, BattleImagesByLevel[Level] + 1)
    return GetImage(os.path.join("Images", "Background", "Level%d"%Level, "%d"%Name))

# Some images are pre-loaded, for very fast access, and never dropped from the
# cache.  For instance: The Blizzard images from the magic spell of the same name.
# Loading the blizzard images is fast, but NOT FAST ENOUGH - ever millisecond counts
# when you're dancing!
PermanentImageCache = {}
IMAGE_CACHE = {}
IMAGE_USE_TIME = {}
SOUND_CACHE = {}
SOUND_USE_TIME = {}

MAX_IMAGE_CACHE_SIZE = 100

VICTORY_SOUND_COUNT = 3
DEFEAT_SOUND_COUNT = 2
class SongType:
    Battle = "Battle"
    Sting = "Sting"
    Maze = "Maze"
    BGM = "Misc"

def PreloadImageCache():
    # Preload SOME images into the permanent cache.
    global PermanentImageCache
    if len(PermanentImageCache.keys()):
        return # already preloaded!
    # Blizzard:
    for Index in range(20):
        SubPath = os.path.join(Paths.ImagesMagic, "Blizzard.%s.png"%Index)
        Image = pygame.image.load(SubPath).convert()
        Image.set_colorkey(Colors.Black)
        PermanentImageCache[SubPath] = Image
    # Blizzard2:
    for Index in range(20):
        SubPath = os.path.join(Paths.ImagesMagic, "Blizzard2.%s.png"%Index)
        Image = pygame.image.load(SubPath).convert()
        Image.set_colorkey(Colors.Black)
        PermanentImageCache[SubPath] = Image
    # Bloodlust:
    for Index in range(3):
        SubPath = os.path.join(Paths.ImagesMagic, "Bloodlust.%s.png"%Index)
        Image = pygame.image.load(SubPath).convert()
        Image.set_colorkey(Colors.Black)
        PermanentImageCache[SubPath] = Image
    # Kaboom:
    for Index in range(4):
        SubPath = os.path.join(Paths.ImagesMagic, "Kaboom.%s.png"%Index)
        Image = pygame.image.load(SubPath).convert()
        Image.set_colorkey(Colors.Black)
        PermanentImageCache[SubPath] = Image

class Song:
    def __init__(self, FileName, Type = SongType.Battle, Title = "", Source = "", Author = "",
                 Remixer = "", Dumper = ""):
        self.FileName = FileName
        self.Type = Type        
        self.Title = Title
        self.Author = Author
        self.SourceGame = Source
        self.Remixer = Remixer
        self.Dumper = Dumper
    def GetPath(self):
        if self.Type == SongType.Battle:
            SongPath = os.path.abspath(os.path.join(Paths.MusicBattle, self.FileName))        
        else:
            SongPath = os.path.abspath(os.path.join(Paths.MusicBGM, self.FileName))
        return SongPath
PuzzleSongs = ["dune","agony"]

def GetPuzzleSongName():
    return random.choice(PuzzleSongs)

def GetMazeSongName(Level):
    List = MazeSongsByLevel[Level-1 % len(MazeSongsByLevel)]
    return random.choice(List)

def GetPossibleBattleSongs(Level):
    return Global.MusicLibrary.GetPossibleBattleSongs(Level)
    List = []
    Level -= 1
    List = BattleSongsByLevel[Level][:]
    if Level>1:
        List.extend(BattleSongsByLevel[Level-1])
    if Level<len(BattleSongsByLevel)-1:
        List.extend(BattleSongsByLevel[Level+1])
    return List

def GetBattleSong(Level):
    """
    Randomly pick a battle-song, for this maze level.  Look at lists corresponding to
    this level and its neighbors.
    """
    List = Global.MusicLibrary.BattleSongs.get(None, [])
    for TheLevel in range(Level-1, Level+2):
        OtherList = Global.MusicLibrary.BattleSongs.get(TheLevel, [])
        List.extend(OtherList)
    return random.choice(List)


            
def PlaySong(Path, Type, SongTempo = 1.0):
    return Music.PlaySong(Path, Type, SongTempo) #Song.GetPath(), Song.Type)
        

def PlayBattleSong(SongName):
    if not SongName:
        SongName = random.choice(["Dancing Justice.xm", "Arrow56.xm",])# "ArrowZelda.xm"])
    SongPath = os.path.abspath(os.path.join(Paths.MusicBattle, SongName))
    print "TSS will now play this song: '%s'"%SongPath
    #TSS.PlaySong(r"D:\Tendrils\Music\Battle\ArrowZelda.xm")
    Music.PlaySong(SongPath, "Battle")

def GetMonsterImage(Monster):
    return GetImage(os.path.join(Paths.ImagesMonster, "Monster.png")) #%%%

def GetItemImage(Item):
    try:
        Image = GetImage(os.path.join(Paths.ImagesItem, "%s.png"%Item.Name)) #%%%
    except:
        Image = GetImage(os.path.join(Paths.ImagesItem, "Axe.png")) #%%% Crummy default
    return Image
    

def GetDefaultCritterImage():
    return GetImage(os.path.join(Paths.ImagesCritter, "Default.png"))

def CleanImageCache():
    global IMAGE_CACHE
    global IMAGE_USE_TIME
    TimeList = []
    for Item in IMAGE_USE_TIME.items():
        TimeList.append((Item[1],Item[0]))
    if len(TimeList)<=MAX_IMAGE_CACHE_SIZE:
        return
    TimeList.sort()    
    for Index in range(len(TimeList) - MAX_IMAGE_CACHE_SIZE):
        SubPath = TimeList[Index]
        try:
            del IMAGE_CACHE[SubPath]
        except:
            pass
        try:
            del IMAGE_USE_TIME[SubPath]
        except:
            pass

def GetImage(SubPath, Perilous = 0):
    global IMAGE_CACHE
    global IMAGE_USE_TIME
    CachedImage = PermanentImageCache.get(SubPath, None)
    if CachedImage:
        return CachedImage
    CachedImage = IMAGE_CACHE.get(SubPath,None)
    if CachedImage:
        IMAGE_USE_TIME[SubPath]=time.time()
        return CachedImage
    FullPath=SubPath
    # If they didn't pass an extension, try the usual suspects:
    Extension = os.path.splitext(FullPath)[1]
    # If the extension is a number, it's not REALLY an extension:
    try:
        Int = int(Extension[1:])
        Extension = ""
    except:
        pass
    if not Extension and os.path.exists(FullPath+".png"):
        Extension = ".png"
        FullPath += Extension
    # Note: the code below won't be used, but leave it in for dev:
    if not Extension and os.path.exists(FullPath+".bmp"): # keep this one
        Extension = ".bmp"
        FullPath += Extension
    if not Extension and os.path.exists(FullPath+".gif"): # keep this one
        Extension = ".gif"
        FullPath += Extension
    try:
        Image = pygame.image.load(FullPath).convert()
    except pygame.error, Message:
        # #%%%
        # Fail as gracefully as possible:
        if Perilous:
            raise ValueError, Message
        else:
            print '**Warning: Cannot load image:', FullPath
            traceback.print_exc()
            return Global.NullImage
    Image = Image.convert()
    IMAGE_CACHE[SubPath] = Image
    IMAGE_USE_TIME[SubPath] = time.time()
    return Image

class DummySound:
    def play(self):
        pass

def CleanSoundCache():
    pass
   

def PlayStandardSound(Name):
    return PlaySound(os.path.join("Sounds",Name))
              
def PlaySound(SubPath):
    return GetSound(SubPath).play()

def GetSound(SubPath):
    global SOUND_CACHE
    global SOUND_USE_TIME
    MasterVolume = Global.Party.Options.get("SFXVolume", 50) / 100.0  #GetMasterVolume()
    if MasterVolume==0 or not pygame.mixer:
        return DummySound()
    CachedSound = SOUND_CACHE.get(SubPath,None)
    if CachedSound:
        SOUND_USE_TIME[SubPath] = time.time()
        CachedSound.set_volume(MasterVolume)
        return CachedSound
    FullPath = SubPath ##os.path.join("sounds", SubPath)
    try:
        Sound = pygame.mixer.Sound(FullPath)
        Volume = MasterVolume
        Sound.set_volume(Volume)
    except pygame.error, Message:
        print 'Cannot load sound:', SubPath
        traceback.print_exc()
        return DummySound()
    SOUND_CACHE[SubPath] = Sound
    SOUND_USE_TIME[SubPath] = time.time()
    return Sound

# dictionary mapping screens/levels to the tiles they use.  (The "level tiles"
# are used for maze and combat left-hand panel
Tiles = {1:12, 2:6, 3:4, 4:7, 5:15, 6:11, 7:3, 8:16, 9:10, 10:13,
         "Equip":9, "Shop":8, "Misc":17, "Equip2":5, "FreePlay":17}
    


SONG_TYPE_BATTLE="Battle"
SONG_TYPE_TOWN="Town"
SONG_TYPE_SHOP="Shop"

SONG_COUNTS={SONG_TYPE_BATTLE:2,SONG_TYPE_TOWN:1,SONG_TYPE_SHOP:1}

if PSYCO_ON:
    psyco.bind(GetImage)
 