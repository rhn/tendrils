import Numeric

def modRref(augmented, base = 2):
    """Performs rref with modular addition on given base"""
    numRows = augmented.shape[0]                    # total number of rows
    for var in range(numRows):                      # for each row
        leadVariable = 0                            # determine if this var HAS a lead variable
        if (augmented[var][var] == 0):              # make sure the ith column for the ith row is non-zero
            for search in range(var+1, numRows):    # for all of the following rows
                if (augmented[search][var] != 0):   # if this has a non-zero value in the variable column
                    rowSwap(augmented, search, var) # swap rows
                    leadVariable = 1                # indicate that we have a lead variable
                    break                           # continue
        else:
            leadVariable = 1                        # simply indicate we have a lead variable
        if (leadVariable):                          # if we have a lead variable
            for checkRow in range(numRows):         # go through all the rows
                if (checkRow == var):               # skip this row
                    continue
                if (augmented[checkRow][var] == 0): # if this checked row is already zero in this variable column
                    continue                        # skip it
                rowModAdd(augmented, var, checkRow, base)
 

def modAdd(a, b, base = 2):
    """Mod base 2 adds two vectors returning the result"""
    if (a.shape[0] != b.shape[0]):                     # make sure vectors are the same size
        raise "IllegalArgument", "Vectors not same size."
    return (a + b) % base

def rowModAdd(matrix, src, dest, base = 2):
    matrix[dest] = modAdd(matrix[src], matrix[dest])

def rowSwap(matrix, a, b):
    al = matrix[a].tolist()
    bl = matrix[b].tolist()
    for i in range(len(al)):
        matrix[b][i] = al[i]
        matrix[a][i] = bl[i]

def createBasis(rref):
    dim = rref.shape[0] - 1                 # get index of last row
    varlist = []                     # the last column is a minimum basis
    basis = [Numeric.transpose(rref)[dim + 1]]  # create empty list of vectors
    while (dim >= 0):                       # count backwards through the rows
        if (allZeros(rref[dim])):           # if this row is all zeros
            varlist.append(dim)             # add this variable # to the list
            dim -= 1
        else:
            break                           # otherwise there are no more free variables
    for var in varlist:                     # for each variable
        b = Numeric.transpose(rref)[var]
        b[var] = 1
        basis.append(b)
    return basis

def solSpace(veclist, base = 2):
    """Takes a list of vectors defining a basis, and returns a list of possible values for the mod space"""
    solutions = [(Numeric.nonzero(veclist[0]) + 1).tolist()]    # first solution is trivial, constant portion of space
    parameters = len(veclist) - 1                   # find the total number of parameterized vectors
    combos = pow(base, parameters)                  # find the total number of solutions (base number to the power of parameters)
    for i in range(1,combos):                       # for each combo (starting at one, because we already have the zeroth
        val = i
        sum = veclist[0]                            # grab the constant
        parm = 1                                    # index into the parameters
        while (val > 0):
            mult = val % base                       # the multiplier for the row
            val = val / base                        # the remainder for the next row
            if (mult == 0):                         # if the multiplier is 0, skip to the next vector
                parm += 1
                continue
            add = veclist[parm] * mult              # multiply parameter vector by multiplier
            sum = modAdd(sum, add, base)            # perform addition
        sol = (Numeric.nonzero(sum) + 1).tolist()   # convert to a list of lights
        if (not(sol in solutions)):                 # if this solution isn't unique, don't add it
            solutions.append(sol)
    answer = solutions[0]
    for sol in range(1,len(solutions)):             # for
        if (len(solutions[sol]) < len(answer)):
            answer = solutions[sol]
    return answer

def allZeros(vec):
    for i in vec:
        if (i != 0):
            return False
    return True

##def validBasis(matrix):             # not really necessary for light's out because every matrix will have a valid basis
##    for vec in veclist:
##        last = len(vec) - 1         # find the last element
##        if (vec[last] != 0):        # if the constant

def modBasis(veclist):
    for vec in veclist:
        mod2Vector(vec)

def mod2Vector(vec):
    dim = vec.shape[0]
    for i in range(dim):
        vec[i] = vec[i] % 2

if __name__=="__main__":
    a = Numeric.array([[1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
       [1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
       [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
       [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]])
    b = Numeric.array([[0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,1]])
    aug = Numeric.concatenate((a,Numeric.transpose(b)),1)
    modRref(aug)
    print aug
    basis = createBasis(aug)
    print basis
    solList = solSpace(basis)
    print solList
                    
    