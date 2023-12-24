from decimal import Decimal
from logging import getLogger

from annotated_types import Ge, Gt
from pydantic import (
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from typing_extensions import Annotated

from app.domain.cart_coupons.exceptions import (
    CartCostValidationError,
    DiscountValidationError,
)

logger = getLogger(__name__)


def cart_cost_validator(
    value: Decimal,
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo,
) -> Decimal:
    try:
        return handler(value)
    except ValidationError:
        logger.info(
            "Cart %s. Invalid coupon min cart cost detected! Required >= 0, got %s.",
            info.data.get("cart_id"),
            value,
        )
        raise CartCostValidationError


def discount_validator(
    value: Decimal,
    handler: ValidatorFunctionWrapHandler,
    info: ValidationInfo,
) -> Decimal:
    try:
        return handler(value)
    except ValidationError:
        logger.info(
            "Cart %s. Invalid coupon discount detected! Required > 0, got %s.",
            info.data.get("cart_id"),
            value,
        )
        raise DiscountValidationError


CartCost = Annotated[Decimal, Ge(Decimal(0)), WrapValidator(cart_cost_validator)]
Discount = Annotated[Decimal, Gt(Decimal(0)), WrapValidator(discount_validator)]

CART_COST_PRECISION = 10
CART_COST_SCALE = 2
DISCOUNT_PRECISION = 10
DISCOUNT_SCALE = 2
