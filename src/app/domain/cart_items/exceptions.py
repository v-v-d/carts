class BaseItemsDomainError(Exception):
    pass


class MinQtyLimitExceededError(BaseItemsDomainError):
    pass
