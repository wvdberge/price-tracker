import json
import os
import re
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

# --- CONFIG ---

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PRODUCTS = {
    "minitool": {
        "url": "https://www.canyon.com/nl-nl/gear/accessories/bikecare-and-service/puncture-repair/canyon-3-in-1-minitool/10014609.html",
        "min_price": 20,
        "max_price": 200
    },
    "aero_drops": {
        "url": "https://www.canyon.com/nl-nl/gear/bike-parts/handlebars-and-stems/canyon-cp0048-cp0049-aero-drops/10014134.html",
        "min_price": 100,
        "max_price": 1000
    },
    "rack": {
        "url": "https://www.canyon.com/nl-nl/gear/accessories/racks/tubus-cargo-evo-28-bike-rack/10010278.html",
        "min_price": 50,
        "max_price": 300
    }
}

PRICE_REGEX = r"€\s?[0-9]+(?:\.[0-9]{3})*(?:,[0-9]{2})?|[0-9]+(?:\.[0-9]{3})*(?:,[0-9]{2})?\s?€"
STATE_FILE = Path(os.environ.get("DATA_DIR", Path(__file__).parent)) / "prices.json"
CHECK_INTERVAL = 86400

# --- HELPERS ---

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def normalize(price_str):
    try:
        return float(price_str.replace("€", "").replace(".", "").replace(",", ".").strip())
    except ValueError:
        return None

def extract_price_from_page(page, min_price, max_price):
    body_text = page.inner_text("body")
    matches = re.findall(PRICE_REGEX, body_text)
    values = []
    for m in matches:
        v = normalize(m)
        if v is not None and min_price <= v <= max_price:
            values.append(v)

    if not values:
        return None

    return max(set(values), key=values.count)

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg},
    )

# --- MAIN LOOP ---

def check_prices():
    previous = load_state()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, cfg in PRODUCTS.items():
            try:
                page = browser.new_page()
                page.goto(cfg["url"], wait_until="load", timeout=60000)
                page.wait_for_timeout(3000)

                price = extract_price_from_page(page, cfg["min_price"], cfg["max_price"])
                page.close()

                if price is None:
                    print(f"{name}: no price found")
                    continue

                if name not in previous:
                    previous[name] = price
                    print(f"{name}: first seen €{price}")
                elif price != previous[name]:
                    msg = f"{name} price changed: €{previous[name]} → €{price}"
                    print("[ALERT]", msg)
                    send_telegram(msg)
                    previous[name] = price
                else:
                    print(f"{name}: €{price} (unchanged)")

            except Exception as e:
                print(f"{name}: error — {e}")

        browser.close()

    save_state(previous)

def run():
    while True:
        check_prices()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
