"""
Carriage returns.  Line feeds.  Their usage differs between OSes, which
occasionally gives rise to some rather miserable bugs.  In DOS/Windows,
text files end lines with a carriage return and a line feed (\r\n).  In
the Unix world, text files often end with just a line feed (\n).

For at least some versions of Python on Linux, lines broken by \r are
not split by the interpreter, which generally breaks code.  (Why are
source files not consistent?  I don't know; maybe I confused PythonWin
somehow.  It happened 3 times in all)

What this whining boils down to is: Source files should consistently
end in \n, so we change any lone \r characters to \n.
"""
import os
GoodLineBreak = "~~~>" + "CRLF" + "<~~~"
BadLineBreak = "~~~>" + "X" + "<~~~"
for FileName in os.listdir("."):
    Extension = os.path.splitext(FileName)[1]
    if Extension.lower()!=".py":
        continue
    File = open(FileName, "r")
    Text = File.read()
    File.close()
    Text = Text.replace("\r\n",GoodLineBreak)
    Count = Text.count("\r")
    #Count += Text.count("\n")
    print "Bad chars found in %s: %s"%(FileName, Count)
    if Count:
        Text = Text.replace("\r", BadLineBreak)
        #Text = Text.replace("\n", "\r\n")
        Text = Text.replace(BadLineBreak, "\n")
        Text = Text.replace(GoodLineBreak, "\n")
        File = open(FileName, "w")
        File.write(Text)
        File.close()