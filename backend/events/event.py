from abc import abstractmethod
import datetime
from enum import Enum

from redis_base import RedisBaseService


class EventType(Enum):
    BULL_ENTRY_SIGNAL = "BULL_ENTRY_SIGNAL"
    BEAR_ENTRY_SIGNAL = "BEAR_ENTRY_SIGNAL"
    BULL_EXIT_SIGNAL = "BULL_EXIT_SIGNAL"
    BEAR_EXIT_SIGNAL = "BEAR_EXIT_SIGNAL"
    SERVICE_ERROR = "SERVICE_ERROR"
    ENTRY_ORDER = "ENTRY_ORDER"
    EXIT_ORDER = "EXIT_ORDER"
    ORDER_FILLED = "ORDER_FILLED"


class Event(RedisBaseService):
    def __init__(self, event_type, source, timestamp):
        self.event_type = event_type
        self.source = source
        self.timestamp = timestamp
        super().__init__()

    @abstractmethod
    def _to_redis_format(self):
        pass

    @abstractmethod
    def publish(self):
        pass
