from lexer import *
from syntax_tree import *
from error import *
import traceback

class SemanticAnalyzer():
    def __init__(self, interpreter):
        self.scopes = [{}]
        self.interpreter = interpreter
        self.function_state = False
        self.class_state = False

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

    def resolve_function(self, node, type):
        old = self.function_state
        self.function_state = True
        self.declare(node.name.token.value)
        self.define(node.name.token.value)

        self.begin_scope()
        for arg in node.args:
            self.declare(arg.name)
            self.define(arg.name)
        self.resolve_block(node.statements)
        self.resolve_local(node.name, node.name.token.value)
        self.end_scope()
        self.function_state = old

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
                raise Error(f"'{node.token.value}' cannot be read in its own declaration.", node.token)
            self.resolve_local(node, node.token.value)

        elif type(node) == Assign:
            self.resolve(node.value)
            self.resolve_local(node, node.name)

        elif type(node) == DeclareFunc:
            self.resolve_function(node, "function")

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
            if not self.function_state:
                raise Error("Cannot use return statement outside of a function.", node.token)

            self.resolve(node.statement)

        elif type(node) == WhileStatement:
            self.resolve(node.condition)
            self.resolve(node.block)

        elif type(node) == FunctionCall:
            self.resolve(node.name)
            for arg in node.args:
                self.resolve(arg)

        elif type(node) == ClassDecl:
            old = self.class_state
            self.class_state = True
            self.define(node.name)
            self.begin_scope()
            self.scopes[-1]["self"] = True
            for method in node.methods:
                self.resolve_function(method, "method")
            self.end_scope()
            self.class_state = old

        elif type(node) == GetProp:
            self.resolve(node.object)

        elif type(node) == SetProp:
            self.resolve(node.object)
            self.resolve(node.value)

        elif type(node) == Self:
            if not self.class_state:
                raise Error("Cannot use 'self' keyword outside of a class.", node.keyword)
            self.resolve_local(node, node.keyword.value)

        elif type(node) == BuiltinList:
            for item in node.items:
                self.resolve(item)