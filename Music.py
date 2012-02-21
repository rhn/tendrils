from Utils import *
from Constants import *
import pygame
import string
import time
import Global
import cPickle

global QueuedSong

SongDirBGM = os.path.join("Music", "BGM")
SongDirBattle = os.path.join("Music","Battle")

# If songs consistenly run slow or fast on a system, StandardFudgeFactor can be used to tweak them.
StandardFudgeFactor = 0

# The mixer.get_pos() method is not affected by pause calls.  So, we add a "fudge factor".
FudgeFactorTicks = StandardFudgeFactor
PauseTime = 0

BonusTicksForDWI = 125
BonusTicksForSM = 125

class SongClass:
    """
    One of the songs used in the game.  We have id information (title, source game, composer, etc),
    file paths (to the song file and the simfile), and arrows.
    """
    def __init__(self, Name, Type = None, SongPath = None, SimFilePath = None, ImagePath = None):
        self.DWIHandlers = {"BPM":self.DWIHandleBPM,
                            "BPMS":self.SMHandleBPMs,
                            "GAP":self.DWIHandleGap,
                            "OFFSET":self.SMHandleOffset,
                            "TITLE":self.DWIHandleTitle,
                            "ARTIST":self.DWIHandleArtist,
                            "SINGLE":self.DWIHandleSingle,
                            "SOLO":self.DWIHandleSingle,
                            "DOUBLE":self.DWIHandleSingle,
                            "CHANGEBPM":self.DWIHandleChangeBPM,
                            "FREEZE":self.DWIHandleFreeze,
                            "NOTES":self.SMHandleNotes,
                            "BACKGROUND":self.DWIHandleBackground,
                            "END":self.DWIHandleEnd,
                            }
        if not Type:
            Type = SongType.BGM
        self.TempoChanges = [] # Entries: (When, NewSpeed)
        self.Freezes = [] # entrils: (when, msec)
        # Dictionary.  Keys are directions, and values are INDICES of arrow-tuples that are
        # freezes; when we next encounter an arrow pointing that way, we'll set the FREEZE-TIME for
        # these OLDER ROWS.
        self.FreezeArrows = {}
        # Author info:
        self.Name = Name
        self.Author = None
        self.SourceGame = None
        self.Dumper = None
        self.Remixer = None
        # Other info:
        self.Type = Type
        self.Gap = 0
        self.DWISkippingFlag = 0
        self.NextID = 0
        self.ArrowFeet = [] # Foot-count for our arrow-lists
        self.ArrowFileType = None
        self.SongPath = SongPath
        self.SimFilePath = SimFilePath
        self.ImagePath = ImagePath
        # Look up our simfilepath, if we don't know it:
        if self.SongPath and not self.SimFilePath:
            Root = os.path.splitext(self.SongPath)[0]
            for Extension in (".tdr", ".dwi"):
                SimPath = Root + Extension
                if os.path.exists(SimPath):
                    self.SimFilePath = SimPath
                    break
        # Look up our imagepath, if we don't know it:
        if self.SongPath and not self.ImagePath:
            Root = os.path.splitext(self.SongPath)[0]
            for Extension in (".png", ".gif", ".jpg", ".jpeg", ".bmp"):
                ImagePath = Root + Extension
                if os.path.exists(ImagePath):
                    self.ImagePath = ImagePath
                    break
        self.CurrentDanceArrows = None
        # key: difficulty level; value: list of arrow lists
        # Arrow lists have entries of the form (msec, ArrowList)
        # ArrowList has entries (ID, TicksAway, Direction, IsOffense)
        self.Arrows = []
    def __str__(self):
        return "<song '%s' (%s)>"%(self.Name, self.SongPath)
    def DWIHandleChangeBPM(self, Bits):
        Str = Bits[0]
        Changes = Str.split(",")
        for Change in Changes:
            Bits = Change.split("=")
            BBB = float(Bits[0]) / 16.0
            BPM = float(Bits[1])
            self.TempoChanges.append((BBB,BPM))
    def SMHandleBPMs(self, Bits):
        Str = Bits[0]
        Changes = Str.split(",")
        for Change in Changes:
            Bits = Change.split("=")
            BBB = float(Bits[0]) / 16.0
            BPM = float(Bits[1])
            if BBB == 0:
                self.BaseBPM = BPM
                self.SetBPM(self.BaseBPM)
            else:
                self.TempoChanges.append((BBB,BPM))
        
    def DWIHandleFreeze(self, Bits):
        Str = Bits[0]
        Changes = Str.split(",")
        for Change in Changes:
            Bits = Change.split("=")
            BBB = float(Bits[0]) / 16.0
            BPM = float(Bits[1])
            self.Freezes.append((BBB,BPM))
    def DWIHandleSingle(self, Bits):
        Level = len(self.Arrows)
        #if not self.Arrows.has_key(Level):
        self.Arrows.append([])
        self.CurrentArrows = self.Arrows[Level]
        self.ArrowFeet.append(int(Bits[1]))
        self.CurrentMsec = self.Gap
        self.SetBPM(self.BaseBPM)
        self.NextID = 0
        self.RowNumber = 0
        self.Beats = 0
        self.SMAccumulation = []
        self.FreezeArrows = {}
        self.SetBPM(self.BaseBPM)
        self.SkippingDWIFlag = 0
    def SMHandleNotes(self, Bits):
        ".sm loader: #NOTES comes at the start of a new set of arrows!"
        Level = len(self.Arrows)
        self.Arrows.append([])
        self.ArrowFeet.append(5) # We don't know yet, so put a default.
        self.CurrentArrows = self.Arrows[Level]
        self.CurrentMsec = self.Gap
        self.SetBPM(self.BaseBPM)
        self.NextID = 0
        self.RowNumber = 0
        self.Beats = 0
        self.SMAccumulation = []
        #self.CurrentMsec = self.SMOffset * self.MsecPerBeat
    def DWIHandleGap(self, Bits):
        self.Gap = float(Bits[0])
        self.Gap += BonusTicksForDWI
    def SMHandleOffset(self, Bits):
        self.Gap = - float(Bits[0]) * 1000
        self.Gap += BonusTicksForSM
    def DWIHandleBPM(self, Bits):
        self.BaseBPM = float(Bits[0])
        self.SetBPM(self.BaseBPM)
    def SetBPM(self, BPM):
        self.BPM = BPM
        self.MsecPerBeat = (60 * 1000) / float(self.BPM)
        self.MsecPerBeat *= 4
    def DWIHandleTitle(self, Bits):
        Str = string.join(Bits,":")
        self.Name = Str
    def DWIHandleArtist(self, Bits):
        Str = string.join(Bits,":")
        self.Artist = Str
    def LoadArrowsTDR(self):
        # Easy!  Just unpickle:
        File = open(self.SimFilePath, "rb")
        self.Arrows = cPickle.load(File)
        self.ArrowFeet = [1, 6, 9]
        File.close()
    def SaveArrowsTDR(self):
        File = open(self.SimFilePath, "wb")
        cPickle.dump(self.Arrows, File)
        File.close()
    def LoadArrows(self):
        if self.Type != SongType.Battle:
            return # only battle songs have simfiles.
        Extension = os.path.splitext(self.SimFilePath)[1].lower()
        if Extension == ".tdr":
            self.ArrowFileType = "tdr"
            self.LoadArrowsTDR()
        elif Extension == ".dwi":
            self.ArrowFileType = "dwi"
            self.LoadArrowsDWI()
        elif Extension == ".sm":
            self.ArrowFileType = "sm"
            self.LoadArrowsSM()
        else:
            print "** I don't dig you, freaky lactose man.  What kind of simfile is '%s'?"%self.SimFilePath
        ##self.DebugPrintArrows()
    def LoadArrowsSM(self):
        """
        .sm = StepMania file format.  This code is mostly copied from LoadArrowsDWI.
        """
        File = open(self.SimFilePath,"r")
        self.CurrentMsec = 0.0
        self.CurrentArrows = None
        self.SMAccumulation = []
        self.Beats = 0
        for RawFileLine in File.xreadlines():
            FileLine = RawFileLine.strip()
            if not FileLine:
                continue
            if FileLine[:2] == "//":
                continue
            if FileLine[0]=="#":
                # This comment line holds some handy data
                if FileLine[-1]==";":
                    FileLine = FileLine[:-1]
                Bits = FileLine.split(":")
                Command = Bits[0][1:]
                if self.DWIHandlers.get(Command):
                    apply(self.DWIHandlers[Command], (Bits[1:],))
                # Special case: SINGLE line may segue right into the notes!
                if Command not in ("SINGLE", "DOUBLE"):
                    continue
                FileLine = Bits[-1]
            if FileLine[0]==",":
                self.SMFinishMeasure()
                continue
            # Handle the "notes" from the start of an arrow-set:
            if FileLine.find(":")!=-1:
                Bits = FileLine.split(":")
                Int = None
                try:
                    Int = int(Bits[0])
                except:
                    pass
                if Int!=None:
                    self.ArrowFeet[-1] = Int
            if "0123456789".find(RawFileLine[0])==-1:
                continue # Not a measure
            self.SMAccumulation.append(FileLine)
    def SMFinishMeasure(self):
        if len(self.SMAccumulation) == 0:
            return
        self.Divisor = len(self.SMAccumulation)
        AddMsec = self.MsecPerBeat / self.Divisor
        IndexToDir = {0:3, 1:2, 2:1, 3:4, 4:5, 5:6} # PARA is still broken %%%
        for FileLine in self.SMAccumulation:
            OffenseFlag = random.choice((0, 1))
            for CharIndex in range(len(FileLine)):
                Char = FileLine[CharIndex]
                if Char == "0":
                    continue
                Dir = IndexToDir.get(CharIndex, None)
                if Dir==None:
                    continue # We don't know how to cope with this arrow!
                # Add an arrow!
                self.AddArrow(self.Arrows[-1], self.CurrentMsec, Dir, OffenseFlag)
                # If this is the start of a freeze, FLAG it as such!
                if Char == "2":
                    self.FreezeArrows[Dir] = (len(self.Arrows[-1]) - 1, self.CurrentMsec + AddMsec)
            self.DWIHandleTempoChanges()
            AddMsec = self.MsecPerBeat / self.Divisor
            self.CurrentMsec += AddMsec #self.MsecPerBeat
            self.Beats += 1 / self.Divisor
        self.SMAccumulation = []
    def DebugPrintArrows(self):
        if not self.Arrows:
            print "I don't have any arrows."
            return
        print "Here's my arrows:"
        for Tuple in self.Arrows[0]:
            print "%d: %2f -> Dir %s, Offense %s Freeze %2f"%(Tuple[0], Tuple[1], Tuple[2], Tuple[3], Tuple[4])
        print "---end of arrows"
    def DWIHandleBackground(self, Bits):
        self.DWISkippingFlag = 1
    def DWIHandleEnd(self, Bits):
        self.DWISkippingFlag = 0
    def LoadArrowsDWI(self):
        self.File = open(self.SimFilePath,"r")
        self.CurrentMsec = 0.0
        self.CurrentArrows = None
        #self.BPM = self.BaseBPM
        self.Beats = 0
        for FileLine in self.File.xreadlines():
            FileLine = FileLine.strip()
            if not FileLine:
                continue
            if FileLine[:2] == "//":
                continue
            if FileLine[0]=="#":
                # This comment line holds some handy data
                if FileLine[-1]==";":
                    FileLine = FileLine[:-1]
                Bits = FileLine.split(":")
                Command = Bits[0][1:]
                if self.DWIHandlers.get(Command):
                    apply(self.DWIHandlers[Command], (Bits[1:],))
                # Special case: SINGLE line may segue right into the notes!
                if Command not in ("SINGLE", "DOUBLE", "SOLO"):
                    continue
                FileLine = Bits[-1]
            if FileLine == ":":
                self.DWISkippingFlag = 1
            if self.DWISkippingFlag:
                continue
            # Default:
            #AddMsec = self.MsecPerBeat / 8.0
            ##print "Load notes for set %s from this line: '%s'"%(len(self.Arrows), FileLine)
            self.Divisor = 8.0
            CharIndex = 0
            AdvanceFlag = 1
            while CharIndex < len(FileLine):
                Char = FileLine[CharIndex]
                if Char == "<":
                    #Handle a lot of arrows in one row:
                    AdvanceFlag = 0
                elif Char == ">":
                    AdvanceFlag = 1
                elif Char == "(":
                    self.Divisor  = 16.0
                elif Char == "[":
                    self.Divisor = 24.0
                elif Char == "{":
                    self.Divisor = 64.0
                elif Char == "`":
                    self.Divisor = 192.0
                elif Char in (")","}","]","'"):
                    self.Divisor = 8.0
                elif Char == "!":
                    # Handle HELD arrow:
                    self.CurrentMsec -= AddMsec
                    CharIndex+=1 # hop to the arrow list
                    self.DWIHandleHeldArrows(FileLine[CharIndex], self.CurrentMsec)
                    CharIndex+=1 # ...and step onward.
                    self.CurrentMsec += AddMsec
                    continue
                elif Char == " ":
                    CharIndex += 1
                    continue #ignore whitespace
                else:
                    self.DWIAddArrows(self.CurrentArrows, self.CurrentMsec, Char)
                    if AdvanceFlag:
                        self.DWIHandleTempoChanges()
                        AddMsec = self.MsecPerBeat / self.Divisor
                        self.CurrentMsec += AddMsec #self.MsecPerBeat
                        self.Beats += 1 / self.Divisor
                CharIndex += 1
        # Final processing? %%%
    def DWIHandleHeldArrows(self, Char, Msec):
        # DWI freeze syntax is x!y, where x is the shown arrowset and y is the held arrowset.
        # (e.g. 4!4 for a held left-arrow, 7!4 to for tap up and hold left)
        # Any arrows with the current-msec become pending freezes.
        if Char in ("4","1","7","B","E","I"):
            self.Freeze(Msec, Directions.Left)
        if Char in ("3","6","9","B","H","L"):
            self.Freeze(Msec, Directions.Right)
        if Char in ("7","8","9","A","G","K"):
            self.Freeze(Msec, Directions.Up)
        if Char in ("1","2","3","A","F","J"):
            self.Freeze(Msec, Directions.Down)
        if Char in ("C", "E", "F", "G", "H", "M"):
            self.Freeze(Msec, Directions.NW)
        if Char in ("D", "I", "J", "K", "L", "M"):
            self.Freeze(Msec, Directions.NE)
    def Freeze(self, Msec, Direction):
        for Index in range(len(self.CurrentArrows)-1, -1, -1):
            Tuple = self.CurrentArrows[Index]
            if Tuple[1]!=Msec:
                break
            if self.CurrentArrows[Index][2]==Direction:
                self.FreezeArrows[Direction] = (Index, Msec)
                return
        # Not found?  Then ADD one.  1!2 is still a freeze.
        self.AddArrow(self.CurrentArrows, Msec, Direction, random.choice((0,1)))
        #self.CurrentArrows.append(Tuple)
        self.FreezeArrows[Direction] = (len(self.CurrentArrows)-1, Msec)
        #self.NextID += 1
    def DWIHandleTempoChanges(self):
        for (BBB, WaitMsec) in self.Freezes:
            if self.Beats >= BBB and (self.Beats - (1/self.Divisor)) < BBB:
                self.CurrentMsec += WaitMsec
        for (BBB, NewBPM) in self.TempoChanges:
            if self.Beats >= BBB and (self.Beats - (1/self.Divisor)) < BBB:
                LateFragment = self.Beats - BBB
                EarlyFragment = 1.0 - LateFragment
                # Do it!
                OldSpot = self.CurrentMsec
                self.CurrentMsec -= (self.MsecPerBeat * LateFragment)
                self.SetBPM(NewBPM)
                self.CurrentMsec += (self.MsecPerBeat * LateFragment)
    def AddArrow(self, ArrowList, Ticks, Dir, IsOffense, FreezeTime = 0):
        # Melt old freezes:
        FreezeTuple = self.FreezeArrows.get(Dir, None)
        if FreezeTuple!=None:
            (ArrowIndex, OldMsec) = FreezeTuple
            Bob = None
            try:
                Bob = list(self.CurrentArrows[ArrowIndex])
            except:
                print "ACK!  Can't thaw an arrow!"
                print self.CurrentArrows
                print ArrowIndex, OldMsec
                print len(self.Arrows), self.ArrowFeet
                del self.FreezeArrows[Dir]
            if Bob:
                Bob[4] = Ticks - OldMsec 
                if self.ArrowFileType == "sm":
                    Bob[4] += (self.MsecPerBeat / self.Divisor)
                #Bob[3] = 1 #%%% TEMP
                self.CurrentArrows[ArrowIndex] = tuple(Bob)
                del self.FreezeArrows[Dir]
                return
        # Ok, normal arrow it is:
        Tuple = (self.NextID, Ticks, Dir, IsOffense, FreezeTime)
        ArrowList.append(Tuple)
        self.NextID += 1
    def DWIAddArrows(self, ArrowList, Msec, Char):
        if Char == "0":
            self.RowNumber += 1
            return
        OffenseFlag = random.choice((0, 1))
        if Char in ("4","1","7","B","E","I"):
            self.AddArrow(ArrowList, Msec, Directions.Left, OffenseFlag)
        if Char in ("3","6","9","B","H","L"):
            self.AddArrow(ArrowList, Msec, Directions.Right, OffenseFlag)
        if Char in ("7","8","9","A","G","K"):
            self.AddArrow(ArrowList, Msec, Directions.Up, OffenseFlag)
        if Char in ("1","2","3","A","F","J"):
            self.AddArrow(ArrowList, Msec, Directions.Down, OffenseFlag)
        if Char in ("C", "E", "F", "G", "H", "M"):
            self.AddArrow(ArrowList, Msec, Directions.NW, OffenseFlag)
        if Char in ("D", "I", "J", "K", "L", "M"):
            self.AddArrow(ArrowList, Msec, Directions.NE, OffenseFlag)
        self.RowNumber += 1
    def SelectDanceArrows(self, Difficulty):
        """
        Choose the arrow-set whose difficulty is closest to our "optimal" number of feet.
        """
        if Difficulty == 0:
            DesiredFeet = 0
        elif Difficulty == 1:
            DesiredFeet = 4
        else:
            DesiredFeet = 10
        BestDist = None
        BestArrows = None
        for Index in range(len(self.Arrows)):
            Dist = abs(DesiredFeet - self.ArrowFeet[Index])
            if (BestDist==None or Dist<BestDist):
                self.CurrentDanceArrows = self.Arrows[Index]
                BestDist = Dist
    def GetArrows(self, Difficulty):
        if not self.CurrentDanceArrows:
            self.SelectDanceArrows(Difficulty)
        if not self.CurrentDanceArrows:
            return []
        Msec = pygame.mixer.music.get_pos() - FudgeFactorTicks*1000
        ReturnList = []
        for Tuple in self.CurrentDanceArrows:
            if Tuple[1]<(Msec-1000):
                continue
            if Tuple[1]>(Msec+8000):
                break
            Bob = list(Tuple)
            Bob[1] -= Msec
            ReturnList.append(Bob)
        return ReturnList

