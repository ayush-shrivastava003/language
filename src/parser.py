from lexer import *
from syntax_tree import *
from error import *

class Parser():
    def __init__(self):
        self.tokens = []
        self.lexer = Lexer()
        self.token_index = -1
        self.current_token = None
        self.filename = None

    def next_token(self) -> None:
        self.token_index += 1

        if self.token_index < len(self.tokens): 
            self.current_token = self.tokens[self.token_index]
        else:
            last_token = self.tokens[-1]
            self.current_token = Token(TokenType.EOF, None, last_token.line, last_token.column + 2)


    def peek(self) -> Token:
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        else:
            return Token(TokenType.EOF, None)

    def eat_token(self, expected_token, error) -> None:
        if self.current_token.type == expected_token:
            self.next_token()
        else:
            raise Error(error, self.current_token)

    def primary(self) -> AbstractSyntaxTree:
        token = self.current_token
        if token.type in (TokenType.NUM, TokenType.STRING, TokenType.BOOL):
            self.eat_token(token.type, "")
            return Literal(token)

        elif token.type == TokenType.PAROPEN:
            self.eat_token(TokenType.PAROPEN, "")
            final = self.get_expression()
            self.eat_token(TokenType.PARCLOSE, "Expected \")\" for expression wrapped in parentheses.")
            return final
        
        elif token.type == TokenType.NAME:
            self.eat_token(TokenType.NAME, "")
            var = Variable(token)
            return var
    
    def call_function(self) -> FunctionCall:
        expr = self.primary()
        while self.current_token.type == TokenType.PAROPEN:
            self.eat_token(TokenType.PAROPEN, "")
            
            if self.current_token.type == TokenType.PARCLOSE:
                self.eat_token(TokenType.PARCLOSE, "")
                expr = FunctionCall(expr, [])

            else:
                args = [self.get_expression()] 

                while self.current_token.type == TokenType.COMMA:
                    self.eat_token(TokenType.COMMA, "")
                    args.append(self.get_expression())
                self.eat_token(TokenType.PARCLOSE, "Expected closing parenthesis to function call.")
                expr = FunctionCall(expr, args)

        return expr

    def unary(self):
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat_token(TokenType.PLUS, "")
            factor = self.primary()
            return UnaryOperator(operator=token, child=factor)

        elif token.type == TokenType.MINUS:
            self.eat_token(TokenType.MINUS, "")
            factor = self.primary()
            return UnaryOperator(operator=token, child=factor)

        elif token.type == TokenType.NOT:
            self.eat_token(TokenType.NOT, "")
            factor = self.primary()
            return UnaryOperator(token, factor)

        val = self.call_function()
        if val is None:
            raise Error(f"Unexpected end of expression.", self.current_token)
        return val

    def factor(self) -> BinaryOperator:
        final = self.unary()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            current_token = self.current_token
            self.eat_token(self.current_token.type, "")
            final = BinaryOperator(current_token.type, final, self.unary())

        # if final == None:
        #     raise Error(f"Unexpected end of expression.", self.current_token)
        return final

    def term(self) -> BinaryOperator:
        final = self.factor()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            current_token = self.current_token
            self.eat_token(self.current_token.type, "")  
            final = BinaryOperator(operator=current_token.type, left=final, right=self.factor())
        return final

    def comparison(self):
        final = self.term()
        while self.current_token.type in (TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
           token = self.current_token
           self.eat_token(self.current_token.type, "")
           final = BinaryOperator(token.type, final, self.term()) 

        return final

    def equality(self):
        final = self.comparison()
        while self.current_token.type in (TokenType.NOT_EQUAL, TokenType.EQUAL):
            token = self.current_token
            self.eat_token(self.current_token.type, "")
            final = BinaryOperator(token.type, final, self.comparison())

        return final

    def and_statement(self):
        final = self.equality()
        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat_token(TokenType.AND, "")
            final = Logical(final, token, self.equality())

        return final

    def or_statement(self):
        final = self.and_statement()

        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat_token(TokenType.OR, "")
            final = Logical(final, token, self.and_statement())
        
        return final

    def ternary(self): # desugared if statement: (condition) ? value_if_true : value_if_false
        condition = self.or_statement()
        if self.current_token.type == TokenType.TERNARY:
            self.eat_token(TokenType.TERNARY)

            true_block = self.or_statement()
            self.eat_token(TokenType.COLON, "Expected \":\" in a ternary expression.")
            false_block = self.or_statement()

            return IfStatement(condition, true_block, false_block)
        
        return condition

    def get_expression(self):
        return self.ternary()

    def declare_var(self) -> Declare:
        self.eat_token(TokenType.DECL, "Expected \"let\" present in variable declaration.")

        name = self.current_token
        self.eat_token(TokenType.NAME, "Expected a name when declaring a variable.")

        self.eat_token(TokenType.ASSIGN, "Expected \"=\" in a variable declaration.")
        value = self.get_expression()

        return Declare(name, value)

    def assign(self):
        name_node = Variable(self.current_token)
        self.eat_token(TokenType.NAME, "Expected a name in variable assignment.")

        if self.current_token.type == TokenType.INCREMENT:
            self.eat_token(TokenType.INCREMENT, "")
            left = name_node
            right = Token(TokenType.NUM, 1, self.current_token.line, self.current_token.column)
            right = Literal(right)
            expr = BinaryOperator(TokenType.PLUS, left, right)
            return Assign(name_node, expr)
        elif self.current_token.type == TokenType.DECREMENT:
            self.eat_token(TokenType.DECREMENT, "")
            left = name_node
            right = Token(TokenType.NUM, 1, self.current_token.line, self.current_token.column)
            right = Literal(right)
            expr = BinaryOperator(TokenType.MINUS, left, right)
            return Assign(name_node, expr)

        self.eat_token(TokenType.ASSIGN, "Expected \"=\" when assigning a variable.")
        value = self.get_expression()
        
        return Assign(name_node, value)

    def func_arg(self) -> Argument:
        arg_name = self.current_token.value
        self.eat_token(TokenType.NAME, "Expected a name for a function argument.")
        return Argument(arg_name)

    def get_func_args(self) -> list:
        if self.current_token.type == TokenType.PARCLOSE:
            return []

        args = [self.func_arg()]

        while self.current_token.type == TokenType.COMMA:
            self.eat_token(TokenType.COMMA, "")
            args.append(self.func_arg())

        return args

    def declare_func(self) -> DeclareFunc:
        func_name = Variable(self.current_token)
        self.eat_token(TokenType.NAME, "Expected a name when declaring a function.")
        self.eat_token(TokenType.PAROPEN, "Expected a set of parentheses after function name.")

        args = self.get_func_args()
        self.eat_token(TokenType.PARCLOSE, "Expected closing parenthesis after argument list.")
        self.eat_token(TokenType.COLON, "Expected colon after parentheses.")

        statements = self.code_block(TokenType.END)

        return DeclareFunc(func_name, args, statements)
    
    def if_statement(self):
        self.eat_token(TokenType.PAROPEN, "Expected a set of parenthesis for condition.")
        condition = self.get_expression()
        self.eat_token(TokenType.PARCLOSE, "Expected closing parenthesis for condition.")
        self.eat_token(TokenType.COLON, "Expected a colon after the condition.")
        block = self.code_block(TokenType.ENDIF)
        self.eat_token(TokenType.ENDIF, "Expected a \"fi\" keyword after if statement.")
        # self.eat_token(SEPR)
        
        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.eat_token(TokenType.ELSE, "")
            else_block = self.code_block(TokenType.ENDIF)
            self.eat_token(TokenType.ENDIF, "")

        return IfStatement(condition, block, else_block)     

    def while_statement(self):
        self.eat_token(TokenType.PAROPEN)
        condition = self.get_expression()
        self.eat_token(TokenType.PARCLOSE)
        self.eat_token(TokenType.COLON)

        block = self.code_block(TokenType.END)
        self.eat_token(TokenType.END)

        return WhileStatement(condition, block)

    def for_statement(self): # "desugars" a for loop and returns a WhileStatement instance (reads a for loop, returns a while loop)
        self.eat_token(TokenType.PAROPEN)

        intializer = None
        if self.current_token.type == TokenType.DECL:
            initializer = self.declare_var()
        else:
            initializer = self.get_expression()
        self.eat_token(TokenType.SEPR)
        condition = self.get_expression()
        
        self.eat_token(TokenType.SEPR)
        increment = self.assign()

        self.eat_token(TokenType.PARCLOSE)
        self.eat_token(TokenType.COLON)

        block = self.code_block(TokenType.END)
        self.eat_token(TokenType.END)

        block.children.append(increment) # put the incrementer at the back

        while_loop = WhileStatement(condition, block)
        return CodeBlock([initializer, while_loop])

    def code_block(self, end_keyword) -> CodeBlock: # end keyword could be TokenType.EOF, FUNCCLOSE, etc
        tree_nodes = []
        while self.current_token.type != end_keyword:
            if self.current_token.type == TokenType.DECL:
                tree_nodes.append(self.declare_var())

            elif self.current_token.type == TokenType.NAME:
                if self.peek().type in (TokenType.ASSIGN, TokenType.INCREMENT, TokenType.DECREMENT):
                    tree_nodes.append(self.assign())

                else:
                    tree_nodes.append(self.get_expression())

            elif self.current_token.type == TokenType.FUNCOPEN:
                self.eat_token(TokenType.FUNCOPEN, "")
                node = self.declare_func()
                self.eat_token(TokenType.END, "")
                tree_nodes.append(node)

            elif self.current_token.type == TokenType.RETURN:
                self.eat_token(TokenType.RETURN, "")
                tree_nodes.append(Return(self.get_expression()))

            elif self.current_token.type == TokenType.PRINT:
                self.eat_token(TokenType.PRINT, "")
                value = ""
                if self.current_token.type != TokenType.SEPR:
                    value = self.get_expression()

                tree_nodes.append(Print(value))

            elif self.current_token.type == TokenType.IF:
                self.eat_token(TokenType.IF, "")
                tree_nodes.append(self.if_statement())

            elif self.current_token.type == TokenType.WHILE:
                self.eat_token(TokenType.WHILE, "")
                tree_nodes.append(self.while_statement())

            elif self.current_token.type == TokenType.FOR:
                self.eat_token(TokenType.FOR, "")
                tree_nodes.append(self.for_statement())

            else:
                tree_nodes.append(self.get_expression())
            
            self.eat_token(TokenType.SEPR, "Expected statement separator (\";\").")

        block = CodeBlock(tree_nodes)
        return block

    def parse(self) -> AbstractSyntaxTree:
        tree = self.code_block(TokenType.EOF)
        self.eat_token(TokenType.EOF, "")
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