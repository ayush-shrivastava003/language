class AbstractSyntaxTree():
    r"""
    this file contains the abstract syntax tree for the main parser.

    a syntax tree is just a representation of the grammar rules defined by our program.
    in the context of a calculator, the syntax tree would show the order of operations
    that the parser follows.

    for example, 10 + 30 / 5 can be represented as:
    ```
         (+)
        /   \
    (10)     (/)
            /   \
        (30)     (5)

    ```
    it's a helpful way to visualize how the interpreter solves expressions.
    """

class Program(AbstractSyntaxTree):
    def __init__(self, children):
        self.children = children

class BinaryOperator(AbstractSyntaxTree):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        # print(self.__repr__())
        
    def __repr__(self):
        return f"BinaryOperator(\noperator: {self.operator},\nleft: {self.left},\nright: {self.right}\n)"

class UnaryOperator(AbstractSyntaxTree):
    def __init__(self, operator, child):
        self.operator = operator
        self.child = child # token that the unary operator is modifying
        # print(self.__repr__())

    def __repr__(self):
        return f"UnaryOperator(operator: {self.operator}, child: {self.child}\n)"

class Number(AbstractSyntaxTree):
    def __init__(self, token):
        self.token = token
        # print(self.__repr__)
    
    def __repr__(self):
        return f"Number({self.token})"

class Assign(AbstractSyntaxTree):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        # print(self.__repr__)

    def __repr__(self):
        return f"Assign(name: {self.name}, value: {self.value})"

class Variable(AbstractSyntaxTree):
    def __init__(self, token):
        self.token = token
        # self.token = value
        # print(self.__repr__())

    def __repr__(self):
        return f"Variable(name: {str(self.token)})"
