"""
Example: AI agent searching real estate listings via the Mainlayer-gated API.

Usage:
    MAINLAYER_TOKEN=your-token python examples/search_properties.py
"""

import os
import httpx

BASE_URL = os.environ.get("REALESTATE_API_URL", "http://localhost:8000")
TOKEN = os.environ.get("MAINLAYER_TOKEN", "your-mainlayer-token-here")

HEADERS = {"X-Mainlayer-Token": TOKEN}


def list_properties(city: str = "Austin", max_price: int = 1_000_000):
    resp = httpx.get(
        f"{BASE_URL}/properties",
        headers=HEADERS,
        params={"city": city, "max_price": max_price, "status": "active"},
    )

    if resp.status_code == 402:
        print("Payment required:", resp.json()["detail"]["message"])
        return

    resp.raise_for_status()
    data = resp.json()
    print(f"Found {data['total_results']} active listings in {city} under ${max_price:,}:\n")
    for prop in data["properties"][:5]:
        print(f"  {prop['address']}, {prop['city']} — ${prop['price']:,} | {prop['bedrooms']}bd {prop['bathrooms']}ba {prop['sqft']:,}sqft")


def advanced_search():
    resp = httpx.post(
        f"{BASE_URL}/search",
        headers=HEADERS,
        json={
            "min_beds": 3,
            "max_price": 800_000,
            "has_pool": True,
            "page": 1,
            "page_size": 10,
        },
    )

    if resp.status_code == 402:
        print("Payment required:", resp.json()["detail"]["message"])
        return

    resp.raise_for_status()
    data = resp.json()
    print(f"\nAdvanced search: {data['total_results']} homes with 3+ beds, pool, under $800k:")
    for prop in data["properties"][:5]:
        print(f"  {prop['address']}, {prop['city']}, {prop['state']} — ${prop['price']:,}")


def get_property_detail(property_id: str):
    resp = httpx.get(f"{BASE_URL}/properties/{property_id}", headers=HEADERS)

    if resp.status_code == 404:
        print(f"Property {property_id} not found")
        return

    resp.raise_for_status()
    prop = resp.json()
    print(f"\nDetail: {prop['address']}")
    print(f"  Price: ${prop['price']:,} | MLS: {prop.get('mls_number', 'N/A')}")
    print(f"  Description: {prop['description'][:120]}…")


if __name__ == "__main__":
    list_properties()
    advanced_search()
    get_property_detail("atx-001")
