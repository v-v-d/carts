from enum import StrEnum


class CartStatusEnum(StrEnum):
    OPENED = "OPENED"
    DEACTIVATED = "DEACTIVATED"
    LOCKED = "LOCKED"
    COMPLETED = "COMPLETED"
