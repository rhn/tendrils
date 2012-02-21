TheFile = open("DKCMusic.txt","r")

LineIndex = -1
BlankCount = 0
PrevFileLine = ""
for FileLine in TheFile.xreadlines():
    FileLine = FileLine.strip()
    if len(FileLine)<1:
        continue
    if FileLine[:7] == "ModPlug":
        print FileLine
        continue
    LineIndex += 1
    if FileLine[:2]=="|.":
        # This line is blank.
        BlankCount += 1
        PrevFileLine = FileLine
    else:
        if BlankCount<2:
            print PrevFileLine
        BlankCount = 0
        
    print FileLine
    