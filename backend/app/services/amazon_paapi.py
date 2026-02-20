import hashlib
import hmac
import json
import time
from datetime import datetime

import requests
from flask import current_app


class AmazonPAAPIError(Exception):
    pass


def _sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signature_key(key, date_stamp, region, service):
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    return _sign(k_service, "aws4_request")


def get_items(asins: list[str]) -> dict:
    cfg = current_app.config
    service = "ProductAdvertisingAPI"
    host = cfg["AMZ_HOST"]
    region = cfg["AMZ_REGION"]
    endpoint = f"https://{host}/paapi5/getitems"
    now = datetime.utcnow()
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    payload = {
        "ItemIds": asins,
        "ItemIdType": "ASIN",
        "Marketplace": cfg["AMZ_MARKETPLACE"],
        "PartnerTag": cfg["AMZ_PARTNER_TAG"],
        "PartnerType": cfg["AMZ_PARTNER_TYPE"],
        "Resources": [
            "Images.Primary.Large",
            "ItemInfo.Title",
            "ItemInfo.ByLineInfo",
            "ItemInfo.Features",
            "ItemInfo.ProductInfo",
            "Offers.Listings.Price",
            "CustomerReviews.Count",
            "CustomerReviews.StarRating",
        ],
    }
    payload_json = json.dumps(payload)
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    canonical_headers = (
        f"content-encoding:amz-1.0\n"
        f"content-type:application/json; charset=utf-8\n"
        f"host:{host}\n"
        f"x-amz-date:{amz_date}\n"
        f"x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems\n"
    )
    signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"
    canonical_request = (
        "POST\n/paapi5/getitems\n\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )

    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        "AWS4-HMAC-SHA256\n"
        f"{amz_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    signing_key = _signature_key(cfg["AMZ_SECRET_KEY"], date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization = (
        "AWS4-HMAC-SHA256 "
        f"Credential={cfg['AMZ_ACCESS_KEY']}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "Content-Encoding": "amz-1.0",
        "Content-Type": "application/json; charset=utf-8",
        "Host": host,
        "X-Amz-Date": amz_date,
        "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems",
        "Authorization": authorization,
    }

    retries = [0.5, 1, 2]
    for idx, backoff in enumerate(retries, start=1):
        response = requests.post(endpoint, headers=headers, data=payload_json, timeout=15)
        if response.status_code < 400:
            return response.json()
        if response.status_code in {429, 500, 502, 503, 504} and idx < len(retries):
            time.sleep(backoff)
            continue
        raise AmazonPAAPIError(f"PA-API error {response.status_code}: {response.text}")

    raise AmazonPAAPIError("PA-API failed after retries")
