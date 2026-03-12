from core.events import Events
from core.event import Event
from tools.os_control.os_tool_router import OSToolRouter
from core.logger import logger


class ToolExecutor:

    def __init__(self, event_bus, registry):

        self.bus = event_bus
        self.registry = registry
        self.os_tools = OSToolRouter()

        event_bus.subscribe(
            Events.PERMISSION_GRANTED,
            self.execute_tool
        )

    async def execute_tool(self, event):

        decision = event.payload

        if not decision["tool_needed"]:
            return

        tool_name = decision["tool_name"]
        params = decision["tool_parameters"]

        tool = self.registry.get(tool_name)

        if tool and tool_name.startswith("os_"):

            return self.os_tools.execute(tool_name.replace("os_", ""), params)

        if tool is None:
            logger.warning("Tool not found")
            return

        result = tool(**params)

        await self.bus.publish(
            Event(
                Events.TOOL_RESULT,
                {"result": result},
                "tool_executor"
            )
        )