from uuid import UUID

import pytest

from tests.utils import fake


@pytest.fixture()
def cart_id() -> UUID:
    return fake.cryptographic.uuid_object()
