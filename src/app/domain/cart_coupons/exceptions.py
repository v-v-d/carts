class BaseCartCouponDomainError(Exception):
    pass


class CartCostValidationError(BaseCartCouponDomainError):
    pass


class DiscountValidationError(BaseCartCouponDomainError):
    pass
