from lexer import *
from syntax_tree import *
from parser import Parser
import sys

_version = "0.1"

class Interpreter():
  def __init__(self):
    self.tokens = []
    self.parser = Parser()
    self.token_index = -1
    self.current_token = None
    self.global_scope = {}

  def stringify(self):
    return [str(token) for token in self.tokens]

  def walk_tree(self, node):
    r"""
    recursive function that walks along the abstract syntax tree (created by the parser) and
    evaluates the result.

    assume the parser has generated the following tree:
    2 * 2 + 4
    ```
        (+)
       /   \
     (*)    (4)
    /   \
  (2)   (2)
    ```

    the interpreter will recognize the binary operator at the top (+), then read the left and right nodes. Since hte left node is also
    a binary operator, `walk_tree` will call itself again to evaluate the multiplication. Then,  
    """
    if type(node) == Number:
      return node.token.value
    
    elif type(node) == BinaryOperator:
      op_type = node.operator.type # type of operator (node.operator is a token, just accessing the type here)
  
      if op_type == PLUS:
        left = self.walk_tree(node.left)
        right = self.walk_tree(node.right)
        print(f"{left} + {right}")
        return left + right
      
      elif op_type == MINUS:
        left = self.walk_tree(node.left)
        right = self.walk_tree(node.right)
        print(f"{left} - {right}")
        return left - right
      
      elif op_type == MULTIPLY:
        left = self.walk_tree(node.left)
        right = self.walk_tree(node.right)
        print(f"{left} * {right}")
        return left * right
      
      elif op_type == DIVIDE:
        left = self.walk_tree(node.left)
        right = self.walk_tree(node.right)
        print(f"{left} / {right}")
        return left / right

    elif type(node) == UnaryOperator:
      if node.operator.type == PLUS:
        return +(self.walk_tree(node.child))

      elif node.operator.type == MINUS:
        return -(self.walk_tree(node.child))

    elif type(node) == Variable:
        if node.token.value not in self.global_scope.keys():
            raise Exception(f"Unknown variable '{node.token.value}'")
        else:
            # print("returning var", self.global_scope[node.token.value])
            return self.global_scope[node.token.value]

    elif type(node) == Assign:
        self.global_scope[node.name.value] = self.walk_tree(node.value)
        return {node.name.value: self.global_scope[node.name.value]}

  def run(self, content):
    self.parser.setup(content)
    tree = self.parser.parse()
    # print(tree)
    return [self.walk_tree(child) for child in tree.children]

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
        
        result = self.run(content)

        if result != [None]:
          print(result)
          # print("\n".join(result))

      except KeyboardInterrupt:
        print("\nbye")
        exit(0)

i = Interpreter()

if len(sys.argv) >= 2:
  if sys.argv[1] == "--eval":
    print(i.run(sys.argv[2]))
    exit()

  try:
    with open(sys.argv[1]) as f:
      print(i.run(f.read()))
  except FileNotFoundError:
    print(f"\x1b[31mfile does not exist: '{sys.argv[1]}'\x1b[0m")

elif len(sys.argv) == 1:
    i.run_shell()
