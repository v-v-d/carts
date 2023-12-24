from fastapi import HTTPException, status

AUTHORIZATION_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"code": 1000, "message": "Authorization failed."},
)
FORBIDDEN_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 1001, "message": "Forbidden."},
)

RETRIEVE_CART_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 2000, "message": "Cart not found."},
)
ACTIVE_CART_ALREADY_EXISTS_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 2001, "message": "Active cart already exists."},
)
DELETE_CART_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 2002, "message": "The cart can't be deactivated."},
)
CART_OPERATION_FORBIDDEN_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 2003, "message": "The cart can't be modified."},
)
CART_ITEM_QTY_LIMIT_EXCEEDED_HTTP_ERROR = lambda err: HTTPException(  # noqa E731
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "code": 2004,
        "message": "Item qty limit exceeded. Limit: {limit}, got: {actual}.".format(
            limit=err.limit, actual=err.actual
        ),
    },
)

ADD_CART_ITEM_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 3000, "message": "Failed to add item to cart."},
)
CART_ITEM_MAX_QTY_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 3001, "message": "Max cart items qty limit exceeded."},
)
UPDATE_CART_ITEM_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 3002, "message": "Failed to update cart item."},
)

COUPON_ALREADY_APPLIED_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "code": 4000,
        "message": (
            "Coupon has already been applied. You need to delete the existing coupon "
            "before applying a new one."
        ),
    },
)
COUPON_APPLYING_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "code": 4001,
        "message": "Failed to apply the coupon. Please try applying it again.",
    },
)

CART_IN_PROCESS_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "code": 5000,
        "message": "The action couldn't be processed. The cart is already being processed.",
    },
)
CART_CANT_BE_LOCKED_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "code": 5001,
        "message": "The cart can't be locked due to not all conditions are met.",
    },
)
CART_CANT_BE_UNLOCKED_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 5002, "message": "The cart can't be unlocked."},
)
CART_CANT_BE_COMPLETED_HTTP_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"code": 5003, "message": "The cart can't be completed."},
)
