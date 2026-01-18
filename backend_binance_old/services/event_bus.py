# services/event_bus.py
class EventBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, event: str, handler):
        self.handlers.setdefault(event, []).append(handler)

    async def publish(self, event: str, data: dict):
        for h in self.handlers.get(event, []):
            await h(data)
