from environment import Environment

class ReturnException(Exception):
  """
  this exception is raised once we hit a return statement. 
  it allows the interpreter to jump back several layers of nesting to reach the function call.
  """
  def __init__(self, value, *args: object):
      super().__init__(*args)
      self.value = value

class Callable():
    def __init__(self) -> None:
        pass

    def call(self, interpreter, args):
        pass


class Function(Callable):
    def __init__(self, closure, expr):
        self.closure = closure
        self.expr = expr
        self.args = expr.args

    def __repr__(self):
        name = self.expr.name.token
        return f"<fn {name.value} at {name.line}:{name.column}>"
    
    def arity(self):
        return len(self.args)

    def call(self, interpreter, args):
        environment = Environment(self.closure)

        for expected, actual in zip(self.expr.args, args):
            environment.assign(expected.name, actual)
        
        try:
            interpreter.traverse_block(self.expr.statements, environment)
        except ReturnException as return_value:
            return return_value.value
        
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.assign("self", instance)
        return Function(environment, self.expr)

class BuiltinFunction(Function):
    def __init__(self, name, action):
        self.name = name
        self.action = action
        self.args = ()

    def call(self, interpreter, args):
        return self.action()

    def __repr__(self):
        return f"<native fn {self.name}>"
    
    def bind(self, instance):
        return self
    
class Class(Callable):
    def __init__(self, expr, methods):
        self.expr = expr
        self.args = []
        self.methods = methods

    def __repr__(self) -> str:
        return f"<class '{self.expr.name}'>"
    
    def arity(self):
        new_fn = self.methods.get("new")
        if new_fn is None:
            return 0
        return new_fn.arity()
    
    def call(self, interpreter, args):
        instance = Instance(self)
        new_fn = self.methods.get("new")
        if new_fn is not None:
            new_fn.bind(instance).call(interpreter, args)
        return instance
    
    def get_method(self, name):
        return self.methods.get(name)
    
class List(Class):
    def __init__(self, items, expr):
        self.items = items
        self.expr = expr
        self.methods = {"length": BuiltinFunction("length", self.length)}

    def call(self, interpreter, args):
        instance = Instance(self)
        return instance

    def __repr__(self):
        return f"<built-in list class>"
    
    def length(self):
        return len(self.items)
    
class Instance():
    def __init__(self, clss) -> None:
        self.clss = clss
        self.fields = {}

    def get(self, name):
        get = self.fields.get(name.token.value)
        method = self.clss.get_method(name.token.value)
        if type(method) in (Function, BuiltinFunction) and method is not None:
            return method.bind(self)
        return get
    
    def set(self, name, value):
        self.fields[name.token.value] = value

    def __repr__(self):
        if type(self.clss) == List:
            return f"{self.clss.items}"
        return f"<'{self.clss.expr.name.token.value}' object>"