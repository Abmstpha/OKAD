"""Tiny demo shop — enough surface for OKAD to find routes."""

from __future__ import annotations

# Pretend FastAPI style for the skeleton extractor
router = type("R", (), {})()


def _route(method: str, path: str):
    def deco(fn):
        return fn

    return deco


# The extractor looks for decorator patterns in source text:
# we also keep classic app.get forms below as comments for grepping demos.


class App:
    def get(self, path):
        def deco(fn):
            return fn

        return deco

    def post(self, path):
        def deco(fn):
            return fn

        return deco


app = App()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/catalog")
def catalog():
    return [{"id": 1, "name": "Mug", "price": 12}]


@app.post("/orders")
def create_order():
    return {"id": "ord_1", "status": "created"}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    return {"id": order_id, "status": "created"}
