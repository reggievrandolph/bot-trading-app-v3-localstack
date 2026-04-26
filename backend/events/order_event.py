from pprint import pprint
from events.event import Event


class OrderEvent(Event):
    def __init__(self, event_type, source, timestamp, symbol):
        super().__init__(event_type, source, timestamp)
        self.symbol = symbol
        self.current_price = None

    def _to_redis_format(self):
        try:
            # Flatten the dictionary and ensure keys and values are of acceptable types
            flattened = {
                "event_type": self.event_type,
                "source": self.source,
                "timestamp": str(self.timestamp),
                "symbol": self.symbol,
            }
            # for k, v in self.conditions.items():
            #     flattened[f"condition_{k}"] = v
            return flattened
        except Exception as e:
            pprint(f"Error converting OrderEvent to Redis format: {e}")

    def publish(self):
        try:
            pprint("Publishing OrderEvent")
            self.redis_client.xadd("ORDER_STREAM", self._to_redis_format())
        except Exception as e:
            pprint(f"Error publishing OrderEvent: {e}")

    # def __str__(self) -> str:
    #     return super().__str__() + f"Conditions: {self.conditions}"
