from app.domain.cart_config.dto import CartConfigDTO


class CartConfig:
    def __init__(self, data: CartConfigDTO) -> None:
        self.max_items_qty = data.max_items_qty
        self.min_cost_for_checkout = data.min_cost_for_checkout
        self.limit_items_by_id = data.limit_items_by_id
        self.hours_since_update_until_abandoned = data.hours_since_update_until_abandoned
        self.max_abandoned_notifications_qty = data.max_abandoned_notifications_qty
        self.abandoned_cart_text = data.abandoned_cart_text
