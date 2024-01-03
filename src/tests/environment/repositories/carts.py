from app.infra.repositories.sqla.carts import CartsRepository


class TestCartsRepository(CartsRepository):
    """
    Test repository for interactions with carts operations through database.
    """

    __test__ = False
