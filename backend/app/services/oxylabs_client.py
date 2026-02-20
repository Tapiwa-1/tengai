import time
from typing import Any

import requests
from flask import current_app


class OxylabsError(Exception):
    pass


def get_amazon_product(asin: str) -> dict[str, Any]:
    username = current_app.config.get("OXYLABS_USERNAME", "")
    password = current_app.config.get("OXYLABS_PASSWORD", "")
    source = current_app.config.get("OXYLABS_SOURCE", "amazon_product")
    domain = current_app.config.get("OXYLABS_AMAZON_DOMAIN", "ae")

    if not username or not password:
        raise OxylabsError("OXYLABS_USERNAME/OXYLABS_PASSWORD are not configured")

    url = "https://realtime.oxylabs.io/v1/queries"
    payload = {
        "source": source,
        "query": asin,
        "domain": domain,
        "parse": True,
    }

    retries = [0.5, 1.0, 2.0]
    for idx, backoff in enumerate(retries, start=1):
        response = requests.post(url, auth=(username, password), json=payload, timeout=30)
        if response.status_code < 400:
            data = response.json()
            if data.get("error"):
                raise OxylabsError(str(data["error"]))
            return data

        if response.status_code in {429, 500, 502, 503, 504} and idx < len(retries):
            time.sleep(backoff)
            continue

        raise OxylabsError(f"Oxylabs error {response.status_code}: {response.text}")

    raise OxylabsError("Oxylabs request failed after retries")
