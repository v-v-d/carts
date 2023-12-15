class BaseCartDomainError(Exception):
    pass


class ItemDoesNotExistInCartError(BaseCartDomainError):
    pass
