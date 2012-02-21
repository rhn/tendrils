WordDict = {}
LetterDicts = [{}, {}, {}, {}]

def LoadWordDicts():
    global WordDict
    global LetterDicts
    File = open("2of12inf.txt","r")
    for FileLine in File.xreadlines():
        Word = FileLine.strip().lower()
        if not Word:
            continue
        if len(Word)==6:
            print Word,
        if len(Word)==4:
            WordDict[Word] = 1
            for Index in range(4):
                if not LetterDicts[Index].has_key(Word[Index]):
                    LetterDicts[Index][Word[Index]] = []
                LetterDicts[Index][Word[Index]].append(Word)
class WordSquareBuilder:
    def __init__(self):
        self.WordGrid = {}
        self.Words = []
        self.UsedWords = {}
    def BuildWordSquares(self, Size = 4):
        for X in range(Size):
            for Y in range(Size):
                self.WordGrid[(X,Y)] = ""
        self.AddWords(0)
    def AddWords(self, Index):
        if Index == 0:
            PossibleWords = WordDict.keys()
        else:
            if self.UsedWords.get(self.Words[0]):
                return
            Letter = self.Words[0][Index]
            PossibleWords = LetterDicts[0][Letter]
            #print "Letter %d must be %s"%(Index, Letter)
            #print "Got possibles:", len(PossibleWords), PossibleWords[:10]
        for Word in PossibleWords:
            Ok = 1
            if Index:
                for OldIndex in range(0, Index):
                    if self.Words[OldIndex][Index] != Word[OldIndex]:
                        #print self.Words, "%s collides at %s with %s (%s vs %s)"%(Word, OldIndex, self.Words[OldIndex], Word[OldIndex], self.Words[OldIndex][Index])
                        Ok = 0
                        break
            if Ok:
                self.Words.append(Word)
                # Recurse:
                if Index == 3:
                    self.PrintGrid()
                    self.UsedWords[self.Words[0]] = 1
                else:
                    self.AddWords(Index+1)
                # Remove again:
                self.Words.remove(Word)
    def PrintGrid(self):
        print "+----+"
        for Word in self.Words:
            print "|%s|"%Word
        print "+----+"
        print

if __name__ == "__main__":
    LoadWordDicts()
    #print len(WordDict.keys())
    #print LetterDicts[0]["a"]
    #print LetterDicts[2]["a"]
    #print WordDict.keys()[:10]
##    WordMeister = WordSquareBuilder()
##    print "Build word squares..."
##    WordMeister.BuildWordSquares()
##    print "ALL DONE!"