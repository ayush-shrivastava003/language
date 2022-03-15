from pickletools import optimize
from lexer import *
from syntax_tree import *
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
import sys
import readline # cursor navigation in python input

_version = "0.1"

class ReturnException(Exception):
  """
  this exception is raised once we hit a return statement. 
  it allows the interpreter to jump back several layers of nesting to reach the function call.
  """
  def __init__(self, value, *args: object):
      super().__init__(*args)
      self.value = value

class StackFrame():
  def __init__(self, name, type, level):
    """
    represents a single frame in the call stack.
    """
    self.name = name
    self.type = type
    self.level = level
    self.data = {}

  def __setitem__(self, key, value):
    """
    builtin function by python that allows easy modifications to the `StackFrame.data` dictionary.
    """
    self.data[key] = value

  def __getitem__(self, key):
    return self.data.get(key)

  def __repr__(self):
    content = "CONTENT:\n" + ("="*8)
    for key, value in self.data.items():
      content += f"\n{key} ({type(key)}) : {value}"
    return f"{self.type} {self.name} @ stack level {self.level}\n{content}"

class CallStack():
  def __init__(self):
    """
    represents the interpreter's call stack. adds a "frame" to the stack when new code is executed (i.e functions),
    and removes them when they're done.
    """
    self.frames = []

  def __repr__(self):
    frames = '\n'.join(reversed(self.frames))
    return f"Call Stack:\n{frames}"

  def push(self, frame):
    """
    push a new frame onto the call stack.
    """
    self.frames.append(frame)
  
  def pull(self):
    """
    remove the topmost frame from the call stack.
    """
    self.frames.pop()
  
  def show_frame(self):
    """
    return the frame currently executing in the stack (the topmost one)
    """
    return self.frames[-1]

  def level(self):
    return self.show_frame().level + 1

class Interpreter():
  def __init__(self):
    self.parser = Parser()
    self.semantic_analyzer = SemanticAnalyzer()
    self.stack = CallStack()

  def is_truthy(self, obj):
    if obj == None:
      return False

    elif type(obj) == bool:
      return obj

    return True

  def traverse(self, node):
    if type(node) == Number:
      return node.token.value
    
    elif type(node) == CodeBlock:
      for statement in node.children:
        self.traverse(statement)

    elif type(node) == BinaryOperator:
      op_type = node.operator.type # type of operator (node.operator is a token, just accessing the type here)
      left = self.traverse(node.left)
      right = self.traverse(node.right)
  
      if op_type == PLUS:
        return left + right
      
      elif op_type == MINUS:
        return left - right
      
      elif op_type == MULTIPLY:
        return left * right
      
      elif op_type == DIVIDE:
        return left / right

      elif op_type == GREATER:
        return left > right

      elif op_type == LESS:
        return left < right

      elif op_type == GREATER_EQUAL:
        return left >= right

      elif op_type == LESS_EQUAL:
        return left <= right

      elif op_type == NOT_EQUAL:
        if left == None and right == None:
          return True
        elif left == None:
          return False
        return left == right

    elif type(node) == UnaryOperator:
      child = self.traverse(node.child)
      if node.operator.type == PLUS:
        return +(child)

      elif node.operator.type == MINUS:
        return -(child)

      elif node.operator.type == NOT:
        return not self.is_truthy(child)

    elif type(node) == Logical:
      left = self.traverse(node.left)

      if node.operator.type == OR:
        if self.is_truthy(left):
          return left

        return self.traverse(node.right)
      
      elif node.operator.type == AND:
        if not self.is_truthy(left):
          return left # since left is not truthy, we return that to indicate the operation is falsey.
        return self.traverse(node.right)

    elif type(node) == Declare:
      var_name = node.name.value
      var_value = self.traverse(node.value)
      frame = self.stack.show_frame()
      frame[var_name] = var_value
      return var_value

    elif type(node) == Variable:
      return self.stack.show_frame()[node.token.value]

    elif type(node) == Assign:
        var_name = node.name.token.value
        var_value = self.traverse(node.value)
        frame = self.stack.show_frame()
        frame[var_name] = var_value
        return var_value

    elif type(node) == FunctionCall:
      frame = StackFrame(node.name, "FUNCTION", self.stack.level())

      expected_args = node.symbol.args
      passed_args = node.args
      return_value = None

      for arg_name, arg_value in zip(expected_args, passed_args):
          frame[arg_name.name] = self.traverse(arg_value)

      self.stack.push(frame)
      try:
        self.traverse(node.symbol.statements)

      except ReturnException as e:
        return_value = e.value

      self.stack.pull()
      return return_value

    elif type(node) == Return:
      raise ReturnException(self.traverse(node.statement))

    elif type(node) == Print:
      print(self.traverse(node.expression))

    elif type(node) == IfStatement:
      if self.is_truthy(self.traverse(node.condition)):
        self.traverse(node.block)
      
      elif node.else_block != None:
        self.traverse(node.block)

    elif type(node) == WhileStatement:
      while self.is_truthy(self.traverse(node.condition)):
        self.traverse(node.block)

  def run(self, content):
    try:
      if self.parser.setup(content):
        tree = self.parser.parse()
        self.semantic_analyzer.traverse(tree)

        frame = StackFrame("PROGRAM", "PROGRAM", 1)
        self.stack.push(frame)
        self.traverse(tree)
        self.stack.pull()
    
    except Exception as e:
      print("\x1b[0m")
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

      except KeyboardInterrupt:
        print("\nbye")
        exit(0)

i = Interpreter()

if len(sys.argv) >= 2:
  if sys.argv[1] == "--eval":
    print(i.run(sys.argv[2]))
    quit()

  try:
    with open(sys.argv[1]) as f:
     i.run(f.read())
  except FileNotFoundError:
    print(f"\x1b[31mfile does not exist: '{sys.argv[1]}'\x1b[0m")

elif len(sys.argv) == 1:
  i.run_shell()
