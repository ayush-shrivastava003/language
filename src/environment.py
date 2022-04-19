class Environment():
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def __repr__(self):
        return "".join([f"{key} ({type(key)}): {value}" for key, value in self.values.items()])

    # def define(self, value):
    #     self.values.append(value)

    def get(self, name, distance=None):
        value = None
        if distance:
             value = self.ancestor(distance).values.get(name)
        else:
             value = self.values.get(name)

        if value is None:
            raise Exception(f"Unkown name '{name}'")  
        return value

    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.parent
        return environment

    def assign(self, name, value, distance=None):
        if distance:
            ancestor = self.ancestor(distance)
            ancestor.values[name] = value
        else:
            self.values[name] = value