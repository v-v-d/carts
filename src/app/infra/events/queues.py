from enum import Enum


class QueueNameEnum(str, Enum):
    EXAMPLE_QUEUE = "example_queue"
    PERIODIC_QUEUE = "periodic_queue"
