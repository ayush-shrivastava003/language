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
            self.current_token = Token(EOF, None)

        # print(self.current_token)

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

    def get_factor(self) -> AbstractSyntaxTree:
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
            factor = self.get_factor()
            return UnaryOperator(operator=token, child=factor)

        elif token.type == MINUS:
            self.eat_token(MINUS)
            factor = self.get_factor()
            return UnaryOperator(operator=token, child=factor)
        
        elif token.type == NAME:
            if self.peek().type == PAROPEN:
                return self.call_function()
            
            self.eat_token(NAME)
            return Variable(token)


    def get_term(self) -> BinaryOperator:
        final = self.get_factor()
        while self.current_token.type in (MULTIPLY, DIVIDE):
            current_token = self.current_token

            if current_token.type == MULTIPLY:
                self.eat_token(MULTIPLY)

            elif current_token.type == DIVIDE:
                self.eat_token(DIVIDE)

            final = BinaryOperator(current_token, final, self.get_factor())

        if final == None:
            raise SyntaxError(f"Unexpected end of expression")
        return final

    def get_expression(self) -> BinaryOperator:
        final = self.get_term()
        while self.current_token.type in (PLUS, MINUS):
            current_token = self.current_token

            if current_token.type == PLUS:
                self.eat_token(PLUS)

            elif current_token.type == MINUS:
                self.eat_token(MINUS)
        
            final = BinaryOperator(operator=current_token, left=final, right=self.get_term())

        return final

    def declare_var(self) -> Declare:
        type = self.current_token.value
        self.eat_token(TYPE)

        name = self.current_token
        self.eat_token(NAME)

        self.eat_token(ASSIGN)
        value = self.get_expression()

        return Declare(name, value, type)

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

        statements = self.get_statements(FUNCCLOSE).children

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

    def get_statements(self, end_keyword) -> CodeBlock: # end keyword could be EOF, FUNCCLOSE, etc
        tree_nodes = []
        while self.current_token.type != end_keyword:
            # print(self.c)
            if self.current_token.type == TYPE:
                tree_nodes.append(self.declare_var())

            elif self.current_token.type == NAME:
                if self.peek().type == ASSIGN:
                    name_node = Variable(self.current_token)
                    self.eat_token(NAME)
                    self.eat_token(ASSIGN)
                    value = self.get_expression()
                    tree_nodes.append(Assign(name_node, value))

                elif self.peek().type == PAROPEN: # function call
                        tree_nodes.append(self.call_function())

                else:
                    tree_nodes.append(self.get_expression())

            elif self.current_token.type == FUNCOPEN:
                self.eat_token(FUNCOPEN)
                node = self.declare_func()
                self.eat_token(FUNCCLOSE)
                tree_nodes.append(node)

            elif self.current_token.type == RETURN:
                self.eat_token(RETURN)
                tree_nodes.append(Return(self.get_expression()))

            else:
                tree_nodes.append(self.get_expression())

            self.eat_token(SEPR)

        block = CodeBlock([node for node in tree_nodes])
        return block

    def parse(self) -> AbstractSyntaxTree:
        tree = self.get_statements(EOF)
        self.eat_token(EOF)
        return tree

    def setup(self, content) -> None:
        self.tokens = []
        self.token_index = -1
        self.current_token = None
        self.lexer.content = content
        self.lexer.index = -1
        self.tokens = self.lexer.tokenize()
        self.next_token()