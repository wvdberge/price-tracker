# price-tracker

Watches Canyon NL product pages for price changes and sends a Telegram alert when a price drops or rises.

## How it works

Runs on a 24h loop. On each cycle it scrapes the configured product pages with Playwright, compares prices to the last known values, and sends a Telegram message if anything changed. First run only establishes the baseline — no alert is sent.

## Products tracked

- Canyon 3-in-1 Minitool
- Canyon CP0048/CP0049 Aero Drops
- Tubus Cargo Evo 28 Rack

## Deploy

Built and pushed to `ghcr.io/wvdberge/price-tracker:latest` via GitHub Actions on every push to `main`.

Run with Docker Compose — set two environment variables:

```
TELEGRAM_TOKEN=<BotFather token>
CHAT_ID=<your Telegram user ID>
```

State is persisted in `/data/prices.json` — mount a volume there to survive container restarts.
