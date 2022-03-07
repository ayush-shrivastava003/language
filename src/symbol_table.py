"""
the semantic analyzer examines the syntax tree before the interpreter does. any unkown variables, bad typing, etc are checked here.
"""
from lexer import *
from syntax_tree import *

class Symbol():
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class VariableSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __repr__(self):
        return f"VariableSymbol(name: {self.name}, type: {self.type}"

class TypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f"TypeSymbol(name: {self.name})"

class SymbolTable():
    def __init__(self):
        self.symbols = {"NUM": TypeSymbol(NUM)}

    def add_symbol(self, symbol):
        self.symbols[symbol.name] = symbol
        print(self.symbols.keys())

    def lookup(self, symbol):
        print(self.symbols.keys())
        return self.symbols.get(symbol)

class SemanticAnalyzer():
    def __init__(self):
        self.table = SymbolTable()

    def traverse(self, node):
        if type(node) == Number:
            pass

        elif type(node) == BinaryOperator:
            # not returning operations because we just want to verify types.
            # it's the interpreter's job to evaluate the operations.
            self.traverse(node.left)
            self.traverse(node.right)

        elif type(node) == UnaryOperator:
            self.traverse(node.child)

        elif type(node) == Declare:
            node_type = self.table.lookup(node.type)

            if node_type == None:
                raise Exception(f"unrecognized type {node.type}")

            self.traverse(node.value) # verify that we know everything about the value

            name = node.name.value

            if self.table.lookup(name) != None:
                raise Exception("variable already declared:", name)

            var = VariableSymbol(name, node_type)
            self.table.add_symbol(var)

        elif type(node) == Assign:
            self.traverse(node.name)
            self.traverse(node.value)

        elif type(node) == Variable:
            name = node.token.value
            symbol = self.table.lookup(name)

            if symbol == None:
                raise Exception(f"unkown variable {name}")
