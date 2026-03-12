from tools.tool_registry import ToolRegistry
from tools.math_tools import solve_expression
from tools.web_tools import web_research

registry = ToolRegistry()
registry.register("web_research", web_research)
registry.register("solve_expression", solve_expression)