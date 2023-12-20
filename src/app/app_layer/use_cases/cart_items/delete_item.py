from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.delete_item import IDeleteCartItemUseCase
from app.app_layer.interfaces.use_cases.cart_items.dto import DeleteCartItemInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CartItemDoesNotExistError


class DeleteCartItemUseCase(IDeleteCartItemUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: DeleteCartItemInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            cart.check_user_ownership(user_id=user.id)
            cart = await self._update_cart(cart=cart, data=data)

        return CartOutputDTO.model_validate(cart)

    async def _update_cart(self, cart: Cart, data: DeleteCartItemInputDTO) -> Cart:
        try:
            item = cart.get_item(data.item_id)
        except CartItemDoesNotExistError:
            return cart

        return await self._delete_item_from_cart(cart=cart, item=item)

    async def _delete_item_from_cart(self, cart: Cart, item: CartItem) -> Cart:
        cart.delete_item(item=item)
        await self._uow.items.delete_item(item=item)

        return cart
