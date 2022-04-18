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
    end = "="*8
    return f"{self.type} {self.name} @ stack level {self.level}\n{content}\n{end}\n"

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
  
  def show_frame(self, level=None):
    """
    return the frame currently executing in the stack (the topmost one)
    """
    return self.frames[-1]

  def level(self):
    return self.show_frame().level + 1
