PLUS, MINUS, MULTIPLY, DIVIDE, NUM, PAROPEN, PARCLOSE, ASSIGN, NAME, EOF, SEPR, TYPE, FUNCOPEN, FUNCCLOSE, COLON, COMMA = "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "NUM", "PAROPEN", "PARCLOSE", "ASSIGN", "NAME", "EOF", "SEPR", "TYPE", "FUNCOPEN", "FUNCCLOSE", "COLON", "COMMA"
ops = {"+": PLUS, "-": MINUS, "*": MULTIPLY, "/": DIVIDE}

class Token():
  def __init__(self, type, value, line=1, column=1):
    self.type = type
    self.value = value
    self.line = line
    self.column = column

  def __str__(self):
    # with open()
    return f"Token({self.type}, {self.value} @ {self.line}:{self.column})"

  def __repr__(self):
    return self.__str__()

class Lexer():
  def __init__(self) -> None:
      self.content = " "
      self.index = -1
      self.char = self.content[self.index]
      self.keywords = {
        "num": (TYPE, NUM),
        "fn": (FUNCOPEN, "fn"),
        "end": (FUNCCLOSE, "end"),
        # "return": (RETURN, "return")
      }

  def increment(self) -> None:
    self.index += 1

    if self.index < len(self.content):
      self.char = self.content[self.index]
    else:
      self.char = None

  def decrement(self) -> None:
    self.index -= 1
    self.char = self.content[self.index]

  def line_and_column(self): # the gods at stack overflow have saved me again
    sub_str = self.content[:self.index+1]
    sub_str = sub_str.splitlines(keepends=True)
    return len(sub_str), len(sub_str[-1])

  def get_num(self) -> float or int:
    final = ""

    while (self.char != None and (self.char.isdigit() or self.char == ".")):
      final += self.char
      self.increment()
    
    self.decrement()

    if "." in final:
      if len(final.split(".")) > 2:
        print(f"\x1b[0minvalid float {final}")
        return
    
      return float(final)
    else:
      return int(final)

  def get_word(self, line, column) -> Token:
    final = ""

    while self.char != None and (self.char.isalnum() or self.char == "_"):
      final += self.char
      self.increment()
    
    self.decrement()

    # token = Token(self.keywords[final] if final in self.keywords.keys() else Token(NAME, final)
    if final in self.keywords.keys():
      token_data = self.keywords[final]
      return Token(token_data[0], token_data[1], line, column)
    else:
      return Token(NAME, final, line, column)

  def tokenize(self) -> list:
    tokens = []
    self.increment()
    while self.char != None:
      line, column = self.line_and_column()
      if self.char.isspace():
        pass

      elif self.char.isdigit():
        num = self.get_num()
        tokens.append(Token(NUM, num, line, column))

      elif self.char.isalpha():
        tokens.append(self.get_word(line, column))

      elif self.char == "=":
        tokens.append(Token(ASSIGN, "=", line, column))
        # return

      elif self.char in ("+", "-", "*", "/"):
        tokens.append(Token(ops[self.char], self.char, line, column))

      elif self.char == "(":
        tokens.append(Token(PAROPEN, "(", line, column))

      elif self.char == ")":
        tokens.append(Token(PARCLOSE, ")", line, column))

      elif self.char == ";":
        tokens.append(Token(SEPR, ";", line, column))

      elif self.char == "?":
        self.increment()
        while self.char != "?":
            self.increment()

        self.increment()

      elif self.char == ":":
        tokens.append(Token(COLON, ":", line, column))

      elif self.char == ",":
        tokens.append(Token(COMMA, ",", line, column))

      else:
        x = self.char.replace('\n', '\\n').replace('\t', '\\t')
        print(f"\x1b[31munrecognized character '{x}'\x1b[0m")
        return []
      
      # tokens[-1].line, tokens[-1].column = line, column
      self.increment()
    
    # line, column = tokens[-1].line, tokens[-1].column+1
    # tokens.append(Token(EOF, None, line, column))
    return tokens
