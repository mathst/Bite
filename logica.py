from unittest import result


# The class eleitorado is a blueprint for creating objects.
#
# The class defines the attributes and methods of the objects.
#
# The attributes are the variables that are defined in the __init__ method.
#
# The methods are the functions that are defined in the class.
#
# The __init__ method is a special method that is called when an object is created.
#
# The __init__ method is used to initialize the attributes of the object.
#
# The self parameter is a reference to the current instance of the class.
#
# The self parameter is used to access the attributes and methods of the class in python.
#
# The self parameter is not explicitly passed when calling a method.
#
# The self parameter is automatically passed when calling a method.
#
# The self parameter is used to access the attributes and methods of the class in python.
#
# The self parameter is used to access the attributes and
class eleitorado:
    def __init__(self, totalEleitores, eleitoresValidos, votosBrancos, votosNulos):
        self.totalEleitores = totalEleitores
        self.eleitoresValidos = eleitoresValidos
        self.votosBrancos = votosBrancos
        self.votosNulos = votosNulos

    def calcValidos(self):
        percentage = 100 * float(self.eleitoresValidos) / float(self.totalEleitores)
        result = str(percentage) + "%"
        print(result)
        return result

    def calcBrancos(self):
        percentage = 100 * float(self.votosBrancos) / float(self.totalEleitores)
        result = str(percentage) + "%"
        print(result)
        return result

    def calcNullos(self):
        percentage = 100 * float(self.votosNulos) / float(self.totalEleitores)
        result = str(percentage) + "%"
        print(result)
        return result


a = eleitorado(1000, 800, 150, 50)

a.calcValidos()
a.calcBrancos()
a.calcNullos()


# The bubble sort algorithm is a simple sorting algorithm that repeatedly steps through the list to be
# sorted, compares each pair of adjacent items and swaps them if they are in the wrong order. The pass
# through the list is repeated until no swaps are needed, which indicates that the list is sorted
class boubleShort:
    def __init__(self, v):
        self.v = v

    def bubbleSort(self):

        for i in range(len(self.v)):
            swapped = False

            for m in range(0, len(self.v) - i - 1):
                if self.v[m] > self.v[m + 1]:
                    temp = self.v[m]
                    self.v[m] = self.v[m + 1]
                    self.v[m + 1] = temp
                    swapped = True
                if not swapped:
                    break
        print(self.v)


v = boubleShort([5, 3, 2, 4, 7, 1, 0, 6])
v.bubbleSort()

# The class `factorial` takes a value `v` and calculates the factorial of `v` using a list
# comprehension
class factorial():
    
    def __init__(self, v):
        self.v = v
            
    def calc(self):
        s, v = 1, self.v
        r = [s for i in range(1, v+1) if (s := s*i)]
        print(r)
        return r
v = factorial(5)
v.calc()


# The class takes in a number and returns the sum of all the multiples of 3 or 5 below the number
class multImp():
    
    def __init__(self, v):
        self.v = v
        
    # take in a number
    def mult(self): 
        total = 0
        for i in range(self.v):
            if (i%3 == 0 or i%5 == 0):
                total = total+i
        print (total)      

        return total

v = multImp(100)
v.mult()