# mini-shop

A deliberately tiny “shop” so you can see OKAD’s story map without a real monorepo.

```text
mini-shop/
  app.py              # FastAPI-ish routes (plain Python for the demo)
  services/orders.py
  models/order.py
  story.draft.json    # hand-authored narrative (what /okad would write)
  README.md
```

## Try it

```bash
cd /path/to/OKAD
source .venv/bin/activate   # if using uv venv
okad skeleton examples/mini-shop
cp examples/mini-shop/story.draft.json examples/mini-shop/okad-out/story.draft.json
okad finalize examples/mini-shop
open examples/mini-shop/okad-out/story.html
```

You should see journeys like **Browse & buy** and request paths like **POST /orders**.
