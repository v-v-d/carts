from app.infra.unit_of_work.sqla import Uow
from tests.environment.repositories.cart_coupons import TestCartCouponsRepository
from tests.environment.repositories.carts import TestCartsRepository
from tests.environment.repositories.carts_notifications import (
    TestCartsNotificationsRepository,
)
from tests.environment.repositories.items import TestItemsRepository


class TestUow(Uow):
    __test__ = False

    items: TestItemsRepository
    carts: TestCartsRepository
    cart_coupons: TestCartCouponsRepository
    carts_notifications: TestCartsNotificationsRepository

    async def __aenter__(self) -> "TestUow":
        self._session = self._session_factory()

        self.items = TestItemsRepository(self._session)
        self.carts = TestCartsRepository(self._session)
        self.cart_coupons = TestCartCouponsRepository(self._session)
        self.carts_notifications = TestCartsNotificationsRepository(self._session)

        return self
