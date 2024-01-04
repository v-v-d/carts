import pytest

from app import api
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def item_id() -> int:
    return fake.numeric.integer_number(start=1)


@pytest.fixture()
def container() -> Container:
    container = Container()
    container.wire(packages=[api.rest.public.v1.cart_items])

    return container