def Rewind(RewindMsec):
    global FudgeFactorTicks
    if not Global.CurrentSong:
        return
    Extension = os.path.splitext(Global.CurrentSong.SongPath)[1].lower()
    if Extension in (".it", ".xm", ".s3m", ".mod"):
        return
    #print "REWINDING..."
    OldFudge = FudgeFactorTicks
    CurrentPos = pygame.mixer.music.get_pos()
    NewMsec = max(0, CurrentPos - FudgeFactorTicks*1000 - RewindMsec)
    #print "Current pos was %.2f; new msec is %.2f"%(CurrentPos, NewMsec)
    FudgeFactorTicks = (CurrentPos - NewMsec)/1000.0
    #print "Fudge: %s->%s"%(OldFudge, FudgeFactorTicks)
    pygame.mixer.music.set_pos(NewMsec)
    #print "After rewind, pos is reported as:", pygame.mixer.music.get_pos()
    
def FadeOut():
    Global.CurrentSong = None
    pygame.mixer.music.set_endevent()
    pygame.mixer.music.fadeout(400)

def GetArrows(Difficulty):
    if not Global.CurrentSong:
        return []
    return Global.CurrentSong.GetArrows(Difficulty)
    #return None #%%% STUB!

def PauseSong():
    global PauseTime
    PauseTime = time.time()
    pygame.mixer.music.pause()

