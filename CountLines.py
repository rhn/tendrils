import os
import sys

Lines = 0
RealLines = 0
for FileName in os.listdir("."):
    Extension = os.path.splitext(FileName)[1]
    if Extension.lower()==".py":
        File = open(FileName, "r")
        for Line in File.readlines():
            Lines += 1
            Line = Line.strip()
            if Line and Line[0]!="#":
                RealLines += 1
        Lines += len(File.readlines())
        File.close()
print "Total lines:", Lines
print "Non-comment, non-empty:", RealLines