"""
Isolated test script to verify Trendyol & n11 scraping reliability
on both local and GitHub Actions (Azure IP) runners.
Does NOT modify any production pools, live_deals.json, or rotation_state.json.
"""

import json
import re
import sys
import urllib3
from curl_cffi import requests as cffi_req

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()


def extract_json_after_prefix(text, prefix):
    idx = text.find(prefix)
    if idx == -1:
        return None
    start = text.find('{', idx + len(prefix))
    if start == -1:
        return None
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text[start:])
    return obj


def test_trendyol(query="kahve makinesi"):
    url = f"https://www.trendyol.com/sr?q={cffi_req.utils.quote(query) if hasattr(cffi_req, 'utils') else query.replace(' ', '%20')}&sst=BEST_SELLER"
    print(f"\n=== TRENDYOL TEST: {url} ===")
    try:
        r = cffi_req.get(
            url,
            impersonate="chrome120",
            headers={"Accept-Language": "tr-TR,tr;q=0.9"},
            timeout=15,
            verify=False,
        )
        print(f"HTTP Status: {r.status_code} | Size: {len(r.text)} bytes")
        if r.status_code != 200:
            print("BLOCKED / NON-200:", r.text[:300])
            return 0

        data = extract_json_after_prefix(r.text, 'window["__single-search-result__PROPS"]=')
        if not data:
            print("ERROR: __single-search-result__PROPS not found (possible Cloudflare challenge)")
            return 0

        # Search recursively for 'products' list
        products = (
            data.get("data", {}).get("products")
            or data.get("products")
            or []
        )
        if not products:
            # fallback search in top-level keys
            for v in data.values():
                if isinstance(v, dict) and isinstance(v.get("products"), list):
                    products = v["products"]
                    break

        print(f"Extracted products: {len(products)}")
        for i, p in enumerate(products[:3], 1):
            name = p.get("name") or ""
            price_obj = p.get("price") or {}
            sale = price_obj.get("discountedPrice") or price_obj.get("sellingPrice") or price_obj.get("current")
            orig = price_obj.get("originalPrice") or price_obj.get("marketPrice")
            purl = p.get("url") or ""
            imgs = p.get("images") or []
            print(f"  {i}. {name[:55]} | orig={orig} sale={sale} | url={purl[:40]} | img={imgs[0] if imgs else ''}")
        return len(products)
    except Exception as e:
        print(f"Trendyol Exception: {e}")
        return 0


def test_n11(query="kahve makinesi"):
    url = f"https://www.n11.com/arama?q={query.replace(' ', '+')}&srt=SALES_VOLUME"
    print(f"\n=== N11 TEST: {url} ===")
    try:
        r = cffi_req.get(
            url,
            impersonate="chrome120",
            headers={"Accept-Language": "tr-TR,tr;q=0.9"},
            timeout=15,
            verify=False,
        )
        print(f"HTTP Status: {r.status_code} | Size: {len(r.text)} bytes")
        if r.status_code != 200:
            print("BLOCKED / NON-200:", r.text[:300])
            return 0

        data = extract_json_after_prefix(r.text, "window.model = ")
        if not data:
            print("ERROR: window.model not found")
            return 0

        # Locate product list inside window.model
        products = data.get("searchResults") or []
        print(f"Extracted products: {len(products)}")
        for i, p in enumerate(products[:3], 1):
            title = p.get("title") or p.get("name") or ""
            orig = p.get("oldPrice") or p.get("displayPrice") or p.get("listPrice")
            sale = p.get("price") or p.get("newPrice") or p.get("discountedPrice")
            purl = p.get("url") or p.get("link") or ""
            imgs = p.get("images") or []
            img = (imgs[0] if imgs else "") or p.get("imageUrl") or p.get("image") or ""
            print(f"  {i}. {str(title)[:55]} | orig={orig} sale={sale} | url={str(purl)[:40]} | img={str(img)[:55]}")
        return len(products)
    except Exception as e:
        print(f"N11 Exception: {e}")
        return 0


if __name__ == "__main__":
    ty_cnt = test_trendyol("kahve makinesi")
    n11_cnt = test_n11("kahve makinesi")
    print(f"\nSUMMARY -> Trendyol: {ty_cnt} products | n11: {n11_cnt} products")