def UnpauseSong():
    global FudgeFactorTicks
    TicksSpentInPause = time.time() - PauseTime
    #FudgeFactorTicks += TicksSpentInPause #%%%
    pygame.mixer.music.unpause()

def StatSong():
    pass #%%% STUB!

def RestartSong():
    global FudgeFactorTicks
    FudgeFactorTicks = StandardFudgeFactor
    pygame.mixer.music.play()

def PlaySong(Song, Force = 0):
    global FudgeFactorTicks
    if not Song:
        return
    if Global.CurrentSong:
        if (not Force) and (Global.CurrentSong.Type == Song.Type):
            return # Already playing that song type!
        Global.CurrentSong.Arrows = [] # Drop it!
        if Global.CurrentSong.Type == SongType.Sting:
            #pygame.mixer.music.set_endevent()
            #pygame.mixer.music.queue(Song.SongPath)
            Global.QueueSong = Song
            return
    FudgeFactorTicks = 0
    Global.CurrentSong = Song
    Global.CurrentSong.LoadArrows()
    pygame.mixer.music.load(Song.SongPath)
    pygame.mixer.music.play()
    pygame.mixer.music.rewind() #%%% try immediate rewind
    pygame.mixer.music.set_endevent(SongOverEvent)
    return 1 # TRUE for SUCCESS

