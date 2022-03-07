from lexer import *
from syntax_tree import *

class Parser():
    def __init__(self):
        self.tokens = []
        self.lexer = Lexer()
        self.token_index = -1
        self.current_token = None

    def next_token(self):
        self.token_index += 1

        if self.token_index < len(self.tokens): 
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = Token(EOF, None)

    def eat_token(self, expected_token):
        if self.current_token.type == expected_token:
            self.next_token()
        else:
            raise Exception(f"expected {expected_token}, found {self.current_token.type}")

    def get_factor(self):
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
        
        elif token.type == VAR:
            self.eat_token(VAR)
            var = Variable(token)
            return var


    def get_term(self):
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

    def get_expression(self):
        final = self.get_term()
        while self.current_token.type in (PLUS, MINUS):
            current_token = self.current_token

            if current_token.type == PLUS:
                self.eat_token(PLUS)

            elif current_token.type == MINUS:
                self.eat_token(MINUS)
        
            final = BinaryOperator(operator=current_token, left=final, right=self.get_term())

        return final

    def get_statements(self):
        """
        statements: ((declare | assignment | expr) SEPR)*
        declare: TYPE VAR ASSIGN VALUE
        assignment: VAR VALUE
        """
        tree_nodes = []

        while self.current_token.type != EOF:
            if self.current_token.type == TYPE: # explicit typing
                type = self.current_token.value
                self.eat_token(TYPE)

                name = self.current_token
                self.eat_token(VAR)

                self.eat_token(ASSIGN)
                value = self.get_expression()

                tree_nodes.append(Declare(name, value, type))

            elif self.current_token.type == VAR:
                name_node = Variable(self.current_token)
                self.eat_token(VAR)

                if self.current_token.type == ASSIGN:
                    self.eat_token(ASSIGN)
                    value = self.get_expression()
                    tree_nodes.append(Assign(name_node, value))

                else:
                    self.token_index -= 1
                    self.current_token = self.tokens[self.token_index]
                    tree_nodes.append(self.get_expression())

            else:
                tree_nodes.append(self.get_expression())

            self.eat_token(SEPR)

        program = Program([node for node in tree_nodes])
        return program

    def parse(self):
        tree = self.get_statements()
        self.eat_token(EOF)
        return tree

    def setup(self, content):
        self.tokens = []
        self.token_index = -1
        self.current_token = None
        self.lexer.content = content
        self.lexer.index = -1
        # self.lexer.char = content[self.lexer.index]
        self.tokens = self.lexer.tokenize()
        self.next_token()

        if self.tokens == []:
            return
