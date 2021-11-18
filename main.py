import sys

# declare token types
EOF, INT, SPACE, ASSIGN, PLUS, MINUS, NEWLINE, STRING, FLOAT = "EOF", "INT", "SPACE", "EQUAL", "PLUS", "MINUS", "NEWLINE", "STRING", "FLOAT"
errorCodes = {
  0: "Syntax Error",
  1: "Unkown Variable Error",
  2: "Internal Error"
}

class Token():
  def __init__(self, type, value):
    """
    A Token is simply a representation of a value, like integers, equal signs, plus signs, decimal points, etc. 
    """
    self.type = type
    self.value = value

  def toString(self):
    return f"Token({self.type}, {self.value})"
  
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
    self.currentToken = Token("START", "START") # arbitrary Token, just need it to be an instance of the class
    self.char = self.content[self.index]
    self.vars = {}

  def raiseError(self, code, reason):
    """
    Outputs an error and terminates the program.
    """
    print(f"\u001b[31m{errorCodes[code]}:\u001b[0m {reason}") # the gibberish is an ANSI escape code to make the text red and cool
    exit()

  def increment(self):
      """
      Moves the pointer to next character.
      """
      self.index += 1
      
      if self.index < len(self.content):
        self.char = self.content[self.index]
      else:
        self.char = None

  def getWord(self):
    """
    Scans the content for a word, moving the pointer until it hits a space.

    Words can represent variables or function calls (functions and function calls are not implemented at the moment).

    This function is also used as a helper function for `getInt` and `getFloat`.
    """
    final = ""

    while self.char != " " and self.char != None and self.char != "\n":
      final += self.char
      self.increment() # TODO: MAKE THIS CODE BLOCK INTO ITS OWN METHOD
    return final

  def getNum(self):
    """
    Scans the content for a number, moving the pointer until it hits a space.
    Then it checks if the number is an integer or a floating point number.
    """
    final = self.getWord()
    split = final.split('.')

    if len(split) > 2:
      self.raiseError(0, "Received multiple decimals in an expected floating point number")
    elif len(split) == 1:
      return int(final), INT

    for num in split:
      if num == '':
        self.raiseError(0, "Expected value after decimal point")

      elif not num.isdigit():
        self.raiseError(0, "Unexpected character in float")

    return final, FLOAT

  def getString(self):
    """
    Scans the content for an string, moving the pointer until it hits an endquote.
    Strings are only identified by double quotes (").
    """
    final = ""

    while self.char != "\"":
      if self.char == None:
        self.raiseError(0, "Unterminated string before EOF")

      final += self.char
      self.increment()

    return final

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
        self.running = False
        break

      elif self.char == " ":
        self.increment()

      if self.char.isdigit():
        num, type = self.getNum()
        return Token(type, num)

      elif self.char == "=":
        return Token(ASSIGN, "=")

      elif self.char == "\n":
        return Token(NEWLINE, "\n")

      elif self.char == "-":
        return Token(MINUS, "-")
      
      elif self.char == "+":
        return Token(PLUS, "+")

      elif self.char == "\"":
        self.increment() # move pointer to start of string rather than the quote
        return Token(STRING, self.getString())


      self.raiseError(0, f"Unexpected character '{self.char}'")
  
    return Token(EOF, None)

  # def verify(self, type):
  #   """
  #   Verify that the token at the current position is of the expected type.
  #   """
  #   if self.currentToken.type == type:
  #     self.currentToken = self.nextToken() # since the type matches, we can move the pointer to the next self.character
  #   else:
  #     self.raiseError(1, f"Expected type {type} at position {self.index}, got {self.currentToken.type}")

  def run(self):
    """
    Continually calls `nextToken` until it has reached EOF, or an until exception has been raised.
    """
    while self.running and self.currentToken.type != EOF:
      self.currentToken = self.nextToken()
      print(self.currentToken.toString())
  

with open(sys.argv[1]) as file:
  content = file.read()

print(content)
i = Interpreter(content)
i.run()