def PlaySongByName(Name):
    Song = Global.MusicLibrary.GetSong(Name)
    PlaySong(Song)

def PlaySongByPath(Path, Type, Tempo = None):
    if not os.path.exists(Path):
        print "** ERROR: Can't play song at '%s', file doesn't exist"%Path
        return
    Global.CurrentSong = SongClass("","", Path, "")
    PlaySong(Global.CurrentSong)

def TestDWI(SongName, SimName):
    #SongName = "Kung Fu Girl"
    Song = SongClass("Test", SongType.Battle, r"music\battle\%s"%SongName,
                     r"music\battle\%s"%SimName,)
    Song.LoadArrows()
    for Item in Song.Arrows[0]:
        print Item

MusicExtensions = (".it",".xm",".s3m",".mp3",".ogg",".mod")
SimFileExtensions = (".tdr", ".dwi", ".sm")
ImageExtensions = (".png", ".jpg", ".gif", ".bmp",)
class MusicLibrary:
    def __init__(self):
        # Keys: Level number, or None (for any level), or Boss (for boss battles)
        self.BattleSongs = {}
        # Keys: Names.  
        self.BGMSongs = {}
        # By level:
        self.MazeSongs = []
        self.BlockSongs = []
        # By filename:
        self.BGMSongInfo = {}
    def Load(self):
        "Load background songs from BGM.txt"
        try:
            File = open("BGM.txt","r")
        except:
            print "** WARNING: Unable to load background musics from BGM.txt!"
            return
        for FileLine in File.xreadlines():
            FileLine = FileLine.strip()
            if (not FileLine) or (FileLine[0]=="#"):
                continue
            # Bits: Name, Filename, Type, Title, Game, Author, Remixer, Dumper
            Bits = FileLine.split("\t")
            if len(Bits)<2:
                continue
            while len(Bits)<8:
                Bits.append("")
            Path = os.path.join("Music", "BGM", Bits[1])
            if Bits[2].lower() in ("battle","maze","blocks"):
                # Just save the info for later:
                self.BGMSongInfo[Bits[1]] = Bits
            else:
                # Create a song record now:
                NewSong = SongClass(Bits[0], Bits[2], Path)
                self.SetSongInfo(NewSong, Bits)
                self.BGMSongs[Bits[0]] = NewSong
    def SetSongInfo(self, NewSong, Bits):
        NewSong.Type = Bits[2]
        NewSong.Name = Bits[3]
        NewSong.SourceGame = Bits[4]
        NewSong.Author = Bits[5]
        NewSong.Remixer = Bits[6]
        NewSong.Dumper = Bits[7]
    def Scan(self, Dir = None, Key = None):
        "Scan for battle songs."
        TopLevel = 0
        if not Dir:
            Dir = os.path.join("Music", "Battle")
            TopLevel = 1
        if not os.path.exists(Dir):
            return
        #############################################
        # Special case: If there's only one music file in the directory, and there's a one markup file, assume that
        # they match.
        MusicCount = 0
        MarkupCount = 0
        FinishedFiles = 0
        ImagePath = None
        BiggestImageSize = 0
        for FileName in os.listdir(Dir):
            FullPath = os.path.join(Dir, FileName)
            if not os.path.isdir(FullPath):
                Extension = os.path.splitext(FullPath)[1].lower()
                if Extension in MusicExtensions:
                    MusicPath = FullPath
                    MusicCount += 1
                    if MusicCount>1:
                        break
                elif Extension in SimFileExtensions:
                    MarkupPath = FullPath
                    MarkupCount += 1
                elif Extension in ImageExtensions:
                    Size = os.stat(FullPath).st_size
                    if Size >= BiggestImageSize:
                        BiggestImageSize = Size
                        ImagePath = FullPath
        if MusicCount == 1 and MarkupCount: # Markupcount of 2 is ok, some songs have .dwi and .sm
            Name = os.path.split(MusicPath)[1]
            Name = os.path.splitext(Name)[0]
            Song = SongClass(Name, SongType.Battle, MusicPath, MarkupPath, ImagePath)
            if not self.BattleSongs.has_key(Key):
                self.BattleSongs[Key] = []
            self.BattleSongs[Key].append(Song)
            #print "Added song '%s' -> '%s'"%(Key, Song) #%%%
            ExtraInfo = self.BGMSongInfo.get(FileName, None)
            if ExtraInfo:
                self.SetSongInfo(Song, ExtraInfo)
            FinishedFiles = 1
        #############################################
        for FileName in os.listdir(Dir):
            FullPath = os.path.join(Dir, FileName)
            if os.path.isdir(FullPath):
                # Sub-directory scan:
                SubKey = None
                if TopLevel:
                    if FileName == "Boss":
                        SubKey = "Boss"
                    else:
                        try:
                            SubKey = int(FileName)
                        except:
                            pass
                self.Scan(FullPath, SubKey)
            else:
                if FinishedFiles:
                    continue
                (RawPath, Extension) = os.path.splitext(FullPath)
                Extension = Extension.lower()
                # Look for known file extensions that also have a corresponding simfile.
                if Extension in MusicExtensions:
                    for SimFileExtension in SimFileExtensions:
                        SimPath = RawPath + SimFileExtension
                        if os.path.exists(SimPath):
                            if not self.BattleSongs.has_key(Key):
                                self.BattleSongs[Key] = []
                            Name = os.path.split(FullPath)[1]
                            Name = os.path.splitext(Name)[0]                                
                            Song = SongClass(FileName, SongType.Battle, FullPath, SimPath)
                            ExtraInfo = self.BGMSongInfo.get(FileName, None)
                            if ExtraInfo:
                                self.SetSongInfo(Song, ExtraInfo)                            
                            self.BattleSongs[Key].append(Song)
                            #print "Added song '%s' -> '%s'"%(Key, Song) #%%%
                            break
    def ScanMazeSongs(self):
        for Level in range(1, 11):
            self.MazeSongs.append([])
            Dir = os.path.join(Paths.MusicBGM, "%s"%Level)
            if not os.path.exists(Dir):
                print "** Warning: Can't find maze music folder '%s'"%Dir
                continue
            for FileName in os.listdir(Dir):
                FullPath = os.path.join(Dir, FileName)
                Extension = os.path.splitext(FullPath)[1]
                if Extension.lower() in MusicExtensions:
                    Song = SongClass(FullPath,None,FullPath)
                    # Look it up:
                    ExtraInfo = self.BGMSongInfo.get(FileName, None)
                    if ExtraInfo:
                        self.SetSongInfo(Song, ExtraInfo)
                    self.MazeSongs[-1].append(Song)
    def ScanBlockSongs(self):
        Dir = os.path.join(Paths.MusicBGM, "Blocks")
        if not os.path.exists(Dir):
            print "** Warning: Can't find block music folder '%s'"%Dir
            return
        for FileName in os.listdir(Dir):
            FullPath = os.path.join(Dir, FileName)
            Extension = os.path.splitext(FullPath)[1]
            if Extension in MusicExtensions:
                Song = SongClass(FullPath,SongType.Blocks,FullPath)
                # Look it up:
                ExtraInfo = self.BGMSongInfo.get(FileName, None)
                if ExtraInfo:
                    self.SetSongInfo(Song, ExtraInfo)
                self.BlockSongs.append(Song)
    def GetSong(self, Name):
        Name = Name.lower().strip()
        Song = self.BGMSongs.get(Name, None)
        if Song:
            return Song
        # Also check level0 battle songs:
        for Song in self.BGMSongs.get(0, []):
            if Song.Name == Name:
                return Song
    def GetBattleSong(self, Name = None):
        if not Name:
            List = self.GetPossibleBattleSongs(Global.Maze.Level)
            return random.choice(List)
        for Key in self.BattleSongs.keys():
            for Song in self.BattleSongs[Key]:
                if os.path.split(Song.SongPath)[1] == Name:
                    return Song
        return None
    def GetPossibleBattleSongs(self, Level):
        List = self.BattleSongs.get(None,[])[:]
        if Level>1:
            NewList = self.BattleSongs.get(Level-1,[])
            List.extend(NewList)
        NewList = self.BattleSongs.get(Level,[])
        List.extend(NewList)
        NewList = self.BattleSongs.get(Level+1,[])
        List.extend(NewList)
        return List
        #return random.choice(List)
    def DebugPrintBattleSongs(self):
        print "DEBUG: Here's a list of battle songs."
        for Key in self.BattleSongs.keys():
            print Key
            for Song in self.BattleSongs[Key]:
                print Song.Name, Song.SourceGame, Song.Remixer, Song.SongPath
    def GetBlockSong(self):
        return random.choice(self.BlockSongs)
    def GetBattleSongList(self):
        "Return list of ALL battle songs.  For free-play."
        List = []
        for SubList in self.BattleSongs.values():
            List.extend(SubList)
        return List

