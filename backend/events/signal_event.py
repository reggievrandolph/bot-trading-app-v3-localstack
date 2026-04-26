from events.event import Event


class SignalEvent(Event):
    def __init__(
        self, event_type, source, timestamp, symbol, current_price, conditions: dict
    ):
        super().__init__(event_type, source, timestamp)
        self.conditions: dict = conditions
        self.symbol = symbol
        self.current_price = current_price

    def _to_redis_format(self):
        # Flatten the dictionary and ensure keys and values are of acceptable types
        flattened = {
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": str(self.timestamp),
            "symbol": self.symbol,
            "current_price": self.current_price,
        }
        for k, v in self.conditions.items():
            flattened[f"condition_{k}"] = v
        return flattened

    def publish(self):
        self.redis_client.xadd("SIGNAL_STREAM", self._to_redis_format())

    def __str__(self) -> str:
        return super().__str__() + f"Conditions: {self.conditions}"
