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
    pass

class BinaryOperator(AbstractSyntaxTree):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        
    def __repr__(self):
        return f"BinaryOperator(\noperator: {self.operator},\nleft: {self.left},\nright: {self.right}\n)"

class Number(AbstractSyntaxTree):
    def __init__(self, token):
        self.token = token
    
    def __repr__(self):
        return f"Number({self.token})"