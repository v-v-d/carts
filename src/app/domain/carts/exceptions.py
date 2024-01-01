from decimal import Decimal


class BaseCartDomainError(Exception):
    pass


class CartItemDoesNotExistError(BaseCartDomainError):
    pass


class CartItemAlreadyExistsError(BaseCartDomainError):
    pass


class NotOwnedByUserError(BaseCartDomainError):
    pass


class MaxItemsQtyLimitExceeded(BaseCartDomainError):
    pass


class SpecificItemQtyLimitExceeded(BaseCartDomainError):
    def __init__(self, limit: Decimal, actual: Decimal) -> None:
        self.limit = limit
        self.actual = actual

    def __str__(self) -> str:
        return f"limit: {self.limit}, actual: {self.actual}"


class ChangeStatusError(BaseCartDomainError):
    pass


class OperationForbiddenError(BaseCartDomainError):
    pass


class CouponAlreadyAppliedError(BaseCartDomainError):
    pass


class CouponDoesNotExistError(BaseCartDomainError):
    pass


class CantBeLockedError(BaseCartDomainError):
    pass
