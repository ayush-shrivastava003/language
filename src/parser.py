# from types import *
from lexer import *
from syntax_tree import *

class Parser():
    def __init__(self):
        self.tokens = []
        self.lexer = Lexer()
        self.token_index = -1
        self.current_token = None

    def next_token(self):
        """
        move to the next token in the stream

        example:

        ```
        [Token(NUM, 1), Token(PLUS, PLUS), Token(NUM, 2)]
        ^^^^^^^^^^^^^ currently here in the token stream

        [Token(NUM, 1), Token(PLUS, PLUS), Token(NUM, 2)]
                        ^^^^^^^^^^^^^^^^^ moved here
        ```
        """
        self.token_index += 1

        if self.token_index < len(self.tokens): 
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = Token(None, None)

    def eat_token(self, expected_token):
        """
        verify that the current token is the token we actually want, and move to the next one if it is. if not, throw an error
        """
        if self.current_token.type == expected_token:
            self.next_token()
        else:
            raise Exception(f"expected {expected_token}, found {self.current_token.type}")

    def get_factor(self):
        """
        in this case, a factor is defined as a number or another expression wrapped in parenthesis.

        if it is the latter, self.parse within self.get_factor - this allows for several layers of expressions
        """
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


    def get_term(self):
        """
        simplifies an expression containing ONLY multiplication or division until it is reduced down to one value.
        ```
        2 * 4 * 5 * 3
        v
        8 * 5 * 3
        v
        40 * 3
        v
        120
        ```
        the value returned from this is substitued into the expression being evaluated in `parse()`

        if there are no multiplication or division operators (i.e it is just a number), then it skips over the while loop.
        """
        final = self.get_factor()

        while self.current_token.type in (MULTIPLY, DIVIDE):
            current_token = self.current_token

            if current_token.type == MULTIPLY:
                self.eat_token(MULTIPLY)
                # final *= self.get_factor()

            elif current_token.type == DIVIDE:
                self.eat_token(DIVIDE)
                # final /= self.get_factor()

            final = BinaryOperator(current_token, final, self.get_factor())

        if final == None:
            raise SyntaxError(f"Unexpected end of expression")
        return final

    def get_expression(self):
        """

        parses the token stream using the following method:

        factor: INTEGER | LPAREN expr RPAREN
        term: factor ((MULTIPLY | DIVIDE) factor)*
        expr: term ((PLUS | MINUS) term)*

        this makes order of operations possible while writing an expression regularly
        
        ```
        1 + 2 * 4 * 5 * 3
        ^ parse the left hand side of expression (after feeding this substring into get_term(), we know the value is just 1)
        1 + 120
            ^^^ parse the right hand side of the expression (since it contains multiplication or division, get_term() simplifies the expression into 120)
        121
        ^^^ finally, add the left and right hand side together
        ```

        this process is repeated until one value is reached.

        a more complicated example:

        ```
        3 * 7 * 9 + 2 * 4 * 5 * 3 + 6 * 7
        ^^^^^^^^^ feed this into get_term() to simplify into one value (returns 189)

        189 + 2 * 4 * 5 * 3 + 6 * 7
            ^^^^^^^^^^^^^ feed the next part into get_term() (returns 120).
            once evaluated, it is immediately added to the left-hand expression (since we know for a fact that it has already been simplified)
        
        309 + 6 * 7
            ^^^^^ feed the final part into get_term() (returns 42)
            again, immediately adds to the left-hand expression since it is already simplified
        
        351
        ```
        """
        final = self.get_term()

        while self.current_token.type in (PLUS, MINUS):
            current_token = self.current_token

            if current_token.type == PLUS:
                self.eat_token(PLUS)
            # final += self.get_term()

            elif current_token.type == MINUS:
                self.eat_token(MINUS)
            # final -= self.get_term()
        
            final = BinaryOperator(operator=current_token, left=final, right=self.get_term())

        return final

    def parse(self):
        try:
            tree = self.get_expression()
            # self.next_token()

            if self.current_token.type != None:
                raise SyntaxError(f"Expected end of expression, found '{self.current_token.value}' instead")
            
            return tree

        except Exception as e:
            print(f"\x1b[31m{e}\x1b[0m")

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