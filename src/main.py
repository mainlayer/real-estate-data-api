"""
Real Estate Data API

Property listings and search sold to AI agents per query via Mainlayer.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from mainlayer import MainlayerClient

from .properties_db import (
    get_all_properties,
    get_property_by_id,
    search_properties as db_search_properties,
)
from .models import (
    Property,
    PropertySummary,
    PropertyType,
    ListingStatus,
    SearchResponse,
)

app = FastAPI(
    title="Real Estate Data API",
    description="Property listings, price history, and market data — billed per query via Mainlayer.",
    version="1.0.0",
)

ml = MainlayerClient(api_key=os.environ.get("MAINLAYER_API_KEY", ""))
RESOURCE_ID = os.environ.get("MAINLAYER_RESOURCE_ID", "")


async def require_payment(x_mainlayer_token: str = Header(...)):
    access = await ml.resources.verify_access(RESOURCE_ID, x_mainlayer_token)
    if not access.authorized:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": "This endpoint is billed per query. Get access at mainlayer.fr",
                "payment_url": "https://mainlayer.fr",
            },
        )
    return access


def _to_summary(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "address": raw["address"],
        "city": raw["city"],
        "state": raw["state"],
        "zip_code": raw["zip_code"],
        "price": raw["price"],
        "bedrooms": raw["bedrooms"],
        "bathrooms": raw["bathrooms"],
        "sqft": raw["sqft"],
        "property_type": raw["property_type"],
        "status": raw["status"],
        "days_on_market": raw["days_on_market"],
        "latitude": raw.get("latitude", 0.0),
        "longitude": raw.get("longitude", 0.0),
    }


@app.get("/properties")
async def list_properties(
    city: Optional[str] = Query(None, description="Filter by city name"),
    state: Optional[str] = Query(None, description="Filter by 2-letter state code"),
    status: Optional[str] = Query(None, description="Filter by listing status: active, pending, sold, off_market"),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    min_beds: Optional[int] = Query(None, description="Minimum bedrooms"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _access=Depends(require_payment),
):
    """List property listings with optional filters."""
    results = get_all_properties()

    if city:
        results = [p for p in results if city.lower() in p["city"].lower()]
    if state:
        results = [p for p in results if p["state"].upper() == state.upper()]
    if status:
        results = [p for p in results if p["status"] == status.lower()]
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if min_beds is not None:
        results = [p for p in results if p["bedrooms"] >= min_beds]

    total = len(results)
    start = (page - 1) * page_size
    page_results = results[start : start + page_size]

    return {
        "total_results": total,
        "page": page,
        "page_size": page_size,
        "properties": [_to_summary(p) for p in page_results],
    }


@app.get("/properties/{property_id}")
async def get_property(
    property_id: str,
    _access=Depends(require_payment),
):
    """Get full details for a specific property."""
    prop = get_property_by_id(property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail=f"Property '{property_id}' not found")
    return prop


@app.post("/search")
async def search_properties(
    body: dict,
    _access=Depends(require_payment),
):
    """
    Advanced property search with flexible criteria.

    Body fields (all optional):
    - city, state, zip_code
    - min_price, max_price
    - min_beds, max_beds
    - min_baths, max_baths
    - min_sqft, max_sqft
    - property_type: single_family | condo | townhouse | multi_family | land
    - has_pool: bool
    - page, page_size
    """
    results = get_all_properties()

    if city := body.get("city"):
        results = [p for p in results if city.lower() in p["city"].lower()]
    if state := body.get("state"):
        results = [p for p in results if p["state"].upper() == state.upper()]
    if zip_code := body.get("zip_code"):
        results = [p for p in results if p["zip_code"] == zip_code]
    if min_price := body.get("min_price"):
        results = [p for p in results if p["price"] >= min_price]
    if max_price := body.get("max_price"):
        results = [p for p in results if p["price"] <= max_price]
    if min_beds := body.get("min_beds"):
        results = [p for p in results if p["bedrooms"] >= min_beds]
    if max_beds := body.get("max_beds"):
        results = [p for p in results if p["bedrooms"] <= max_beds]
    if min_sqft := body.get("min_sqft"):
        results = [p for p in results if p["sqft"] >= min_sqft]
    if max_sqft := body.get("max_sqft"):
        results = [p for p in results if p["sqft"] <= max_sqft]
    if ptype := body.get("property_type"):
        results = [p for p in results if p["property_type"] == ptype]
    if "has_pool" in body:
        results = [p for p in results if p.get("has_pool") == body["has_pool"]]

    page = body.get("page", 1)
    page_size = min(body.get("page_size", 20), 100)
    total = len(results)
    start = (page - 1) * page_size
    page_results = results[start : start + page_size]

    return {
        "total_results": total,
        "page": page,
        "page_size": page_size,
        "properties": [_to_summary(p) for p in page_results],
        "sampled_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
