# from types import *

PLUS, MINUS, MULTIPLY, DIVIDE, NUM, PAROPEN, PARCLOSE, ASSIGN, VAR, EOF = "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "NUM", "PAROPEN", "PARCLOSE", "ASSIGN", "VAR", "EOF"
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
#      self.keywords = {""}

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

    while self.char != None and self.char.isalpha():
      final += self.char
      self.increment()
    
    self.decrement()
#    token = self.keywords[final] if final in self.keywords.keys() else Token(VAR, final)
    token = Token(VAR, final)
    return token

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
      if self.char.isspace() or self.char == "\n":
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
      
      else:
        x = self.char.replace('\n', '\\n').replace('\t', '\\t')
        print(f"\x1b[31munrecognized character '{x}'\x1b[0m")
        return []
      
      self.increment()
    
    print('returning', tokens)
    return tokens
