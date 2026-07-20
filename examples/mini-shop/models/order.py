"""Order entity / persistence stub."""


class Order:
    def __init__(self, id: str, total: float, currency: str):
        self.id = id
        self.total = total
        self.currency = currency
