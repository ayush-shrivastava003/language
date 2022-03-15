from unicodedata import name


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

class CodeBlock(AbstractSyntaxTree):
    def __init__(self, children):
        self.children = children
    
    def __repr__(self):
        return f"CODE BLOCK: {self.children}"

class BinaryOperator(AbstractSyntaxTree):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        # print(self.__repr__())
        
    def __repr__(self):
        return f"{self.left} {self.operator.value} {self.right}"

class UnaryOperator(AbstractSyntaxTree):
    def __init__(self, operator, child):
        self.operator = operator
        self.child = child # token that the unary operator is modifying
        # print(self.__repr__())

    def __repr__(self):
        return f"{self.operator}{self.child}"

class Number(AbstractSyntaxTree):
    def __init__(self, token):
        self.token = token
        # print(self.__repr__)
    
    def __repr__(self):
        return f"{self.token.value}"

class Assign(AbstractSyntaxTree):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name} = {self.value}"

class Variable(AbstractSyntaxTree):
    def __init__(self, token):
        self.token = token
        # self.token = value
        # print(self.__repr__())

    def __repr__(self):
        return f"{self.token.value}"

class Declare(AbstractSyntaxTree):
    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type
    
    def __repr__(self):
        return f"'{self.type} {self.name.value} = {self.value}'"

class Argument(AbstractSyntaxTree):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"{self.name}: {self.type}"

class DeclareFunc(AbstractSyntaxTree):
    def __init__(self, name, args, statements):
        self.name = name
        self.args = args
        self.statements = statements
        # self.symbol = symbol
    
    def __repr__(self):
        return f"fn {self.name}({', '.join(self.args)})"

class FunctionCall(AbstractSyntaxTree):
    def __init__(self, name, args, symbol=None):
        self.name = name
        self.args = args
        self.symbol = symbol
    
    def __repr__(self) -> str:
        return f"{self.name}({', '.join(self.args)})"

class Return(AbstractSyntaxTree):
    def __init__(self, statement):
        self.statement = statement

class Print(AbstractSyntaxTree):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self) -> str:
        return f"print {self.expression}"

class IfStatement(AbstractSyntaxTree):
    def __init__(self, condition, block, else_block=None):
        self.condition = condition
        self.block = block
        self.else_block = else_block

    def __repr__(self):
        return f"if ({self.condition}) | else {bool(self.else_block)}"

class Logical(AbstractSyntaxTree):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.left} OR {self.right}"