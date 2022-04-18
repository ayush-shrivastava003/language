class Environment():
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def __repr__(self):
        return f"{self.values}"

    # def define(self, value):
    #     self.values.append(value)

    def get(self, name, distance=None):
        if distance:
            return self.ancestor(distance).values[name]
        else:
            return self.values[name]

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