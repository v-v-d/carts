class BaseItemsRepoError(Exception):
    pass


class ItemAlreadyExists(BaseItemsRepoError):
    pass
