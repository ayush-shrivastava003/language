import sys

# declare token types
EOF, UINT, SPACE, ASSIGN = "EOF", "UINT", " ", "="

errorCodes = {
  0: "Syntax Error"
}

class Token():
  def __init__(self, type, value):
    self.type = type
    self.value = value
  
class Interpreter():
  def __init__(self, content):
    """
    content is a string representation of the file.
    """
    self.content = content
    self.index = 0

  def raiseError(self, code, reason):
    print(f"\u001b[31m{errorCodes[code]}:\u001b[0m {reason}")

  def nextToken(self):
    """
    Converts the value at the position into a Token object.
    """
    if self.index > len(self.content) - 1:
      return Token(EOF, "None")
    
    char = self.content[self.index]
    self.index += 1

    if char.isdigit():
      return Token(UINT, int(char))
    
    if char == " ":
      return Token(SPACE, " ")
    
    if char == "=":
      return Token(ASSIGN, "=")

    self.raiseError(0, f"Unidentified type '{char}'")

with open(sys.argv[1]) as file:
  content = file.read()
  file.close()

i = Interpreter(content)
i.nextToken()
i.nextToken()