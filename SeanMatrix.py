import math
import time

class Vector:
    """Vector object"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    def __init__(self, elements = []):
        if (len(elements) != 0):
            if isinstance(elements[0], type([])):       # if it's a vertical vector
                    self.direction = Vector.VERTICAL
            elif isinstance(elements[0], type(1)) or isinstance(elements[0], type(1.0)):    # horizontal vector
                self.direction = Vector.HORIZONTAL
            else:
                raise "IllegalArgument", "Incorrect input types for Vector"
        self.elements = [i for i in elements]       # create list of elements
        self.size = len(elements)                   # determine size
    
    def __repr__(self):
        """Prints vector as a list"""
        st = "Vector["
        for i in range(0, self.size):
            st += str(self.elements[i]) + ", "
        st =  st[:-2] + "]"
        return st

    def __add__(self, vec):
        if isinstance(vec, Vector):                     # find out if we're adding vectors
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            sum = Vector([0 for i in range(self.size)]) # create destination vector
            for i in range(self.size):
                sum[i] = self[i] + vec[i]               # element-by-element summation
        elif (isinstance(vec, type(3)) or isinstance(vec, type(3.4))):  # argument is int or float
            sum = Vector([0 for i in range(self.size)]) # element-by-element addition
            for i in range(self.size):
                sum[i] = self[i] + vec
        else:
            raise "IllegalArgument", "Can only add vectors and scalars"  # no valid input
        if (self.direction == Vector.HORIZONTAL):       # return same direction as left-hand vector
            return sum
        else:
            return sum.transpose()

    def __radd__(self, vec):
        if isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            sum = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                sum[i] = self[i] + vec[i]
        elif (isinstance(vec, type(3)) or isinstance(vec, type(3.4))):
            sum = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                sum[i] = self[i] + vec
        else:
            raise "IllegalArgument", "Can only add vectors and scalars"
        if (self.direction == Vector.HORIZONTAL):   # return same direction of left-hand vector
            return sum                              # if argument is scalar, resultant vector is horizontal
        else:
            return sum.transpose()
        
    def __sub__(self,vec):
        vec2 = vec * -1                             # negate argument
        return self + vec2                          # add the negative

    def __rsub__(self,vec):         
        vec2 = self * -1                            # negate self
        return vec + vec2                           # add the negative
    
    def __div__(self, vec):
        if (isinstance(vec, type(3)) or isinstance(vec, type(3.4))):
            return self * (1/float(vec))
        elif isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            div = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                div[i] = float(self[i]) / vec[i]
            return div

    def __rdiv__(self, vec):
        if (isinstance(vec, type(3)) or isinstance(vec,type(3.4))):
            div = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                div[i] = float(vec) / self[i]
        elif isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            div = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                div[i] = float(vec[i]) / self[i]
        return div
                
    def __mod__(self, vec):
        if (isinstance(vec, type(3)) or isinstance(vec, type(3.2))):
            md = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                md[i] = self[i] % vec
        elif isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            md = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                md[i] = self[i] % vec[i]
        else:
            raise "IllegalArgument", "Wrong arguments for modulo"
        return md

    def __rmod__(self, vec):
        if (isinstance(vec, type(3)) or isinstance(vec, type(3.2))):
            md = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                md[i] = vec % self[i]
        elif isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            md = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                md[i] = vec[i] % self[i] 
        else:
            raise "IllegalArgument", "Wrong arguments for modulo"
        return md

    def __neg__(self):
        negative = Vector([0 for i in range(self.size)])
        for i in range(self.size):
            negative[i] = -self[i]
        return negative
    
    def __mul__(self, vec):
        if isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            prod = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                prod[i] = self[i] * vec[i]
        elif (isinstance(vec, type(3)) or isinstance(vec, type(3.4))):
            prod = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                prod[i] = self[i] * vec
        else:
            raise "IllegalArgument", "Can only add vectors and scalars"
        if (self.direction == Vector.HORIZONTAL):
            return prod
        else:
            return prod.transpose()

    def __rmul__(self, vec):
        if isinstance(vec, Vector):
            if (len(vec) != self.size):
                raise "IllegalArgument", "Vectors need to be same length."
            prod = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                prod[i] = self[i] * vec[i]
        elif (isinstance(vec, type(3)) or isinstance(vec, type(3.4))):
            prod = Vector([0 for i in range(self.size)])
            for i in range(self.size):
                prod[i] = self[i] * vec
        else:
            raise "IllegalArgument", "Can only add vectors and scalars"
        if (self.direction == Vector.HORIZONTAL):
            return prod
        else:
            return prod.transpose()        
    
    def __len__(self):
        return self.size

    def __setitem__(self, index, value):
        if self.direction == Vector.HORIZONTAL:
            self.elements[index] = value
        else:
            self.elements[index][0] = value
        
    def __getitem__(self, index):
        if self.direction == Vector.HORIZONTAL:
            return self.elements[index]
        else:
            return self.elements[index][0]

    def normalize(self):
        """Returns a vector in the same direction
           who's length is 1"""
        norm = Vector([0 for i in range(self.size)])    # create holder for returning vector
        mag = self.magnitude()                          # find magnitude of vector
        for i in range(self.size):                      # for each element
            norm[i] = self[i] / mag                     # store the value / magnitude in normal vector
        return norm                                     # return vector
    
    def angleD(self,vec):
        """Returns angle (in degrees) between this vector
           and the vector passed"""
        ang = self.angleR(vec)                          # get the angle in radians
        return ang * 180 / math.pi                      # convert to degrees

    def angleR(self, vec):
        """Returns angle (in radians) between this vector
           and the vector passed"""
        # uses the relationship a . b = |a||b|cos(x) -> (a . b)/|a||b| = cos(x)
        top = self.dotProduct(vec)                      # find the value of the dot product
        bottom = vec.magnitude() * self.magnitude()     # find the product of their magnitudes
        return math.acos(top/bottom)                    # Take the arc cosine

    def magnitude(self):
        """Returns the magnitude of the vector.
           The square root of the sum of the squares of the values."""
        sum = 0                                     # initialize accumulator
        if self.direction == Vector.HORIZONTAL:     # determine if it's a horizontal vector
            for el in self.elements:                # for each element
                sum += math.pow(el,2)               # accumulate (summed) squares of elements
        else:                                       # if it's vertical
            for el in self.elements:                # for each element
                sum += math.pow(el[0],2)            # extract value
        return math.sqrt(sum)                       # return square root of sum

    def dotProduct(self, vec):
        """Returns the dot product between this vector
           and an equal-lengthed vector supplied as argument"""
        if (len(vec) != self.size):         # make sure arguments are same size
            raise "IllegalArgument", "Vectors need to be same length."
        if self.direction == Vector.VERTICAL:   # make left argument horizontal
            left = self.transpose()
        else:
            left = self.elements
        if vec.direction == Vector.VERTICAL:    # make right argument horizontal
            right = self.transpose()
        else:
            right = vec
        dp = 0                                  # accumulator for dot product value
        for i in range(self.size):
            dp += left[i] * right[i]            # multiply element-by-element and sum result
        return dp

    def transpose(self):
        """Returns transpose of vector"""
        if self.direction == Vector.HORIZONTAL:             # if horizontal
            trans = Vector([[i] for i in self.elements])    # create list of lists
        else:                                               # if vertical
            elem = []                                       # create empty list for catching values
            for el in self.elements:                        # iterate through elements
                elem.append(el[0])                          # add element to list
            trans = Vector(elem)                            # construct transposed vector
        return trans                                        # return vector
    
    def crossProduct(self, vec):
        """Takes cross product with this R3 vector
           and an R3 vector supplied as argument"""
        if self.size != 3 and vec.size != 3:                    # test for valid size
            raise "Illegal Argument", "Only for 3D vectors"
        x = self[1] * vec[2] - self[2] * vec[1]                 # find each term
        y = self[2] * vec[0] - self[0] * vec[2]
        z = self[0] * vec[1] - self[1] * vec[0]
        return Vector([x,y,z])                                  # construct and return cross product

    def matrixLeftMultiply(self, matrix):
        pass

    def concatenate(self, vec):
        if isinstance(vec, type([1])) or isinstance(vec, Vector):        # appending a list
            concat = Vector([i for i in self] + [i for i in vec])
        else:
            raise "IllegalArgument", "Need to append list or Vector"
        return concat
    
    def toList(self):
        """Return the matrix as a list"""
        return self.elements

    def allZeros(self):
        """Reports if the vector is only zeros"""
        for i in self:
            if i != 0:
                return 0
        return 1

    def leadVariable(self):
        """Reports the index of the first non-zero value
           Returns -1 if all zeros"""
        for i in range(self.size):
            if self[i] != 0:
                return i
        return -1

    def nonZero(self):
        """Returns Vector of all indeces with non-zero values"""
        nz = []
        for i in range(self.size):
            if self[i] != 0:
                nz.append(i)
        return Vector(nz)

