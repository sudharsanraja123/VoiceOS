class ToolRegistry:

    def __init__(self):

        self.tools = {}

    def register(self, name, func):

        self.tools[name] = func

    def execute(self, name, params):

        if name in self.tools:

            return self.tools[name](**params)