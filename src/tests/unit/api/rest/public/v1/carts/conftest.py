from uuid import UUID

import pytest

from app import api
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def cart_id() -> UUID:
    return fake.cryptographic.uuid_object()


@pytest.fixture()
def container() -> Container:
    container = Container()
    container.wire(packages=[api.rest.public.v1.carts])

    return container