class Matrix:
    def __init__(self, array = []):
        if len(array) == 0:                     # empty list
            self.undefined = 1
            return
        self.undefined = 0
        self.rows = len(array)
        self.cols = len(array[0])
        for sublist in array:
            if self.cols != len(sublist):
                raise "IllegalArgument", "Matrix must be rectangular"
        self.grid = [Vector(i) for i in array]

    def __repr__(self):
        """Prints matrix as a grid of lists"""
        if self.undefined:
            return "[]"
        st = "Matrix["                  # initialize string for matrix
        for row in self.grid:    # for each row
            st += str(row)[6:] + "\n       "
        st = st[:-8] + "]"
        return st

    def __getitem__(self, key):
        """Grabs the indexed ROW"""
        if self.undefined:
            return None
        return self.grid[key]

    def __setitem__(self, key, value):
        if self.undefined:
            return
        if not(isinstance(value, Vector)):
            raise "IllegalArgument", "Only Vectors can be placed into a matrix."
        self.grid[key] = value

    def shape(self):
        if self.undefined:
            return (0,0)
        return (self.rows, self.cols)

    def augment(self, mat):
        """Creates a new matrix with the argument
           appended to the right side of the matrix"""
        if isinstance(mat, Vector):                     # argument is a vector
            if self.undefined:                          # empty matrix
                grid = []
                for i in range(mat.size):               # for each element in the vector
                    grid.append([mat[i]])
            else:
                height = self.shape()[0]                    # grab height of vector
                if (height != len(mat)):
                    raise "IllegalArgument", "Vector must be same height as matrix."
                grid = []                                   # build new matrix grid
                for i in range(self.rows):                  # for each element in the vector
                    grid.append(self[i].toList() + [mat[i]])    # create new list
        elif isinstance(mat, Matrix):
            if self.undefined:
                return mat
            if self.rows != mat.rows:
                raise "IllegalArgument", "Matrices must have equal number of rows"
            grid = []
            for i in range(self.rows):
                grid.append(self[i].toList() + mat[i].toList())
        else:
            raise "IllegalArgument", "Argument must be Vector or Matrix"
        return Matrix(grid)

    def isSquare(self):
        if self.undefined:
            return 1
        return self.rows == self.cols

    def cofactor(self, r, c):
        """Returns cofactor based on the element at r,c"""
        if self.undefined:                              # if empty matrix
            return None                                 # return none
        cof = []                                        # create empty grid for cofactor
        for rows in range(self.rows):                   # for each row
            if rows == r:                               # if the row is the row of the cofactor variable
                continue                                # skip it
            thisrow = []                                # create empty list for cofactor row
            for cols in range(self.cols):               # for each variable in column
                if cols == c:                           # if the col is the col of the cofactor variable
                    continue                            # skip it
                thisrow.append(self[rows][cols])        # otherwise, append this value to the row list
            cof.append(thisrow)                         # append the row to the grid
        return Matrix(cof)                              # create matrix of cofactor

    def det(self):
        if self.undefined:                              # if matrix isn't defined
            return None
        if (not(self.isSquare())):                      # if matrix isn't square, det is undefined
            raise "IllegalState", "Determinant only defined for square matrix."
        if (self.shape()[0] <= 0):                      # if matrix is empty, det is undefined
            raise "IllegalState", "Determinant not defined for empty matrix"
        if (self.shape()[0] == 1):                      # if matrix is 1 x 1, det is merely the element
            return self[0][0]
        if (self.shape()[0] == 2):                      # if matrix is 2 x 2, det is ad - bc
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]
        # doesn't seem to have much value to perform cofactor expansion for determinant
        # not even for 3 x 3
