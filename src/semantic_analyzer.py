from lexer import *
from syntax_tree import *

class SemanticAnalyzer():
    def __init__(self, interpreter):
        self.scopes = []
        self.interpreter = interpreter

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: str):
        """
        Indicate that a name has begun the binding process,
        but is not yet finished.
        """
        if not len(self.scopes): return
        scope = self.scopes[-1]
        scope[name] = False

    def define(self, name: str):
        """
        Indicate that a name has finished the binding process.
        The name can now be used elsewhere in the program.
        """
        if not len(self.scopes): return
        scope = self.scopes[-1]
        scope[name] = True

    def resolve_local(self, expr: AbstractSyntaxTree, name: Token):
        for scope in reversed(self.scopes):
            if name in scope.keys():
                distance = len(self.scopes) - 1 - self.scopes.index(scope)
                self.interpreter.resolve(expr, distance)

    def resolve_block(self, block):
        for statement in block.children:
            self.resolve(statement)

    def resolve(self, node):
        if type(node) == CodeBlock:
            self.begin_scope()
            self.resolve_block(node)
            self.end_scope()

        elif type(node) in (BinaryOperator, Logical):
            self.resolve(node.left)
            self.resolve(node.right)

        elif type(node) == UnaryOperator:
            self.resolve(node.child)

        elif type(node) == Declare:
            name = node.name.value
            self.declare(name)
            self.resolve(node.value)
            self.define(name)

        elif type(node) == Variable:
            scope: dict = self.scopes[-1]
            is_defined = scope.get(node.token.value)

            if len(self.scopes) and is_defined == False:
                raise Exception(f"'{node.token.value}' cannot be read in its own declaration.")
            self.resolve_local(node, node.token.value)

        elif type(node) == Assign:
            self.resolve(node.value)
            self.resolve_local(node, node.name)

        elif type(node) == DeclareFunc:
            self.declare(node.name.value)
            self.define(node.name.value)

            self.begin_scope()
            for arg in node.args:
                self.declare(arg.name)
                self.define(arg.name)
            self.resolve_block(node.statements)
            self.resolve_local(node, node.name.value)
            self.end_scope()

        elif type(node) in (BinaryOperator, Logical):
            self.resolve(node.left)
            self.resolve(node.right)

        elif type(node) == UnaryOperator:
            self.resolve(node.child)

        elif type(node) == IfStatement:
            self.resolve(node.condition)
            self.resolve(node.block)
            if node.else_block:
                self.resolve(node.else_block)

        elif type(node) == Print:
            self.resolve(node.expression)

        elif type(node) == Return:
            self.resolve(node.statement)

        elif type(node) == WhileStatement:
            self.resolve(node.condition)
            self.resolve(node.block)

        elif type(node) == FunctionCall:
            self.resolve(node.name)
            for arg in node.args:
                self.resolve(arg)
