import pytest

from app import api
from app.containers import Container


@pytest.fixture()
def container() -> Container:
    container = Container()
    container.wire(packages=[api.rest.internal.v1.carts])

    return container
