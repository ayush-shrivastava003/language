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
        return f"VariableSymbol(name: {self.name}, type: {self.type})"

class TypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f"TypeSymbol(name: {self.name})"

class FunctionSymbol(Symbol):
    def __init__(self, name, statements, args=None, return_statement=None):
        super().__init__(name)
        self.args = [] if args == None else args
        self.statements = statements
        self.return_statement = return_statement
    
    def __repr__(self):
        return f"FunctionSymbol(name: {self.name}, args: {self.args})"

class SymbolTable():
    def __init__(self):
        """
        symbol table for a specific scope (global, function scope, etc)
        """
        self.symbols = {}

    def add_symbol(self, symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        symbol = self.symbols.get(name)

        return symbol

    def __repr__(self):
        g = '\n'.join([f"{name}: {value}" for name, value in self.symbols.items()])
        return f"SYMBOLS:\n{g}\n"

class Scope():
    def __init__(self, name, level, parent=None):
        """
        single class to hold multiple symbol tables for a scope.
        made in order to have vars/functions have the same name and prevent confusion.
        """
        self.name = name
        self.level = level
        self.parent = parent # refers to the scope surrounding the current one (e.g a function's scope's parent would be the global scope)

        self.types = SymbolTable()
        self.vars = SymbolTable()
        self.functions = SymbolTable()

        self.data = {
            "types": self.types,
            "vars": self.vars,
            "functions": self.functions
        }
        self.data["types"].symbols = {"NUM": TypeSymbol(TokenType.NUM)}

    def __repr__(self):
        parent_name = self.parent.name if self.parent != None else "N/A"
        return f"""
        
        SCOPE {self.name}
        PARENT: {parent_name}

        CONTENT
        =======
        TYPES: {self.types.symbols}
        VARS: {self.vars.symbols}
        FUNCTIONS: {self.functions.symbols}

        """

    def lookup(self, name, category):
        symbol = self.data[category].lookup(name)
        if symbol != None:
            return symbol

        if self.parent != None:
            symbol = self.parent.lookup(name, category)
            return symbol
    
    def add_symbol(self, symbol, category):
        symbol.level = self.level
        self.data[category].add_symbol(symbol)

class SemanticAnalyzer():
    def __init__(self):
        self.scope = Scope('global', 0)
        self.global_scope = self.scope

    def traverse(self, node) -> None:
        if type(node) == Number:
            pass

        elif type(node) == CodeBlock:
            for statement in node.children:
                self.traverse(statement)

        elif type(node) == BinaryOperator:
            # not returning operations because we just want to verify types.
            # it's the interpreter's job to evaluate the operations.
            self.traverse(node.left)
            self.traverse(node.right)

        elif type(node) == UnaryOperator:
            self.traverse(node.child)

        elif type(node) == Declare:
            node_type = self.scope.lookup(node.type, "types")

            if node_type == None:
                raise Exception(f"unrecognized type {node.type}")

            self.traverse(node.value) # verify that we know everything about the value

            name = node.name.value

            if self.scope.lookup(name, "vars") != None:
                raise Exception("variable already declared:", name)

            var = VariableSymbol(name, node_type)
            self.scope.add_symbol(var, "vars")

        elif type(node) == Assign:
            self.traverse(node.name)
            self.traverse(node.value)

        elif type(node) == Variable:
            name = node.token.value
            symbol = self.scope.lookup(name, "vars")

            if symbol == None:
                raise Exception(f"unkown variable {name}", node.token)

        elif type(node) == DeclareFunc:
            function_name =  node.name
            if self.scope.lookup(function_name, "functions") == None:
                _symbol = FunctionSymbol(function_name, node.statements)
                
                self.scope.add_symbol(_symbol, "functions")
                new_scope = Scope(function_name, self.scope.level+1, self.global_scope)
                self.scope = new_scope

                for arg in node.args:
                    arg_symbol = VariableSymbol(arg.name, arg.type)
                    self.scope.add_symbol(arg_symbol, "vars")

                    _symbol.args.append(arg_symbol)

                self.traverse(node.statements)
                self.scope = self.scope.parent
            else:
                raise Exception("function already declared")

        elif type(node) == FunctionCall:
            symbol = self.scope.lookup(node.name, "functions")
            if symbol == None:
                raise Exception(f"unkown function '{node.name}'")
            
            elif len(node.args) != len(symbol.args):
                raise Exception(f"wanted {len(symbol.args)} argument(s), got {len(node.args)}")
            
            node.symbol = symbol
            [self.traverse(arg) for arg in node.args]

        elif type(node) == Return:
            self.traverse(node.statement)

        elif type(node) == Print:
            self.traverse(node.expression)

        elif type(node) == IfStatement:
            self.traverse(node.condition)
            new_scope = Scope("<if_statement>", self.scope.level+1, self.scope)
            self.scope = new_scope

            self.traverse(node.block)

            self.scope = self.scope.parent

            if node.else_block != None:
                new_scope = Scope("<else_statement>", self.scope.level+1, self.scope)
                self.scope = new_scope
                self.traverse(node.else_block)
                self.scope = self.scope.parent

        elif type(node) == WhileStatement:
            self.traverse(node.condition)
            new_scope = Scope("<while_loop>", self.scope.level+1, self.scope)
            self.scope = new_scope

            self.traverse(node.block)

            self.scope = self.scope.parent