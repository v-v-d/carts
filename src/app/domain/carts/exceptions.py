class BaseCartDomainError(Exception):
    pass


class CartItemDoesNotExistError(BaseCartDomainError):
    pass


class NotOwnedByUserError(BaseCartDomainError):
    pass


class MaxItemsQtyLimitExceeded(BaseCartDomainError):
    pass


class ChangeStatusError(BaseCartDomainError):
    pass


class OperationForbiddenError(BaseCartDomainError):
    pass
