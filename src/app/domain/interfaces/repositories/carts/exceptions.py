class BaseCartsRepoError(Exception):
    pass


class CartNotFoundError(BaseCartsRepoError):
    pass


class ActiveCartAlreadyExistsError(BaseCartsRepoError):
    pass
