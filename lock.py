import random
import time
from SeanMatrix import *

class Grid:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.matrix = Matrix([[0 for j in range(w)] for i in range(h)])
        self.size = w * h
        self.solution = []
        self.nonSingular = 2
        self.generateTransform()
        self.clicks = 0
        self.helps = 0

    def findSolution(self):
        dim = self.transform.shape()[0]             # find number of rows
        b = self.vectorState()                      # find state Vector
        augment = self.transform.augment(b)         # create augmented matrix
        rref = augment.modRref()                    # find the modular rref
        basis = rref.createBasis()                  # create basis of solution space
        self.solSpace(basis)                        # find solution from the basis

    def solSpace(self, veclist, base = 2):
        """Takes a list of vectors defining a basis, and returns a list of possible values for the mod space"""
        solutions = [(veclist[0].nonZero() + 1).toList()]    # first solution is trivial, constant portion of space
        parameters = len(veclist) - 1                       # find the total number of parameterized vectors
        combos = pow(base, parameters)                      # find the total number of solutions (base number to the power of parameters)
        for i in range(1,combos):                           # for each combo (starting at one, because we already have the zeroth
            val = i
            sum = veclist[0]                                # grab the constant - sum is a Vector
            parm = 1                                        # index into the parameters
            while (val > 0):
                mult = val % base                           # the multiplier for the row
                val = val / base                            # the remainder for the next row
                if (mult == 0):                             # if the multiplier is 0, skip to the next vector
                    parm += 1
                    continue
                add = veclist[parm] * mult                  # multiply parameter vector by multiplier
                sum = (sum + add) % 2                       # perform addition
                #sum = modAdd(sum, add, base)            
            sol = (sum.nonZero() + 1).toList()              # convert to a list of lights
            if (not(sol in solutions)):                     # if this solution isn't unique, don't add it
                solutions.append(sol)
        answer = solutions[0]
        for sol in range(1,len(solutions)):                 # for
            if (len(solutions[sol]) < len(answer)):
                answer = solutions[sol]
        self.solution = answer    
    
    def generateTransform(self):    # converted to Sean Matrix
        """Creates general transform matrix for this light grid."""
        self.transform = Matrix()                           # create empty matrix
        for i in range(self.size):                          # for each entry in x vector
            sol = Vector([0 for j in range(self.size)])     # create Vector representing a "click"
            sol[i] = 1                                      # set the ith light to "clicked"
            self.toggleMatrix(i+1)                          # toggle the grid at the ith light
            state = self.vectorState()                      # grab the grid's state as a vector
            self.toggleMatrix(i+1)                          # untoggle the grid at the ith light
            self.transform = self.transform.augment(state)  # augment transform matrix with state vector            
        self.nonSingular = round(self.transform.det())      # determine if transform is non-singular (non-zero determinant)

    def reset(self):                # converted to SeanMatrix
        self.matrix = Matrix([[0 for j in range(w)] for i in range(h)])
        
    def vectorState(self):          # converted to SeanMatrix
        state = Vector([0 for j in range(self.size)])
        for i in range(self.size):
            state[i] = self.getLight(i+1)
        return state
    
    def setState(self, vec):                # converted to SeanMatrix
        for i in range(1,len(vec)+1):
            self.setLight(i,vec[i-1])

    def __repr__(self):                     # converted to SeanMatrix
        return str(self.matrix)

    def setLight(self, location, value):    # converted to SeanMatrix
        location -= 1
        row = location / self.width
        col = location % self.width
        self.matrix[row][col] = value

    def getLight(self,location):            # converted to SeanMatrix
        location -= 1
        row = location / self.width
        col = location % self.width
        return self.matrix[row][col]

    def allOn(self):                        # converted to SeanMatrix
        for location in range(self.size):
            row = location / self.width
            col = location % self.width
            self.matrix[row][col] = 1
            
    def evalClick(self, square):                # converted to SeanMatrix
        """Evalueates a click on a light"""
        # receive which square they've clicked on.
        if self.nonSingular:                    # if there exists a unique solution
            if square in self.solution:         # if the square they've selected in part of the solution
                self.solution.remove(square)    # remove that move from the solution
            else:
                self.solution.append(square)    # otherwise add it to the solution
        changed = self.toggleMatrix(square)     # toggle the grid
        self.clicks += 1                        # count click
        return changed

    def solved(self):                           # converted to SeanMatrix
        """Returns 1 if puzzle is solved, otherwise 0"""
        for i in range(self.height):            # for each row of lights
            if not(self.matrix[i].allZeros()):  # if row ISN'T all zeros
                return 0
        return 1
        
    def nextMove(self, randomVal = 1):      # converted to SeanMatrix
        """Returns the next helpful move."""
        if (not(self.solved())):            # if there are solutions left
            self.helps += 1
            if not(self.nonSingular):       # if there is no unique solution
                self.findSolution()
            if randomVal:
                val = random.randint(0,len(self.solution)-1)
            else:
                val = 0
            #print self.solution
            return self.solution[val], len(self.solution)
        return -1
            
    def toggleMatrix(self, location): # converted to SeanMatrix
        """Toggles target square and neighbors.  Returns list of changes"""
        locations = [location]
        location -= 1
        if (location >= (self.width * self.height)):
            raise IndexError, "Invalid location input: %d" % (location + 1)
        row = location / self.width
        col = location % self.width
        # toggle actual button
        self.matrix[row][col] = (self.matrix[row][col] + 1) % 2
        # If it has an upper neighbor, toggle it.
        if (row - 1) >= 0:
            self.matrix[row-1][col] = (self.matrix[row-1][col] + 1) % 2
            locations.append(self.width * (row - 1) + col + 1)
        # If it has a lower neighbor, toggle it.
        if (row + 1) < self.height:
            self.matrix[row+1][col] = (self.matrix[row+1][col] + 1) % 2
            locations.append(self.width * (row + 1) + col + 1)
        # If it has a left neighbor, toggle it.
        if (col - 1) >= 0:
            self.matrix[row][col-1] = (self.matrix[row][col-1] + 1) % 2
            locations.append(self.width * row + (col - 1) + 1)
        # If it has a right neighbor, toggle it.
        if (col + 1) < self.width:
            self.matrix[row][col+1] = (self.matrix[row][col+1] + 1) % 2
            locations.append(self.width * row + (col + 1) + 1)
        return locations

    def randomize(self, ease = 0):
        """Random start state.  0 >= ease >= width*height/2
           -- higher numbers are easier to solve"""
        if (ease >= (self.size / 2)):           # If it's easier than reality allows
            raise "InvalidArgument", "Difficulty level (%d) too high." % (ease)
        mixup = range(1,self.size + 1)          # create list of all possible clicks
        random.shuffle(mixup)                   # mix up the list
        moves = (self.size / 2) - ease          # define the number of moves
        generation = []
        for i in range(moves):                  # an element from the list of possible clicks
            m = mixup.pop(0)                    # remove the move from the list
            generation.append(m)                # track the clicks used to create initial state
            self.toggleMatrix(m)                # change the matrix
        if self.nonSingular:                    # if there exists a unique solution
            generation.sort()
            self.solution = generation   # solution is the ordered list of clicks
        else:
            self.findSolution()                  # otherwise, crunch out the solution

if __name__ == "__main__":
    g = Grid(2,2)   # init grid
    print g.transform
    print g.nonSingular
    print g
    #g.randomize()   # fill grid
    #g.allOn()
##    print g         # display initial grid
##    while (not g.solved()):
##        print "\t\tClick on %d." % (g.nextMove()[0])
##        print "Following lights changed:",g.evalClick(g.nextMove()[0])
##        print g
##    print "SOLVED!!!"