##        if (self.shape()[0] < 3):                       # if matrix is small enough, perform cofactor
##            print "cofactor method"
##            det = 0
##            for i in range(self.rows):                  # for each element of the row
##                if (i % 2) == 0:                        # signs for cofactor expansion
##                    sign = -1
##                else:
##                    sign = 1
##                det += sign * self[0][i] * self.cofactor(0,i).determinant()
        else:
            # diagonalize method
            diag, determ = self.diagonalize()              # diagonalize the matrix, grab the factor resultant from swapping rows
            for i in range(self.rows):                  # for each diagonal element
                determ *= diag[i][i]                       # multiply diagonal values
        return determ                                      # return product
            
    def transpose(self):
        """Returns transpose of the matrix"""
        if self.undefined:                          # if matrix is undefined
            return Matrix()                         # return a new, undefined matrix
        t = Matrix(self[0].transpose().toList())    # create matrix of the transpose of first row
        for i in range(1,self.rows):                # iterate through the rest of the rows
            t = t.augment(self[i])                  # augment t with the transpose of each row
        return t                                    # return t

    def getRowVector(self, index):
        """Same as just indexing into the matrix[index]"""
        if self.undefined:              # if matrix is undefined
            return None
        return self[index]              

    def getColVector(self, index):
        if self.undefined:          # if matrix is undefined
            return None
        temp = self.transpose()     # transpose the matrix
        return temp[index]          # return the corresponding row of the transposed matrix

    def matrixMultiply(self, mat):
        """Right multiplies supplied matrix argument to this matrix
           Returns none if either matrix is undefined"""
        if self.undefined or mat.transpose:                 # if either matrix is undefined
            return None
        if (isinstance(mat,Matrix)):
            if self.cols != mat.rows:       # can't perform multiplication
                raise "IllegalArgument", "Input matrix must have the same height as this matrix's width"
            mul = Matrix([[0 for col in range(mat.cols)] for row in range(self.rows)])  # create empty result
            matT = mat.transpose()
            for r in range(self.rows):                  # for each row
                for c in range(mat.cols):                # for each column in row
                    mul[r][c] = self[r].dotProduct(matT[c])
        elif (isinstance(mat, Vector)):
            if self.cols != len(mat):
                raise "IllegalArgument", "Input vector must have same height as matrix"
            mul = Matrix([[0] for i in range(self.rows)])
            for r in range(self.rows):
                mul[r][0] = self[r].dotProduct(mat)
        else:
            raise "IllegalArgument", "Argument must be Matrix or Vector"
        return mul

    def rowSwap(self, a, b):
        if self.undefined:          # if undefined,
            return None             # do nothing and return None
        """Swaps two rows in a matrix and returns the impact on the determinant"""
        if (a >= self.rows or b >= self.rows or a < 0 or b < 0):    # if a or b are beyond scope of matrix
            raise "IllegalArgument", "Invalid row number"           # raise exception
        for i in range(self.cols):                                  # for each element in the two rows
            temp = self[a][i]                                       # normal swap
            self[a][i] = self[b][i]
            self[b][i] = temp
        return -1                                                   # a swap negates the determinant

    def rowAdd(self, src, dest, mult = 1):
        if self.undefined:                      # if matrix is undefined
            return                              # do nothing
        if (src >= self.rows or dest >= self.rows or src < 0 or dest < 0):  # rows outside of scope of matrix
            raise "IllegalArgument", "Invalid row number"                   # raise exception
        self[dest] = self[dest] + (self[src] * mult)                        # perform vector math

    def rowModAdd(self, src, dest, base = 2):
        if self.undefined:                                                  # if matrix is undefined
            return                                                          # do nothing
        if (src >= self.rows or dest >= self.rows or src < 0 or dest < 0):  # if rows are outside scope of matrix
            raise "IllegalArgument", "Invalid row number"                   # raise exception
        self[dest] = (self[dest] + self[src]) % base                        # otherwise perform vector math
        
    def rowMul(self, dest, mult = 1):
        """Multplies row by given value, returns inverse of the value for
           consideration in determinant"""
        if self.undefined:                                  # matrix undefined
            return None                                     # return None
        if (dest >= self.rows or dest < 0):                 # if row outside of matrix's scope
            raise "IllegalArgument", "Invalid row number"   # raise exception
        self[dest] = self[dest] * mult                      # perform vector math
        return (1 / mult)                                   # Return inverse of multiplier - for determinant

    def clone(self):
        if self.undefined:                                                          # if matrix undefined
            return Matrix()                                                         # return a new empty matrix
        copy = Matrix([[0 for i in range(self.cols)] for j in range(self.rows)])    # create new, empty matrix
        for r in range(self.rows):                                                  # for each row
            for c in range(self.cols):                                              # iterate through column values
                copy[r][c] = self[r][c]                                             # copy value from here to clone
        return copy                                                                 # return copy

    def modRref(self, base = 2):
        if self.undefined:                              # if matrix undefined
            return Matrix()                             # return undefined matrix
        aug = self.clone()                              # copy the matrix
        for var in range(self.rows):                    # for each row
            leadVariable = 0                            # determine if this var HAS a lead variable
            if (aug[var][var] == 0):                    # make sure the ith column for the ith row is non-zero
                for search in range(var+1, self.rows):  # for all of the following rows
                    if (aug[search][var] != 0):         # if this has a non-zero value
                        aug.rowSwap(search,var)         # swap rows
                        leadVariable = 1                # indicate that we have a lead variable
                        break                           # stop looking
            else:
                leadVariable = 1                        # simply indicate we have a lead variable
            if (leadVariable):                          # if we have a lead variable
                for checkRow in range(self.rows):       # go through all the rows
                    if (checkRow == var):               # skip its own row
                        continue
                    if (aug[checkRow][var] == 0):       # If this is already 0, we need do nothing
                        continue
                    aug.rowModAdd(var, checkRow, base)
        return aug

    def diagonalize(self):
        if self.undefined:                                  # if the matrix is undefined
            return Matrix()                                 # return empty matrix
        aug = self.clone()                                  # copy the matrix
        swapfactor = 1
        for var in range(self.rows - 1):                    # for each row (except the last)
            leadVariable = 0                                # determine if this var HAS a lead variable
            if (aug[var][var] == 0):                        # make sure the ith column for the ith row is non-zero
                for search in range(var+1, self.rows):      # for all of the following rows
                    if (aug[search][var] != 0):             # if this has a non-zero value
                        aug.rowSwap(search,var)             # swap rows
                        swapfactor = -swapfactor
                        leadVariable = 1                    # indicate that we have a lead variable
                        break                               # stop looking
            else:
                leadVariable = 1                            # simply indicate we have a lead variable
            if (leadVariable):                              # if we have a lead variable
                for checkRow in range(var + 1, self.rows):  # go through all the REST of the rows
                    if (checkRow == var):                   # skip its own row
                        continue
                    if (aug[checkRow][var] == 0):           # If this is already 0, we need do nothing
                        continue
                    checkVal = aug[checkRow][var]
                    varVal = aug[var][var]
                    mult = -(float(checkVal)/varVal)
                    aug.rowAdd(var, checkRow, mult)
        #aug[0] = aug[0] * factor
        return aug, swapfactor
    def createBasis(self):
        """Creates a solution basis for the matrix as a list of vectors.
           The first vector is a constant vector, all following vectors are
           parameterized."""
        if self.undefined:                                      # if matrix is undefined
            return []                                           # return empty list
        # this needs to be re-worked into a more general case
        # i.e. more variables than equations
        # Solution space for a non-rectangular transform matrix
        if (self.cols <= self.rows):
            raise "IllegalState", "Basis only valid where there are more columns than rows."
        dim = self.rows - 1                                     # get index of last row
        varlist = []                                            # prepare list for free variables
        trans = self.transpose()                                # create transpose of matrix
        basis = [trans[trans.rows - 1]]                         # grab the final "column"
        while (dim >= 0):                                       # count backwards through the rows
            if self[dim].allZeros():                            # if this row is all zeros
                varlist.append(dim)                             # add this variable # to the list
                dim -= 1
            else:
                break                                           # otherwise there are no more free variables
        for var in varlist:                                     # for each free variable
            b = trans[var]                                      # grab the "column" of the free variable
            b[var] = 1                                          # set this free variable to itself
            basis.append(b)                                     # append this space to the basis
        return basis
        
            
        

