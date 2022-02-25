from sys import argv
# import sys
from traceback import print_exc
# import os

_version = "0.1"
PLUS, MINUS, MULTIPLY, DIVIDE, NUM, PAROPEN, PARCLOSE = "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "NUM", "PAROPEN", "PARCLOSE"
ops = {"+": PLUS, "-": MINUS, "*": MULTIPLY, "/": DIVIDE}

class Token():
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __str__(self):
    return f"Token({self.type}, {self.value})"

  def __repr__(self):
    return self.__str__()

class Lexer():
  def __init__(self) -> None:
      self.content = " "
      self.index = -1
      self.char = self.content[self.index]

  def increment(self):
    self.index += 1

    if self.index < len(self.content):
      self.char = self.content[self.index]
    else:
      self.char = None

  def get_num(self):
    final = ""

    while (self.char != None and (self.char.isdigit() or self.char == ".")):
      final += self.char
      self.increment()

    self.index -= 1
    self.char = self.content[self.index]

    if "." in final:
      if len(final.split(".")) > 2:
        print(f"\x1b[0minvalid float {final}")
        return
    
      return float(final)
    else:
      return int(final)


  def tokenize(self):
    """
    converts the content into a stream of tokens readable to the parser
    and interpreter

    example:

    "1 + 2" -> (Token(NUM, 1), Token(PLUS, PLUS), Token(NUM, 2))
    """
    tokens = []
    self.increment()
    while self.char != None:
      if self.char == None:
        break

      if self.char.isspace():
        self.increment()

      if self.char.isdigit():
        num = self.get_num()
        if num != None: 
          tokens.append(Token(NUM, num))
        else: 
          break

      elif self.char in ("+", "-", "*", "/"):
        tokens.append(Token(ops[self.char], self.char))

      elif self.char == "(":
        tokens.append(Token(PAROPEN, "("))

      elif self.char == ")":
        tokens.append(Token(PARCLOSE, ")"))
      
      else:
        print("\x1b[31munrecognized character:", self.char)
        return []
      
      self.increment()

    return tokens


class Interpreter():
  def __init__(self):
    self.tokens = []
    self.lexer = Lexer()
    self.token_index = -1
    self.current_token = None

  def stringify(self):
    return [str(token) for token in self.tokens]

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
      return None

  def eat_token(self, expected_token):
    """
    verify that the current token is the token we actually want, and move to the next one if it is. if not, throw an error
    """
    if self.current_token.type == expected_token:
      self.next_token()
    else:
      raise TypeError(f"expected {expected_token}, found {self.current_token.type}")

  def get_factor(self):
    """
    in this case, a factor is defined as a number or another expression wrapped in parenthesis.

    if it is the latter, self.parse within self.get_factor - this allows for several layers of expressions
    """
    token = self.current_token

    if token.type == NUM:
      self.eat_token(NUM)
      return token.value

    elif token.type == PAROPEN:
      self.eat_token(PAROPEN)
      final = self.parse()
      self.eat_token(PARCLOSE)
      return final


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
      if self.current_token.type == MULTIPLY:
        self.eat_token(MULTIPLY)
        final *= self.get_factor()

      elif self.current_token.type == DIVIDE:
        self.eat_token(DIVIDE)
        final /= self.get_factor()

    return final
  
  def parse(self):
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
    try:
      final = self.get_term()

      while self.current_token.type in (PLUS, MINUS):
        token_type = self.current_token.type

        if token_type == PLUS:
          self.eat_token(PLUS)
          final += self.get_term()

        elif token_type == MINUS:
          self.eat_token(MINUS)
          final -= self.get_term()
      
      return final
  
    except:
      print("\x1b[31m")
      print_exc()
      print("\x1b[0m")
      

  def run(self, content):
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

    print(self.parse())

  def run_shell(self):
    print(f"\x1b[32mShell version {_version}")
    print("Supported operators: +, -, *, /, ()")
    print("Type \"exit\" or hit ^C to exit.")
    while True:
      try:
        content = input(">\x1b[0m ")
        if content == "exit":
          raise KeyboardInterrupt()

        if content.isspace() or content == "":
          continue
        self.run(content)

      except KeyboardInterrupt:
        print("\nbye")
        exit(0)

i = Interpreter()
# content = 
# print(f"expecting {eval('(14.65 + 2) * 4 + 290*(4 + 6 * (8 + (10*8)))')}")
# i.run("(14.65 + 2) * 4 + 290*(4 + 6 * (8+ (10*8)))")
i.run_shell()

if len(argv) >= 2:
  with open(argv[1]) as f:
    i.run(f.read())

elif len(argv) == 1:
    i.run_shell()