if not Global.MusicLibrary:
    Global.MusicLibrary = MusicLibrary()
    Global.MusicLibrary.Load()
    Global.MusicLibrary.Scan()
    Global.MusicLibrary.ScanMazeSongs()
    #Global.MusicLibrary.DebugPrintBattleSongs()
    Global.MusicLibrary.ScanBlockSongs()

if PSYCO_ON:
    psyco.bind(SongClass.GetArrows)

if __name__ == "__main__":
    # If run from the command line: Fix a song!  Args:
    #    Music.py TDRFileName GapChange TimeMultiplier DeleteArrowCount
    # For isntance, to delay the starting point, but speed up arrow tempo a little:
    #    Music.py froo.tdr 20 1.0001
    FilePath = sys.argv[1]
    try:
        DelArrowCount = int(sys.argv[4])
    except:
        DelArrowCount = 0
    os.system("copy \"%s\" \"%s.bak\""%(FilePath, FilePath))
    Song = SongClass("Test", SongType.Battle, FilePath,
                     FilePath,)
    Song.LoadArrows()
    GapChange = float(sys.argv[2])
    if len(sys.argv)>3:
        Multiplier = float(sys.argv[3])
    else:
        Multiplier = 1.0
    for ArrowSet in Song.Arrows:
        for Index in range(len(ArrowSet)):
            List = list(ArrowSet[Index])
            List[1] += GapChange
            List[1] *= Multiplier
            Tuple = tuple(List)
            ArrowSet[Index] = Tuple            
    if DelArrowCount:
        Song.Arrows[2] = Song.Arrows[1][:-DelArrowCount]
    Song.SaveArrowsTDR()
    

    