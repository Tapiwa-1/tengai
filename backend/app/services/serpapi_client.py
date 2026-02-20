import time
from typing import Any

import requests
from flask import current_app


class SerpApiError(Exception):
    pass


def get_amazon_product(asin: str) -> dict[str, Any]:
    api_key = current_app.config.get("SERPAPI_KEY", "")
    if not api_key:
        raise SerpApiError("SERPAPI_KEY is not configured")

    params = {
        "engine": "amazon_product",
        "amazon_domain": "amazon.ae",
        "asin": asin,
        "api_key": api_key,
    }

    retries = [0.5, 1.0, 2.0]
    url = "https://serpapi.com/search.json"

    for idx, backoff in enumerate(retries, start=1):
        response = requests.get(url, params=params, timeout=20)
        if response.status_code < 400:
            data = response.json()
            if data.get("error"):
                raise SerpApiError(data["error"])
            return data

        if response.status_code in {429, 500, 502, 503, 504} and idx < len(retries):
            time.sleep(backoff)
            continue

        raise SerpApiError(f"SerpApi error {response.status_code}: {response.text}")

    raise SerpApiError("SerpApi request failed after retries")