if __name__ == "__main__":
##    m1 = Matrix([[1,2],[2,3]])
    m2 = Matrix([[1,2,3],[3,2,5],[5,6,7]])
    m1 = Matrix([[1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1]])
##    m1 = Matrix([[1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
##                 [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
##                 [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
##                 [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
##                 [1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
##                 [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
##                 [0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
##                 [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
##                 [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
##                 [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0],
##                 [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
##                 [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
##                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
##                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0],
##                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
##                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]])
    v1 = Vector([1,0,1,0])
    #v1 = Vector([1,0,0,1,0,1,0,1,1,1,1,0,1,0,0,0])
    m3 = Matrix()
    print "Matrix unit test:"
    print m3
    print m3[0]
    m3[0] = 7
    print m3.shape()
    print m3.augment(m2)
    print m3.augment(v1)
    print m3.det()
    print m3.augment(m2).det()
##    print
##    print m1
##    start = time.clock()
##    print m2.determinant()
##    stop = time.clock()
##    print "Time elapsed for determinant:", (stop - start)
##    aug = m1.augment(v1)
##    print "augmented:"
##    print aug
##    augRref = aug.modRref()
##    print "Rref of aug"
##    print augRref
##    print m1.diagonalize()[0]
##    base = augRref.createBasis()
##    print base

    