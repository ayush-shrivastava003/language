from lexer import *
from syntax_tree import *
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from environment import Environment
from function_obj import *
from call_stack import *
import sys
import readline # cursor navigation in python input

_version = "0.1"

class Interpreter():
  def __init__(self):
    self.parser = Parser()
    self.semantic_analyzer = SemanticAnalyzer(self)
    self.stack = CallStack()
    self.global_environment = Environment()
    self.environment = self.global_environment
    self.depths = {}

  def resolve(self, expr, depth):
    self.depths[expr] = depth

  def lookup(self, name, expr):
    distance = self.depths.get(expr)
    print(expr, type(expr), distance)
    if distance is None:
      raise Exception(f"Unkown name '{name}'")
    return self.environment.get(name, distance=distance)

  def define(self, name, value):
    if self.environment:
      self.environment.assign(name, value)
    else:
      self.global_environment.assign(name, value)

  def is_truthy(self, obj):
    if obj == None:
      return False

    elif type(obj) == bool:
      return obj

    return True

  def traverse_block(self, node, environment):
    old = self.environment
    try:
      self.environment = environment
      for statement in node.children:
        self.traverse(statement)
    finally:
      self.environment = old

  def traverse(self, node):
    if type(node) == Number:
      return node.token.value
    
    elif type(node) == CodeBlock:
      self.traverse_block(node, Environment(self.environment))

    elif type(node) == BinaryOperator:
      op_type = node.operator # type of operator (node.operator is a token, just accessing the type here)
      left = self.traverse(node.left)
      right = self.traverse(node.right)
      if op_type == TokenType.PLUS:
        return left + right
      
      elif op_type == TokenType.MINUS:
        return left - right
      
      elif op_type == TokenType.MULTIPLY:
        return left * right
      
      elif op_type == TokenType.DIVIDE:
        return left / right

      elif op_type == TokenType.GREATER:
        return left > right

      elif op_type == TokenType.LESS:
        return left < right

      elif op_type == TokenType.GREATER_EQUAL:
        return left >= right

      elif op_type == TokenType.LESS_EQUAL:
        return left <= right

      elif op_type == TokenType.NOT_EQUAL:
        if left == None and right == None:
          return True
        elif left == None:
          return False
        return left == right

    elif type(node) == UnaryOperator:
      child = self.traverse(node.child)
      if node.operator.type == TokenType.PLUS:
        return +(child)

      elif node.operator.type == TokenType.MINUS:
        return -(child)

      elif node.operator.type == TokenType.NOT:
        return not self.is_truthy(child)

    elif type(node) == Logical:
      left = self.traverse(node.left)

      if node.operator.type == TokenType.OR:
        if self.is_truthy(left):
          return left

        return self.traverse(node.right)
      
      elif node.operator.type == TokenType.AND:
        if not self.is_truthy(left):
          return left # since left is not truthy, we return that to indicate the operation is falsey.
        return self.traverse(node.right)

    elif type(node) == Declare:
      var_name = node.name.value
      var_value = self.traverse(node.value)
      self.environment.assign(var_name, var_value)
      return var_value

    elif type(node) == Variable:
      return self.lookup(node.token.value, node)

    elif type(node) == Assign:
        var_name = node.name
        var_value = self.traverse(node.value)
        distance = self.depths[var_name]
        if not distance:
          self.global_environment.assign(var_name.token.value, var_value)
        else:
          self.environment.assign(var_name.token.value, var_value, distance=distance)
        return var_value

    elif type(node) == FunctionCall:
      print(self.depths)
      function: Function = self.lookup(node.name.token.value, node.name)
      # function: Function = self.lookup(node.name.value, node)
      args = []
      for arg in node.args:
        args.append(self.traverse(arg))
      return function.call(self, args)

    elif type(node) == Return:
      raise ReturnException(self.traverse(node.statement))

    elif type(node) == Print:
      if node.expression == "":
        print()
        return
      print(self.traverse(node.expression))

    elif type(node) == IfStatement:
      if self.is_truthy(self.traverse(node.condition)):
        self.traverse(node.block)
      
      elif node.else_block != None:
        self.traverse(node.else_block)

    elif type(node) == WhileStatement:
      while self.is_truthy(self.traverse(node.condition)):
        self.traverse(node.block)

    elif type(node) == DeclareFunc:
      function = Function(node)
      self.environment.assign(node.name.token.value, function)

  def walk(self, node):
    print(node)

  def run(self, content):
    try:
      if self.parser.setup(content):
        tree = self.parser.parse()
        self.semantic_analyzer.resolve_block(tree)

        # frame = StackFrame("PROGRAM", "PROGRAM", 1)
        # self.stack.push(frame)
        self.traverse_block(tree, self.global_environment)
        # self.stack.pull()
    
    except Exception as e:
      print(f"\x1b[31m{e}\x1b[0m")
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
        
        self.run(content)

      except KeyboardInterrupt:
        print("\nbye")
        exit(0)

i = Interpreter()

if len(sys.argv) >= 2:
  if sys.argv[1] == "--eval":
    print(i.run(sys.argv[2]))
    quit()
  
  try:
    i.parser.filename = sys.argv[1]
    with open(sys.argv[1]) as f:
     i.run(f.read())
  except FileNotFoundError:
    print(f"\x1b[31mfile does not exist: '{sys.argv[1]}'\x1b[0m")

elif len(sys.argv) == 1:
  i.run_shell()
