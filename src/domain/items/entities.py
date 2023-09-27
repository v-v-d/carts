from domain.items.dto import ItemDTO


class Item:
    def __init__(self, data: ItemDTO) -> None:
        self.id = data.id
        self.name = data.name
        self.qty = data.qty
        self.price = data.price
        self.cost = self.price * self.qty
