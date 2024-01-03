from app.infra.repositories.sqla.cart_coupons import CartCouponsRepository


class TestCartCouponsRepository(CartCouponsRepository):
    """
    Test repository for interactions with cart_coupons operations through database.
    """

    __test__ = False
