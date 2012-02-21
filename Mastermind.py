import sys
import random
def PlayGame():
    Digits = "12345"
    SecretCode =""
    CodeLength = 4
    for Position in range(CodeLength):
        SecretCode += random.choice(Digits)
    GuessCount = 0
    while (1):
        print "Enter four digits from 1 to 5: ",
        Guess = sys.stdin.readline()
        GuessCount += 1
        # Make sure it's 4 characters long:
        Padding = " " * (CodeLength - len(Guess))
        Guess = Guess[:CodeLength] + Padding
        PositionUsed = [0,0,0,0]
        # Give black pegs for correct guesses:
        BlackPegs = 0
        for Position in range(CodeLength):
            if Guess[Position] == SecretCode[Position]:
                BlackPegs += 1
                PositionUsed[Position] = 1
        # Give white pegs for partly-correct guesses:
        WhitePegs = 0
        for Position in range(CodeLength):
            if Guess[Position] == SecretCode[Position]:
                continue
            for OtherPosition in range(CodeLength):
                if Guess[OtherPosition] == SecretCode[Position]\
                and not PositionUsed[OtherPosition]:
                    WhitePegs += 1
                    PositionUsed[OtherPosition] = 1
                    break
        print "%d Black, %d White"%(BlackPegs, WhitePegs)
        if (BlackPegs == CodeLength):
            print "Congratulations!  You used %d guesses."%GuessCount
            break

PlayGame()        