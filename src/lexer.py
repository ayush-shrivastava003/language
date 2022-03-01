# from types import *

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
        print("\x1b[31munrecognized character:", self.char, "\x1b[0m")
        return []
      
      self.increment()

    return tokens