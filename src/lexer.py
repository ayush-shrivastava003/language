# from types import *

PLUS, MINUS, MULTIPLY, DIVIDE, NUM, PAROPEN, PARCLOSE, ASSIGN, VAR, EOF, SEPR, TYPE = "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "NUM", "PAROPEN", "PARCLOSE", "ASSIGN", "VAR", "EOF", "SEPR", "TYPE"
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
      self.types = {"num": Token(TYPE, NUM)}

  def increment(self):
    self.index += 1

    if self.index < len(self.content):
      self.char = self.content[self.index]
    else:
      self.char = None

  def decrement(self):
    self.index -= 1
    self.char = self.content[self.index]

  def get_num(self):
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

  def get_word(self):
    final = ""

    while self.char != None and (self.char.isalpha() or self.char == "_"):
      final += self.char
      self.increment()
    
    self.decrement()
    token = self.types[final] if final in self.types.keys() else Token(VAR, final)
    return token

  def tokenize(self):
    tokens = []
    self.increment()
    while self.char != None:
      if self.char.isspace():
        pass

      elif self.char.isdigit():
        num = self.get_num()
        if num != None: 
          tokens.append(Token(NUM, num))
        else: 
          break

      elif self.char.isalpha():
        tokens.append(self.get_word())

      elif self.char == "=":
        tokens.append(Token(ASSIGN, "="))

      elif self.char in ("+", "-", "*", "/"):
        tokens.append(Token(ops[self.char], self.char))

      elif self.char == "(":
        tokens.append(Token(PAROPEN, "("))

      elif self.char == ")":
        tokens.append(Token(PARCLOSE, ")"))

      elif self.char == ";":
        tokens.append(Token(SEPR, ";"))

      elif self.char == "?":
        self.increment()
        while self.char != "?":
            self.increment()

        self.increment()

      else:
        x = self.char.replace('\n', '\\n').replace('\t', '\\t')
        print(f"\x1b[31munrecognized character '{x}'\x1b[0m")
        return []
      
      self.increment()
    
    return tokens
