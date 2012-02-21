import os
import sys
import traceback
import random

Size = 17
Depth = 5

Wall = 0
FromUp = 1
FromDown = 2
FromNorth = 3
FromSouth = 4
FromWest = 5
FromEast = 6
Clear = 7
Entrance = 200
XDir = [0,  0,  0,  0, -1, 1]
YDir = [0,  0, -1,  1,  0, 0]
ZDir = [-1, 1,  0,  0,  0, 0]
Dirs = [0,1,2,3,4,5]
OppositeDir = [1,0,3,2,5,4]
NextDir = [1,2,3,4,5,0]
ContentsToBacktrack = {FromUp: 0, FromDown:1, FromNorth: 2, FromSouth:3, FromWest:4,
                       FromEast:5}
DirContents = [FromDown, FromUp, FromSouth, FromNorth, FromEast, FromWest]

class MazeBuilder:
    def __init__(self):
        self.Map = []
        self.Distances = []
        for Index in range(Depth):
            Row = [Wall]*Size
            Grid = []
            DistGrid = []
            for Index in range(Size):
                Grid.append(Row[:])
                DistGrid.append(Row[:])
            self.Distances.append(DistGrid)
            self.Map.append(Grid)
    def GetSquareLabel(self, Contents):
        if Contents==Wall:
            return "X"
        else:
            return "."
    def DebugPrint(self, File):
        for Level in (0, 1, 2, 3,4):
            File.write("\n\n---Level %d---\n"%Level)
            File.write("  01234567890123456789\n")
            for Y in range(Size):
                Str = ""
                for X in range(Size):
                    Square = self.Map[Level][X][Y]
                    Str += self.GetSquareLabel(Square)
                File.write("%2d%s%s\n"%(Size-Y-1,Str, Size-Y-1))
            File.write("  01234567890123456789\n")
    def CanMove(self, Dir):
        X = self.X + XDir[Dir]*2
        Y = self.Y + YDir[Dir]*2
        Z = self.Z + ZDir[Dir]*2
        if X not in range(Size):
            return 0
        if Y not in range(Size):
            return 0
        if Z not in range(Depth):
            return 0
        if self.Map[Z][X][Y] != Wall:
            return 0
        return 1
    def WriteMazeFiles(self):
        LevelToDungeon = [5,0,6,0,7]
        for Z in (0, 2, 4):
            # Set up the master grid:
            MasterGrid = []
            MasterGridRow = ["0,1,1,1,1"]*30
            for Index in range(30):
                MasterGrid.append(MasterGridRow[:])
            # Write our stuff to the master grid:
            for X in range(Size):
                for Y in range(Size):
                    Cell = "0"
                    if (X, Y, Z) == self.BestPoint:
                        Cell = "666"
                    else:
                        if self.IsVacant(X,Y,Z,0) and self.IsVacant(X,Y,Z,1):
                            Cell = "6"
                        elif self.IsVacant(X,Y,Z,0):
                            Cell = "4"
                        elif self.IsVacant(X,Y,Z,1):
                            Cell = "5"
                    for Dir in [3,2,4,5]:
                        if self.IsVacant(X,Y,Z,None) and self.IsVacant(X,Y,Z,Dir):
                            Cell += ",0"
                        else:
                            Cell += ",1"
                    MasterGrid[29-Y][X] = Cell
            # Now write out the maze:
            FullPath = os.path.join("Mazes", "Level%d.txt"%(LevelToDungeon[Z]))
            File = open(FullPath,"w")
            for MasterRow in MasterGrid:
                for Cell in MasterRow:
                    File.write("%s\t"%Cell)
                File.write("\n")
            File.close()
    def IsVacant(self, X, Y, Z, Dir):
        if Dir!=None:
            X += XDir[Dir]
            Y += YDir[Dir]
            Z += ZDir[Dir]
        if X not in range(Size):
            return 0
        if Y not in range(Size):
            return 0
        if Z not in range(Depth):
            return 0
        if self.Map[Z][X][Y]==Wall:
            return 0
        return 1
    def BuildMaze(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        CurrentDistance = 0
        self.Map[self.Z][self.X][self.Y]= Entrance
        while (1):
            #self.DebugPrint()
            #print "Press <enter>",
            #sys.stdin.readline()
            # Pick a random direction.
            Dir = random.choice(Dirs[2:])            
            FirstDir = Dir
            Blocked = 0
            while (not self.CanMove(Dir)):
                Dir = NextDir[Dir]
                if Dir == FirstDir:
                    Blocked = 1
                    break
            # If we can move, do so:
            if not Blocked:
                self.X += XDir[Dir]
                self.Y += YDir[Dir]
                self.Z += ZDir[Dir]
                self.Map[self.Z][self.X][self.Y] = Clear
                self.X += XDir[Dir]
                self.Y += YDir[Dir]
                self.Z += ZDir[Dir]
                self.Map[self.Z][self.X][self.Y] = DirContents[Dir]
                CurrentDistance += 1
                self.Distances[self.Z][self.X][self.Y] = CurrentDistance
                continue
            # We must backtrack now:
            Contents = self.Map[self.Z][self.X][self.Y]
            if Contents == Entrance:
                break
            Dir = ContentsToBacktrack[Contents]
            self.X += XDir[Dir]*2
            self.Y += YDir[Dir]*2
            self.Z += ZDir[Dir]*2
            CurrentDistance -= 1
    def FindFarthestPoint(self):
        BestPoint = None
        BestDist = 0
        for Z in range(Depth):
            for X in range(Size):
                for Y in range(Size):
                    Dist = self.Distances[Z][X][Y]
                    if Dist > BestDist:
                        BestDist = Dist
                        BestPoint = (X,Y,Z)
        print "Furthest point:", BestPoint, BestDist
        self.BestPoint = BestPoint

Builder = MazeBuilder()
Builder.BuildMaze()
Builder.DebugPrint(sys.stdout)
File = open("Map.txt","w")
Builder.DebugPrint(File)
File.close()
Builder.FindFarthestPoint()
Builder.WriteMazeFiles()