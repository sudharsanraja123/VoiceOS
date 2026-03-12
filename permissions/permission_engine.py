from core.events import Events
from core.event import Event
from core.logger import logger


class PermissionEngine:

    def __init__(self, event_bus):

        self.event_bus = event_bus

        event_bus.subscribe(Events.LLM_DECISION, self.check_permission)

    async def check_permission(self, event):

        decision = event.payload

        if decision["requires_permission"]:

            logger.info("\nAssistant:")
            logger.info(decision["reasoning"])
            logger.info("Do you approve? (yes/no)")

            answer = input("> ")

            if answer.lower() == "yes":

                await self.event_bus.publish(
                    Event(
                        Events.PERMISSION_GRANTED,
                        decision,
                        "permission_engine"
                    )
                )

            else:

                await self.event_bus.publish(
                    Event(
                        Events.PERMISSION_DENIED,
                        decision,
                        "permission_engine"
                    )
                )