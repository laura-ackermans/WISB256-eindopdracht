import math

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # surround any splitchar by spaces, take into account what to do when a negative value is entered. 
    tokenstring = []
    for c in range(0,len(string)):
        if string[c] == '-' and c == 0:
            tokenstring.append(" ( ")
            tokenstring.append("-1")
            tokenstring.append(" * ")
        elif string[c] == '-' and string[c-1] in splitchars:
            tokenstring.append(" ( -1 * ")
        elif string[c] in splitchars:
            tokenstring.append(' %s ' % string[c])
        elif string[c-1] == '-' and (c == 1 or string[c-2] in splitchars):
            tokenstring.append(string[c])
            tokenstring.append(' ) ')
        else:
            tokenstring.append(string[c])
    tokenstring = ''.join(tokenstring)
    print(tokenstring)
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split()
    
    #special casing for **:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans
    
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# check if a string represents an integer value        
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

class Expression():
    """A mathematical expression, represented as an expression tree"""
    # koppel de "+ functie" aan optelling 
    def __add__(self, other):
        return AddNode(self, other)
    
    # koppel de "- functie" aan aftrekking   
    def __sub__(self,other): 
        return SubNode(self, other)
        
    # koppel de "* functie" aan vermenigvuldiging   
    def __mul__(self,other): 
        return MulNode(self, other)

    # koppel de "/ functie" aan deeling   
    def __truediv__(self,other): 
        return DivNode(self, other)

    # koppel de "** functie" aan machtsverheffing  
    def __pow__(self,other): 
        return PowNode(self, other)
        
    # basic Shunting-yard algorithm
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and '+'s
        output = []
        
        # list of operators
        oplist1 = ['**']
        oplist2 = ['*', '/']
        oplist3 = ['+', '-']
        oplist = oplist1 + oplist2 + oplist3
        brackets = ['(', ')']
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
            elif token not in oplist + brackets: 
                output.append(Variable(token))
            elif token in oplist3:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    # TODO: when there are more operators, the rules are more complicated
                    # look up the shunting yard-algorithm
                    if len(stack) == 0 or stack[-1] not in oplist:
                        break
                    output.append(stack.pop())
                # push the new operator onto the stack
                stack.append(token)
            elif token in oplist2:
                while True:
                    if len(stack) == 0 or stack[-1] not in oplist1+oplist2:
                        break
                    output.append(stack.pop())
                stack.append(token)
            elif token in oplist1:
                while True:
                    if len(stack) == 0 or stack[-1] not in oplist1:
                        break
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                # left parantheses go to the stack
                stack.append(token)
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
            # TODO: do we need more kinds of tokens?
            else:
                # unknown token
                raise ValueError('Unknown token: %s' % token)
            
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())

        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]

class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
        
    def evaluate(self,dictionary): 
        return self.value
        
class Variable(Expression): 
    """Represents a variable"""
    def __init__(self, variable):
        self.variable = variable
        
    def __eq__(self,other): 
        if isinstance(other, Variable):
            return self.variable == other.variable
        else:
            return False
        
    def __str__(self):
        return str(self.variable)
    
    def evaluate(self, dictionary):
        value = dictionary[self.variable]
        return value
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        operation_map = {
            '+' : (1, False),
            '-' : (1, True),
            '*' : (2, False),
            '/' : (2, True),
            '**': (3, True)}
        rank, lassoc = operation_map[self.op_symbol]
        nodes = [AddNode, SubNode, DivNode, MulNode, PowNode]
        leaves = [Constant, Variable]
        if type(self.lhs) in leaves and type(self.rhs) in leaves:
            lstring = str(self.lhs)
            rstring = str(self.rhs)
            return "%s %s %s" % (lstring, self.op_symbol, rstring) 
        
        elif type(self.lhs) in nodes and type(self.rhs) in leaves:
            rank2, lassoc2 = operation_map[self.lhs.op_symbol]
            lstring = str(self.lhs)
            rstring = str(self.rhs)
            if rank2 < rank: #or ( rank2 == rank and self.op_symbol == '**' ): 
                return "(%s) %s %s" % (lstring, self.op_symbol, rstring)
            else: 
                return "%s %s %s" % (lstring, self.op_symbol, rstring)
        
        elif type(self.lhs) in leaves and type(self.rhs) in nodes:
            rank3, lassoc3 = operation_map[self.rhs.op_symbol]
            lstring = str(self.lhs)
            rstring = str(self.rhs)
            if rank3 > rank or ( rank3 == rank and not lassoc ): 
                return "%s %s %s" % (lstring, self.op_symbol, rstring)
            elif rank3 == rank and lassoc3 == True: 
                return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
            else: 
                return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
        
        elif type(self.lhs) in nodes and type(self.rhs) in nodes:
            rank2, lassoc2 = operation_map[self.lhs.op_symbol]
            rank3, lassoc3 = operation_map[self.rhs.op_symbol]
            lstring = str(self.lhs)
            rstring = str(self.rhs)
            if rank2 < rank: # or ( rank2 == rank and self.op_symbol == '**' ):
                if rank3 > rank or ( rank3 == rank and not lassoc ): 
                    return "(%s) %s %s" % (lstring, self.op_symbol, rstring)
                else: 
                    return "(%s) %s (%s)" % (lstring, self.op_symbol, rstring)
            else: 
                if rank3 > rank or ( rank3 == rank and not lassoc ): 
                    return "%s %s %s" % (lstring, self.op_symbol, rstring)
                else: 
                    return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
        else: 
            return "ERROR"
            
    def evaluate(self,dictionary = {}):
        leftTree = self.lhs.evaluate(dictionary)
        rightTree = self.rhs.evaluate(dictionary)
        return eval('%s %s %s' % (leftTree, self.op_symbol, rightTree))
        
# de klasse die de optelfunctie voor expression creeert        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

# de klasse die de aftrekfunctie voor expression creeert 
class SubNode(BinaryNode): 
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs): 
        super(SubNode, self).__init__(lhs, rhs, '-')
        
# de klasse die de vermenigvuldigingsfunctie voor expression creeert 
class MulNode(BinaryNode): 
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs): 
        super(MulNode, self).__init__(lhs, rhs, '*')
        
# de klasse die de deelfunctie voor expression creeert 
class DivNode(BinaryNode): 
    """Represents the division operator"""
    def __init__(self, lhs, rhs): 
        super(DivNode, self).__init__(lhs, rhs, '/')
        
# de klasse die de machtsfunctie voor expression creeert 
class PowNode(BinaryNode): 
    """Represents the power operator"""
    def __init__(self, lhs, rhs): 
        super(PowNode, self).__init__(lhs, rhs, '**')