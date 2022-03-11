from lexer import *
from syntax_tree import *
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
import sys
import readline # cursor navigation in python input

_version = "0.1"

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
      content += f"\n{key} : {value}"
    return f"{self.type} {self.name} @ stack level {self.level}\n{content}"

class CallStack():
  def __init__(self):
    """
    represents the interpreter's call stack. adds a "frame" to the stack when new code is executed (i.e functions),
    and removes them when they're done.
    """
    self.frames = []

  def __repr__(self):
    frames = '\n- '.join(reversed(self.frames))
    return f"Call Stack:\n{frames}"

  def push(self, frame):
    """
    push a new frame onto the call stack.
    """
    self.frames.append(frame)
    # print("pushed new frame to stack:", frame)
  
  def pull(self, frame):
    """
    remove the topmost frame from the call stack.
    """
    self.frames.pop()
    # print("pulled frame from stack:", frame)
  
  def show_frame(self):
    """
    return the frame currently executing in the stack (the topmost one)
    """
    # print("returning", self.frames[-1])
    return self.frames[-1]

class Interpreter():
  def __init__(self):
    self.parser = Parser()
    self.semantic_analyzer = SemanticAnalyzer()
    self.stack = CallStack()

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
      # self.global_scope[var_name] = var_value
      frame = self.stack.show_frame()
      frame[var_name] = var_value
      return var_value

    elif type(node) == Variable:
      return self.stack.show_frame()[node.token.value]

    elif type(node) == Assign:
        var_name = self.traverse(node.name)
        var_value = self.traverse(node.value)
        frame = self.stack.show_frame()
        frame[var_name] = var_value
        return var_value

    elif type(node) == DeclareFunc:
      pass

    elif type(node) == FunctionCall:
      # stack_level = len(self.stack.frames) + 1
      frame = StackFrame(node.name, "FUNCTION", node.symbol.level)

      expected_args = node.symbol.args
      passed_args = node.args

      for arg_name, arg_value in zip(expected_args, passed_args):
          frame[arg_name] = arg_value

      print(f"adding {frame.name} to call stack")
      self.stack.push(frame)
      # [self.traverse(statement) for statement in node.symbol.statements]
      for statement in node.symbol.statements:
        print(f"traversing {statement}")
        self.traverse(statement)


  def run(self, content):
    try:
      self.parser.setup(content)
      tree = self.parser.parse()
      [self.semantic_analyzer.traverse(child) for child in tree.children]

      frame = StackFrame("PROGRAM", "PROGRAM", 1)
      self.stack.push(frame)
      final = [self.traverse(child) for child in tree.children]
      self.stack.pull(frame)
      return final
    
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
          # print("\n".join(result))

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
      print(i.run(f.read()))
  except FileNotFoundError:
    print(f"\x1b[31mfile does not exist: '{sys.argv[1]}'\x1b[0m")

elif len(sys.argv) == 1:
  with open("test.language") as f:
    print(i.run(f.read()))
