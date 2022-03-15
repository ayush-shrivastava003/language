from lexer import *
from syntax_tree import *

class Parser():
    def __init__(self):
        self.tokens = []
        self.lexer = Lexer()
        self.token_index = -1
        self.current_token = None

    def next_token(self) -> None:
        self.token_index += 1

        if self.token_index < len(self.tokens): 
            self.current_token = self.tokens[self.token_index]
        else:
            last_token = self.tokens[-1]
            self.current_token = Token(EOF, None, last_token.line, last_token.column + 2)


    def peek(self) -> Token:
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        else:
            return Token(EOF, None)

    def eat_token(self, expected_token) -> None:
        if self.current_token.type == expected_token:
            self.next_token()
        else:
            # raise Exception(f"expected {expected_token}, found {self.current_token.type}")
            print(f"\x1b[31mSyntax error at line {self.current_token.line}, column {self.current_token.column}\n")
            with open("test.language", "r") as f:
                lines = f.readlines()
                print(lines[self.current_token.line -1])
                print(f'{" " * (self.current_token.column - 1)}^')
                print(f"expected {expected_token}, found {self.current_token.type}\x1b[0m")
            quit()

    def primary(self) -> AbstractSyntaxTree:
        token = self.current_token
        if token.type == NUM:
            self.eat_token(NUM)
            return Number(token)

        elif token.type == PAROPEN:
            self.eat_token(PAROPEN)
            final = self.get_expression()
            self.eat_token(PARCLOSE)
            return final

        elif token.type == PLUS:
            self.eat_token(PLUS)
            factor = self.factor()
            return UnaryOperator(operator=token, child=factor)

        elif token.type == MINUS:
            self.eat_token(MINUS)
            factor = self.factor()
            return UnaryOperator(operator=token, child=factor)

        elif token.type == NOT:
            self.eat_token(NOT)
            factor = self.factor()
            return UnaryOperator(token, factor)
        
        elif token.type == NAME:
            if self.peek().type == PAROPEN:
                return self.call_function()
            
            self.eat_token(NAME)
            return Variable(token)


    def factor(self) -> BinaryOperator:
        final = self.primary()
        while self.current_token.type in (MULTIPLY, DIVIDE):
            current_token = self.current_token
            self.eat_token(self.current_token.type)
            final = BinaryOperator(current_token, final, self.primary())

        if final == None:
            raise SyntaxError(f"Unexpected end of expression")
        return final

    def term(self) -> BinaryOperator:
        final = self.factor()
        while self.current_token.type in (PLUS, MINUS):
            current_token = self.current_token
            self.eat_token(self.current_token.type)  
            final = BinaryOperator(operator=current_token, left=final, right=self.factor())

        return final

    def comparison(self):
        final = self.term()

        while self.current_token.type in (GREATER, LESS, GREATER_EQUAL, LESS_EQUAL):
           token = self.current_token
           self.eat_token(self.current_token.type)
           final = BinaryOperator(token, final, self.term()) 

        return final

    def equality(self):
        final = self.comparison()

        while self.current_token.type in (NOT_EQUAL, EQUAL):
            token = self.current_token
            self.eat_token(self.current_token.type)
            final = BinaryOperator(token, final, self.comparison())

        return final

    def and_statement(self):
        final = self.equality()

        while self.current_token.type == AND:
            token = self.current_token
            self.eat_token(AND)
            final = Logical(final, token, self.equality())

        return final

    def or_statement(self):
        final = self.and_statement()

        while self.current_token.type == OR:
            token = self.current_token
            self.eat_token(OR)
            final = Logical(final, token, self.and_statement())
        
        return final

    def get_expression(self):
        return self.or_statement()

    def declare_var(self) -> Declare:
        type = self.current_token.value
        self.eat_token(TYPE)

        name = self.current_token
        self.eat_token(NAME)

        self.eat_token(ASSIGN)
        value = self.get_expression()

        return Declare(name, value, type)

    def assign(self):
        name_node = Variable(self.current_token)
        self.eat_token(NAME)
        self.eat_token(ASSIGN)
        value = self.get_expression()
        
        return Assign(name_node, value)

    def func_arg(self) -> Argument:
        arg_name = self.current_token.value
        self.eat_token(NAME)
        self.eat_token(COLON)

        arg_type = self.current_token.value
        self.eat_token(TYPE)

        return Argument(arg_name, arg_type)

    def get_func_args(self) -> list:
        if self.current_token.type == PARCLOSE:
            return []

        args = [self.func_arg()]

        while self.current_token.type == COMMA:
            self.eat_token(COMMA)
            args.append(self.func_arg())

        return args

    def declare_func(self) -> DeclareFunc:
        func_name = self.current_token.value
        self.eat_token(NAME)
        self.eat_token(PAROPEN)

        args = self.get_func_args()
        self.eat_token(PARCLOSE)
        self.eat_token(COLON)

        statements = self.code_block(END)

        return DeclareFunc(func_name, args, statements)

    def call_function(self) -> FunctionCall:
        name = self.current_token.value
        self.eat_token(NAME)
        self.eat_token(PAROPEN)
        
        if self.current_token.type == PARCLOSE:
            self.eat_token(PARCLOSE)
            return FunctionCall(name, [])

        args = [self.get_expression()]

        while self.current_token == COMMA:
            self.eat_token(COMMA)
            args.append(self.get_expression())
        self.eat_token(PARCLOSE)

        return FunctionCall(name, args)
    
    def if_statement(self):
        self.eat_token(PAROPEN)
        condition = self.get_expression()
        self.eat_token(PARCLOSE)
        self.eat_token(COLON)
        block = self.code_block(ENDIF)
        self.eat_token(ENDIF)
        # self.eat_token(SEPR)
        
        else_block = None
        if self.current_token.type == ELSE:
            self.eat_token(ELSE)
            else_block = self.code_block(ENDIF)
            self.eat_token(ENDIF)

        return IfStatement(condition, block, else_block)     

    def while_statement(self):
        self.eat_token(PAROPEN)
        condition = self.get_expression()
        self.eat_token(PARCLOSE)
        self.eat_token(COLON)

        block = self.code_block(END)
        self.eat_token(END)

        return WhileStatement(condition, block)

    def for_statement(self): # "deugars" a for loop and returns a WhileStatement instance (reads a for loop, returns a while loop)
        self.eat_token(PAROPEN)

        intializer = None
        if self.current_token.type == TYPE:
            initializer = self.declare_var()
        else:
            initializer = self.get_expression()
        
        self.eat_token(SEPR)
        condition = self.get_expression()
        
        self.eat_token(SEPR)
        increment = self.assign()

        self.eat_token(PARCLOSE)
        self.eat_token(COLON)

        block = self.code_block(END)
        self.eat_token(END)

        block.children.append(increment) # put the incrementer at the back

        while_loop = WhileStatement(condition, block)
        return CodeBlock([initializer, while_loop])

    def code_block(self, end_keyword) -> CodeBlock: # end keyword could be EOF, FUNCCLOSE, etc
        tree_nodes = []
        while self.current_token.type != end_keyword:
            if self.current_token.type == TYPE:
                tree_nodes.append(self.declare_var())

            elif self.current_token.type == NAME:
                if self.peek().type == ASSIGN:
                    tree_nodes.append(self.assign())

                elif self.peek().type == PAROPEN: # function call
                        tree_nodes.append(self.call_function())

                else:
                    tree_nodes.append(self.get_expression())

            elif self.current_token.type == FUNCOPEN:
                self.eat_token(FUNCOPEN)
                node = self.declare_func()
                self.eat_token(END)
                tree_nodes.append(node)

            elif self.current_token.type == RETURN:
                self.eat_token(RETURN)
                tree_nodes.append(Return(self.get_expression()))

            elif self.current_token.type == PRINT:
                self.eat_token(PRINT)
                value = ""
                if self.current_token.type != SEPR:
                    value = self.get_expression()

                tree_nodes.append(Print(value))

            elif self.current_token.type == IF:
                self.eat_token(IF)
                tree_nodes.append(self.if_statement())

            elif self.current_token.type == WHILE:
                self.eat_token(WHILE)
                tree_nodes.append(self.while_statement())

            elif self.current_token.type == FOR:
                self.eat_token(FOR)
                tree_nodes.append(self.for_statement())

            else:
                tree_nodes.append(self.get_expression())

            self.eat_token(SEPR)

        block = CodeBlock(tree_nodes)
        return block

    def parse(self) -> AbstractSyntaxTree:
        tree = self.code_block(EOF)
        self.eat_token(EOF)
        return tree

    def setup(self, content) -> None:
        self.tokens = []
        self.token_index = -1
        self.current_token = None
        self.lexer.content = content
        self.lexer.index = -1
        self.tokens = self.lexer.tokenize()

        if self.tokens == []:
            return False

        self.next_token()
        return True