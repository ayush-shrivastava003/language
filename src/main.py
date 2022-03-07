from lexer import *
from syntax_tree import *
from parser import Parser
from symbol_table import SemanticAnalyzer
import sys
import readline # cursor navigation in python input

_version = "0.1"

class Interpreter():
  def __init__(self):
    self.tokens = []
    self.parser = Parser()
    self.semantic_analyzer = SemanticAnalyzer()
    self.token_index = -1
    self.current_token = None
    self.global_scope = {}

  def stringify(self):
    return [str(token) for token in self.tokens]

  def traverse(self, node):
    if type(node) == Number:
      return node.token.value
    
    elif type(node) == BinaryOperator:
      op_type = node.operator.type # type of operator (node.operator is a token, just accessing the type here)
  
      if op_type == PLUS:
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        return left + right
      
      elif op_type == MINUS:
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        return left - right
      
      elif op_type == MULTIPLY:
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        return left * right
      
      elif op_type == DIVIDE:
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        return left / right

    elif type(node) == UnaryOperator:
      if node.operator.type == PLUS:
        return +(self.traverse(node.child))

      elif node.operator.type == MINUS:
        return -(self.traverse(node.child))

    elif type(node) == Declare:
      var_name = node.name.value
      var_value = self.traverse(node.value)
      self.global_scope[var_name] = var_value
      return var_value

    elif type(node) == Variable:
      print(node)
      return self.global_scope[node.token.value]

    elif type(node) == Assign:
        print(node.name)
        var_name = self.traverse(node.name)
        var_value = self.traverse(node.value)
        self.global_scope[var_name] = var_value
        return var_value

  def run(self, content):
    try:
      self.parser.setup(content)
      tree = self.parser.parse()
      [self.semantic_analyzer.traverse(child) for child in tree.children]
      return [self.traverse(child) for child in tree.children]
    
    except Exception as e:
      # print("whoops", e)
      raise e

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
