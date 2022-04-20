from environment import Environment

class ReturnException(Exception):
  """
  this exception is raised once we hit a return statement. 
  it allows the interpreter to jump back several layers of nesting to reach the function call.
  """
  def __init__(self, value, *args: object):
      super().__init__(*args)
      self.value = value

class Function():
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        name = self.expr.name.token
        return f"<fn {name.value} at {name.line}:{name.column}>"

    def call(self, interpreter, args):
        environment = Environment(interpreter.global_environment)

        for expected, actual in zip(self.expr.args, args):
            environment.assign(expected.name, actual)
        
        try:
            interpreter.traverse_block(self.expr.statements, environment)
        except ReturnException as return_value:
            return return_value.value