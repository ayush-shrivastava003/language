from enum import Enum
# from error import Error

class TokenType(Enum):
  PLUS = "PLUS"
  MINUS = "MINUS"
  MULTIPLY = "MULTIPLY"
  DIVIDE = "DIVIDE"
  NUM = "NUM"
  STRING = "STRING"
  BOOL = "BOOL"
  PAROPEN = "PAROPEN"
  PARCLOSE = "PARCLOSE"
  ASSIGN = "ASSIGN"
  NAME = "NAME"
  EOF = "EOF"
  SEPR = "SEPR"
  TYPE = "TYPE"
  FUNCOPEN = "FUNCTOPEN"
  END = "END"
  COLON = "COLON"
  COMMA = "COMMA"
  RETURN = "RETURN"
  PRINT = "PRINT"
  IF = "IF"
  ENDIF = "ENDIF"
  ELSE = "ELSE"
  GREATER = "GREATER"
  LESS = "LESS"
  EQUAL = "EQUAL"
  NOT = "NOT"
  GREATER_EQUAL = "GREATER_EQUAL"
  LESS_EQUAL = "LESS_EQUAL"
  OR = "OR"
  AND = "AND"
  NOT_EQUAL = "NOT_EQUAL"
  WHILE = "WHILE"
  FOR = "FOR"
  DECL = "DECL"
  TERNARY = "TERNARY"
  INCREMENT = "INCEMENT"
  DECREMENT = "DECREMENT"
  CLASS_DECL = "CLASS_DECL"
  DOT = "."
  SELF = "self"
  LIST_OPEN = "LIST_OPEN"
  LIST_CLOSE = "LIST_CLOSE"

ops = {"+": TokenType.PLUS, "-": TokenType.MINUS, "*": TokenType.MULTIPLY, "/": TokenType.DIVIDE}

class Token():
  def __init__(self, type, value, line=1, column=1):
    self.type = type
    self.value = value
    self.line = line
    self.column = column

  def __str__(self):
    return f"Token({self.type}, {self.value} @ {self.line}:{self.column})"

  def __repr__(self):
    return self.__str__()

class Lexer():
  def __init__(self) -> None:
      self.content = " "
      self.index = -1
      self.char = self.content[self.index]
      self.keywords = {
        "num": (TokenType.TYPE, TokenType.NUM),
        "fn": (TokenType.FUNCOPEN, "fn"),
        "end": (TokenType.END, "end"),
        "return": (TokenType.RETURN, "return"),
        "print": (TokenType.PRINT, "print"),
        "if": (TokenType.IF, "if"),
        "fi": (TokenType.ENDIF, "fi"),
        "else": (TokenType.ELSE, "else"),
        "or": (TokenType.OR, "or"),
        "and": (TokenType.AND, "and"),
        "while": (TokenType.WHILE, "while"),
        "for": (TokenType.FOR, "for"),
        "let": (TokenType.DECL, "let"),
        "true": (TokenType.BOOL, True),
        "false": (TokenType.BOOL, False),
        "class": (TokenType.CLASS_DECL, "class"),
        "self": (TokenType.SELF, "self")
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

  def peek(self):
    if self.index + 1 > len(self.content) - 1:
      return None
    return self.content[self.index + 1]

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

  def get_word(self) -> Token:
    final = ""

    while self.char != None and (self.char.isalnum() or self.char == "_"):
      final += self.char
      self.increment()
    
    self.decrement()

    # token = Token(self.keywords[final] if final in self.keywords.keys() else Token(NAME, final)
    line, column = self.line_and_column()
    if final in self.keywords.keys():
      token_data = self.keywords[final]
      return Token(token_data[0], token_data[1], line, column)
    else:
      return Token(TokenType.NAME, final, line, column)

  def tokenize(self) -> list:
    tokens = []
    self.increment()
    while self.char != None:
      line, column = self.line_and_column()
      if self.char.isspace():
        pass

      elif self.char.isdigit():
        num = self.get_num()
        tokens.append(Token(TokenType.NUM, num, line, column))

      elif self.char.isalpha():
        tokens.append(self.get_word())

      elif self.char == "=":
        if self.peek() == "=":
          tokens.append(Token(TokenType.EQUAL, "==", line, column))
          self.increment()
          self.increment()
          continue
        tokens.append(Token(TokenType.ASSIGN, "=", line, column))
        # return

      elif self.char in ("+", "-", "*", "/"):
        if self.char == "/":

          if self.peek() == "/":
            self.increment()
            self.increment()
            while self.char and self.char != "\n":
              self.increment()
            continue
    
          # elif self.peek() == "*":
          #   self.increment()
          #   self.increment()
          #   while self.char != "*" and self.peek() != "/": # TODO: fix block comments
          #     self.increment()
          #   self.increment()
          #   self.increment()
          #   continue
        elif self.char == "+":
          if self.peek() == "+":
            self.increment()
            self.increment()
            tokens.append(Token(TokenType.INCREMENT, "++", line, column))
            continue

        elif self.char == "-":
          if self.peek() == "-":
            self.increment()
            self.increment()
            tokens.append(Token(TokenType.DECREMENT, "--", line, column))
            continue
        tokens.append(Token(ops[self.char], self.char, line, column))

      elif self.char == "(":
        tokens.append(Token(TokenType.PAROPEN, "(", line, column))

      elif self.char == ")":
        tokens.append(Token(TokenType.PARCLOSE, ")", line, column))

      elif self.char == ";":
        tokens.append(Token(TokenType.SEPR, ";", line, column))

      elif self.char == "?":
        tokens.append(Token(TokenType.TERNARY, "?"))

      elif self.char == ":":
        tokens.append(Token(TokenType.COLON, ":", line, column))

      elif self.char == ",":
        tokens.append(Token(TokenType.COMMA, ",", line, column))

      elif self.char == ">":
        if self.peek() == "=":
          tokens.append(Token(TokenType.GREATER_EQUAL, ">=", line, column))
          self.increment()
          self.increment()
          continue
        tokens.append(Token(TokenType.GREATER, ">", line, column))

      elif self.char == "<":
        if self.peek() == "=":
          tokens.append(Token(TokenType.LESS_EQUAL, "<=", line, column))
          self.increment()
          self.increment()
          continue
        tokens.append(Token(TokenType.LESS, "<", line, column))

      elif self.char == "!":
        if self.peek() == "=":
          tokens.append(Token(TokenType.NOT_EQUAL, "!=", line, column))
          self.increment()
          self.increment()
          continue
        tokens.append(Token(TokenType.NOT, "!", line, column))

      elif self.char == "\"" or self.char == "'":
        first_char = self.char
        self.increment()
        string = ""
        while self.char != first_char:
          string += self.char
          self.increment()
        l, c = self.line_and_column()
        tokens.append(Token(TokenType.STRING, string, l, c))

      elif self.char == "[":
        tokens.append(Token(TokenType.LIST_OPEN, "[", line, column))

      elif self.char == "]":
        tokens.append(Token(TokenType.LIST_CLOSE, "]", line, column))

      elif self.char == ".":
        l, c = self.line_and_column()
        tokens.append(Token(TokenType.DOT, ".", l, c))
  
      else:
        print(f"\x1b[31mUnrecognized character '{self.char}' at {line}:{column}\x1b[0m")
        return []
      
      # tokens[-1].line, tokens[-1].column = line, column
      self.increment()

    return tokens
