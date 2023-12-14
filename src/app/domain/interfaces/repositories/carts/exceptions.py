class BaseCartsRepoError(Exception):
    pass


class CartNotFoundError(BaseCartsRepoError):
    pass
