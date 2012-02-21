"Read lightsout stuff:"

def FirstImport():
    File = open("Reference\\Lights out - classic.txt","r")
    CurrentString = ""
    Index = 0
    MoveCount = 0
    for FileLine in File.xreadlines():
        if FileLine[0] in (".","X"):
            Str = FileLine[0]+FileLine[2]+FileLine[4]+FileLine[6]+FileLine[8]
            CurrentString += Str+","
            MoveCount += FileLine.count("O")
        elif CurrentString:
            # Ok, print one:
            Index += 1
            print """Puzzle = LightsPuzzleDefinition("%s", 5, 5, %s)
Puzzle.FillFromString("%s")
PuzzleDefinitions.append(Puzzle)
    """%(Index, MoveCount, CurrentString)
            CurrentString = ""
            MoveCount = 0
    Index += 1
    print """Puzzle = LightsPuzzleDefinition("%s", 5, 5, %s)
Puzzle.FillFromString("%s")
PuzzleDefinitions.append(Puzzle)
    """%(Index, MoveCount, CurrentString)

def SecondImport():
    File = open("Reference\\Lights out - 2000.txt","r")
    CurrentString = ""
    Index = 0
    MoveCount = 0
    for FileLine in File.xreadlines():
        if FileLine[0] in (".","X","R","G"):
            Str = FileLine[0]+FileLine[2]+FileLine[4]+FileLine[6]+FileLine[8]
            CurrentString += Str+","
            MoveCount += FileLine.count("1")
            MoveCount += FileLine.count("2")*2
        elif CurrentString:
            # Ok, print one:
            Index += 1
            print """Puzzle = LightsPuzzleDefinition("X %s", 5, 5, %s)
Puzzle.FillFromString("%s")
PuzzleDefinitions.append(Puzzle)
"""%(Index, MoveCount, CurrentString)
            CurrentString = ""
            MoveCount = 0
    Index += 1
    print """Puzzle = LightsPuzzleDefinition("X %s", 5, 5, %s)
Puzzle.FillFromString("%s")
PuzzleDefinitions.append(Puzzle)
    """%(Index, MoveCount, CurrentString)

        

            

FirstImport()
SecondImport()