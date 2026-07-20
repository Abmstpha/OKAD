"""Order application service."""


class OrderService:
    def create(self, items: list[dict], currency: str = "USD") -> dict:
        total = sum(i.get("price", 0) for i in items)
        return {"id": "ord_1", "total": total, "currency": currency, "status": "created"}

    def get(self, order_id: str) -> dict:
        return {"id": order_id, "status": "created"}
