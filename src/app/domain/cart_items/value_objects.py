from decimal import Decimal
from logging import getLogger

from annotated_types import Gt
from pydantic import (
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from typing_extensions import Annotated

from app.domain.cart_items.exceptions import MinQtyLimitExceededError

logger = getLogger(__name__)


def qty_validator(
    value: Decimal,
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo,
) -> Decimal:
    try:
        return handler(value)
    except ValidationError:
        logger.info(
            "Invalid item %s qty detected! Required >= 0, got %s.",
            info.data.get("item_id") if info.data else None,
            value,
        )
        raise MinQtyLimitExceededError


Qty = Annotated[Decimal, Gt(Decimal(0)), WrapValidator(qty_validator)]

ITEM_PRICE_PRECISION = 10
ITEM_PRICE_SCALE = 2
