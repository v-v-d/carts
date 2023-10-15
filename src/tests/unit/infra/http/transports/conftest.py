import pytest

from tests.utils import fake


@pytest.fixture()
def response_err_text() -> str:
    return fake.text.word()
