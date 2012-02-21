"""
This utility takes .IT file output from OpenSPC and processes it into a more managable form.

OpenSPC performs as many as 100 updates per second, and produces a row for each update.  Most
songs have a heartbeat period much longer than 10 msec (e.g. AxelayL1, a fast song, takes
about 85 msec per beat).  Since the heartbeat-period is not an integer multiple of the
update period, the number of rows per beat varies - e.g. AxelayL1 gets either 8 or 9 rows between
beats.

There are two problems: First, the rhythm of the song is off (though not blatantly so).  And second,
creating arrows for such a song is very onerous.  What we want to do is compress the output down
to one row per beat, preserving the sound and improving the rhythm.

This utility reads a text file of the .it score, and outputs a massaged version.
"""
import sys
import os
import traceback
SuperPortamentoFudge = 24.62
# 0123456789A
#|F-532v04...|........EED|...........|...........|...........|.....v00...|...........|...........|F-532v04...|........EED|...........|...........|...........|.....v00...|...........|...........|.....v02   
class CellClass:
    def __init__(self, Str):
        self.Volume = None #default
        self.Note = Str[:3]
        if self.Note == "...":
            self.Note = None
        self.Instrument = Str[3:5]        
        self.VolumeEffect = Str[5:8]
        if self.VolumeEffect == "...":
            self.VolumeEffect = None
        else:
##            print "Str:",Str, len(Str)
##            print self.VolumeEffect
            self.Volume = int(self.VolumeEffect[1:])
        self.Effect = Str[8:11]
    def __str__(self):
        if self.Note:
            Str = self.Note
        else:
            Str = "..."
        if self.Instrument:
            Str += self.Instrument
        else:
            Str += ".."
        if self.VolumeEffect:
            Str += self.VolumeEffect
        else:
            Str += "..."
        if self.Effect:
            Str += self.Effect
        else:
            Str += "..."
        return Str
    def GetPort(self):
        if not self.Effect:
            return 0
        if self.Effect[0:2]=="FF":
            return 4 * int(self.Effect[2], 16)
        elif self.Effect[0:2]=="FE":
            return int(self.Effect[2], 16)
        elif self.Effect[0]=="F":
            return int(SuperPortamentoFudge * int(self.Effect[1:3], 16))
        if self.Effect[0:2]=="EF":
            return -4 * int(self.Effect[2], 16)
        elif self.Effect[0:2]=="EE":
            return -int(self.Effect[2], 16)
        elif self.Effect[0]=="E":
            return int(-SuperPortamentoFudge * int(self.Effect[1:3], 16))
        return 0
    def GetVolume(self):
        if self.Volume!=None:
            return self.Volume
        if self.Note:
            return 64
        return None
