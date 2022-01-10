PLUS, MINUS, MULTIPLY, DIVIDE, NUM = "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "NUM"
ops = {"+": PLUS, "-": MINUS, "*": MULTIPLY, "/": DIVIDE}

class Token():
  def __init__(self, type, value):
    self.type = type
    self.value = value

  def stringify(self):
    return f"Token({self.type}, {self.value})"
    
class Interpreter():
  def __init__(self):
    self.tokens = []

  def stringify(self, tokens):
    for token in range(len(tokens)):
      tokens[token] = tokens[token].stringify()

    return tokens
  
  def tokenize(self, content):
    for char in content:
      print("char is", char)
      if char.isdigit():
        self.tokens.append(Token(NUM, int(char)))

      elif char in ("+", "-", "*", "/"):
        self.tokens.append(Token(ops[char], char))

  def eval(self, tokens):
    operator = tokens[1].type

    if operator == PLUS:
      return tokens[0].value + tokens[2].value

    elif operator == MINUS:
      return tokens[0].value - tokens[2].value

    elif operator == MULTIPLY:
      return tokens[0].value * tokens[2].value

    elif operator == DIVIDE:
      return tokens[0].value / tokens[2].value

    else:
      print("invalid expression (single digit integers with one of the four basic operations in between)")
      exit(0)

  def run(self, content):
    self.tokenize(content)
    print(self.eval(self.tokens))

Interpreter().run("1 / 2")