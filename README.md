# price-tracker

Watches Canyon NL product pages for price changes and sends a Telegram alert when a price drops or rises.

## How it works

Runs on a 24h loop. On each cycle it scrapes the configured product pages with Playwright, compares prices to the last known values, and sends a Telegram message if anything changed. First run only establishes the baseline — no alert is sent.

## Products tracked

- Canyon 3-in-1 Minitool
- Canyon CP0048/CP0049 Aero Drops
- Tubus Cargo Evo 28 Rack
- ForkLift (binarynights.com)

## Adding a new product

1. Open the product page in a browser, right-click the price, and choose Inspect/Inspect Element
2. Find a unique `id` or `class` on the price element, e.g. `#price-label-1` or `.product-price`
3. Add an entry to `PRODUCTS` in `pricetracker.py`:

```python
"my_product": {
    "url": "https://example.com/product",
    "selector": "#price-label-1",  # omit to fall back to full-page scan
    "min_price": 10,
    "max_price": 200
}
```

4. Push to `main` — GitHub Actions rebuilds the image automatically
5. Pull the new image in Dockge and restart the stack

Supports € and $ prices. The `min_price`/`max_price` range filters out unrelated prices on the page when no selector is set.

## Deploy

Built and pushed to `ghcr.io/wvdberge/price-tracker:latest` via GitHub Actions on every push to `main`.

Run with Docker Compose:

```yaml
services:
  price-tracker:
    image: ghcr.io/wvdberge/price-tracker:latest
    container_name: price-tracker
    restart: unless-stopped
    volumes:
      - /volume1/docker/price-tracker:/data
    environment:
      - TELEGRAM_TOKEN=<BotFather token>
      - CHAT_ID=<your Telegram user ID>
      - DATA_DIR=/data
```

State is persisted in `/data/prices.json` — mount a volume there to survive container restarts.
