import sys

# declare token types
EOF, INT, SPACE, ASSIGN, PLUS, MINUS, NEWLINE = "EOF", "INT", " ", "=", "+", "-", "\n"

errorCodes = {
  0: "Syntax Error",
  1: "Internal Error"
}

class Token():
  def __init__(self, type, value):
    """
    A Token is simply a representation of a value, like integers, equal signs, plus signs, decimal points, etc. 
    """
    self.type = type
    self.value = value
  
class Interpreter():
  def __init__(self, content):
    """
    The actual interpreter for the language.

    Some information:

    * content is a string representation of the file.

    * index is the position of the "pointer" in the content.

    * running indicates whether or not the program should be continuing (it would only be false at EOF or once an error is raised).
    """
    self.content = content
    self.index = -1
    self.running = True
    self.currentToken = None
    self.char = self.content[self.index]
    self.vars = {}

  def raiseError(self, code, reason):
    """
    Outputs an error and terminates the program by setting `self.running` to false.
    """
    print(f"\u001b[31m{errorCodes[code]}:\u001b[0m {reason}") # the gibberish is an ANSI escape code to make the text red and cool
    self.running = False

  def increment(self):
      """
      Moves the pointer to next character.
      """
      self.index += 1
      
      if self.index < len(self.content):
        self.char = self.content[self.index]
      else:
        self.running = False
        self.char = None

  def getInt(self):
    """
    Scans the content for an integer, moving the pointer until it hits a space.
    """
    final = ""

    while self.char != " " and self.char != None: # checks for None in case the next char is EOF
      final += self.char
      self.increment()

    return int(final)

  def nextToken(self):
    """
    Increments the pointer and converts the value at its position into a Token object.
    For example, if the content looked like this:

    `1+1`

    And the current position (`self.index`) is 0, `nextToken` will increment the pointer to 1 and convert it to a token. In this case,
    nextToken would return a token of type `PLUS`.
    """
    while self.char != None:
      self.increment()

      if self.char == None:
        break

      elif self.char == " ":
        self.increment()

      if self.char.isdigit():
        return Token(INT, self.getInt())

      elif self.char == "=":
        return Token(ASSIGN, "=")

      elif self.char == "\n":
        return Token(NEWLINE, "\n")

      elif self.char == "-":
        return Token(MINUS, "-")
      
      elif self.char == "+":
        return Token(PLUS, "+")


      self.raiseError(0, f"Unidentified type '{self.char}'")
  
    return Token(EOF, None)

  def verify(self, type):
    """
    Verify that the token at the current position is of the expected type.
    """
    if self.currentToken.type == type:
      self.currentToken = self.nextToken() # since the type matches, we can move the pointer to the next self.character
    else:
      self.raiseError(1, f"Expected type {type} at position {self.index}, got {self.currentToken.type}")

  def run(self):
    """
    Continually calls `nextToken` until it has reached EOF, or an until exception has been raised.
    """
    while self.running:
      self.currentToken = self.nextToken()
      print(self.currentToken, self.currentToken.value)
  

with open(sys.argv[1]) as file:
  content = file.read()

print(content)
i = Interpreter(content)
i.run()