class Munger:
    def __init__(self, RowsPerBeat):
        self.RowsPerBeat = RowsPerBeat
    def GetRow(self,Str):
        Cells = []
        Bits = Str.split("|")
        for Bit in Bits[1:17]:
            Cells.append(CellClass(Bit))
        return Cells
    def RowToString(self, Row):
        Str = ""
        for Cell in Row:
            Str += "|%s"%Cell
        return Str
    def RowHasNotes(self, Row):
        for Cell in Row:
            if Cell.Note:
                return 1
        return 0
    def MungeFile(self, FilePath):
        File = open(FilePath)
        FileLines = File.readlines()
        File.close()
        (Dir, FileName) = os.path.split(FilePath)
        BaseName = os.path.splitext(FileName)[0]+".out.txt"
        OutputFileName = os.path.join(Dir, BaseName)
        OutputFile = open(OutputFileName, "w")
        # Strip bogus lines:
        for Line in FileLines[:]:
            if Line.find("ModPlug")!=-1:
                FileLines.remove(Line)
        RowNumber = 0
        BeatRow = 0
        CellVolumes = []
        ##print "Top row:", FileLines[RowNumber]
        OldRow = self.GetRow(FileLines[RowNumber])
        for Cell in OldRow:
            Volume = Cell.GetVolume()
            if Volume!=None:
                CellVolumes.append(Volume)
            else:
                CellVolumes.append(64)
        ##OlderCellVolumes = CellVolumes[:]
        OldCellVolumes = CellVolumes[:]
        PatternRowNumber = 0
        OutputFile.write("ModPlug Tracker  IT\n")
        VerboseFlag = 0 #%%%
        while (1):
            CacheRows = []
            BeatRow += self.RowsPerBeat ##8.541666666666666
            RowsToRead = int(round(BeatRow))
            BeatRow -= RowsToRead
            ReadRange = range(RowNumber + 1, RowNumber + 1 + RowsToRead)
            # Read the correct number of rows, stopping early if you see a note on the 2nd-to-last row:
            for ReadRowNumber in ReadRange:
                ##print "Read row %d into cache."%ReadRowNumber
                if ReadRowNumber >= len(FileLines):
                    # discard the trailing stuff and finish!
                    return
                CacheRows.append(self.GetRow(FileLines[ReadRowNumber]))
                RowNumber += 1
                if ReadRowNumber in ReadRange[-3:] and self.RowHasNotes(CacheRows[-1]):
                    break
            if VerboseFlag:
                print "Read up to row:", RowNumber
                print "Here's our old row:"
                print self.RowToString(OldRow)
                print "--Row cache:----"
                for Row in CacheRows:
                    print self.RowToString(Row)
                print "---------------------"
            # Put notesin either the last row or the current row:
            MidPoint = len(CacheRows) / 2
            for CacheRowIndex in range(len(CacheRows) - 1):
                CacheRow = CacheRows[CacheRowIndex]
                for CellIndex in range(16):
                    if CacheRow[CellIndex].Note:
                        if CacheRowIndex<MidPoint:
                            OldRow[CellIndex] = CacheRow[CellIndex] # squish?
                        else:
                            CacheRows[-1][CellIndex] = CacheRow[CellIndex]
            # Process EFFECTS properly: PORTAMENTO and VOLUME.
            
            ################################################
            # VOLUME:
            CellVolumeTotals = [0]*16
            VolList = [OldRow,]
            VolList.extend(CacheRows[:-1])
            CellVolumes = OldCellVolumes[:]
            for VolRow in VolList:
                for CellIndex in range(16):
                    Cell = VolRow[CellIndex]
                    Volume = Cell.GetVolume()
                    if Volume!=None:
                        CellVolumes[CellIndex] = Cell.Volume
                    CellVolumeTotals[CellIndex] += CellVolumes[CellIndex]
                    #CellVolumes[CellIndex] = Cell.Volume
            Victim = CacheRows[-1]
            for CellIndex in range(16):
                AvgVolume = int(CellVolumeTotals[CellIndex] / (len(CacheRows)))
                VictimCellVolume = Victim[CellIndex].GetVolume()
                if VictimCellVolume != None:
                    CellVolumes[CellIndex] = VictimCellVolume
##                elif AvgVolume != OldCellVolumes[CellIndex]:
##                    CellVolumes[CellIndex] = AvgVolume
##                    Victim[CellIndex].VolumeEffect = "v%02d"%AvgVolume                    
                elif CellVolumes[CellIndex] != OldCellVolumes[CellIndex]:
                    # Capture SLOW volume moves!
                    Victim[CellIndex].VolumeEffect = "v%02d"%CellVolumes[CellIndex]
                    
            OldCellVolumes = CellVolumes[:]
            #################################################
            # PORTAMENTO:
            CellPort = [0]*16
            for CellIndex in range(16):
                if CacheRows[-1][CellIndex].Note:
                    PortRows = CacheRows[:-3]
                else:
                    PortRows = CacheRows[:-1]
                for CacheRow in PortRows: #Fudge factor!  Skip the last 2!
                    Cell = CacheRow[CellIndex]
                    CellPort[CellIndex] += Cell.GetPort()
##            if OldRow[1].Note == "D-7":
##                print "***********\n\n\n\n"
##                print "RowCache:"
##                for Row in CacheRows:
##                    print self.RowToString(Row)
##                print "PortRows:"
##                for Row in PortRows:
##                    print self.RowToString(Row)
##                print "CellPort:"
##                print CellPort
##                for Row in PortRows:
##                    print Row[1].GetPort()
            Victim = OldRow
            for CellIndex in range(16):
                Port = CellPort[CellIndex] + Victim[CellIndex].GetPort()
                if Port:
                    if Port>0:
                        EffectStr = "F"
                    else:
                        EffectStr = "E"
                    ##AbsPort = min(abs(Port), 255)
                    AbsPort = abs(Port)
                    if AbsPort < 16:
                        EffectStr += "E%X"%AbsPort
                    elif AbsPort <= 15*4:
                        EffectStr += "F%01X"%(AbsPort/4)
                    else:
                        EffectStr += "%02X"%int(round(AbsPort/SuperPortamentoFudge)) # ASSUMED: Final speed is A08
                    Victim[CellIndex].Effect = EffectStr
            
            # Print the last row, swap the current row to the last row:
            OutputFile.write(self.RowToString(OldRow)+"\n")
            PatternRowNumber += 1
            if PatternRowNumber>=200:
                OutputFile.write("\n\n\nModPlug Tracker  IT\n")
                PatternRowNumber = 0
            OldRow = CacheRows[-1]


Bob = Munger(float(sys.argv[2]))#8.5416666666666661)
Bob.MungeFile(sys.argv[1])
