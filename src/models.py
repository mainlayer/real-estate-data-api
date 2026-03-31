from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class PropertyType(str, Enum):
    single_family = "single_family"
    condo = "condo"
    townhouse = "townhouse"
    multi_family = "multi_family"
    land = "land"


class ListingStatus(str, Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    off_market = "off_market"


class Property(BaseModel):
    id: str
    address: str
    city: str
    state: str
    zip_code: str
    price: int
    bedrooms: int
    bathrooms: float
    sqft: int
    lot_size_sqft: Optional[int] = None
    year_built: int
    property_type: PropertyType
    status: ListingStatus
    days_on_market: int
    description: str
    features: List[str]
    garage_spaces: int = 0
    has_pool: bool = False
    hoa_monthly: Optional[int] = None
    taxes_annual: int
    latitude: float
    longitude: float
    photos_count: int
    listing_agent: str
    mls_number: str


class PropertySummary(BaseModel):
    id: str
    address: str
    city: str
    state: str
    zip_code: str
    price: int
    bedrooms: int
    bathrooms: float
    sqft: int
    property_type: PropertyType
    status: ListingStatus
    days_on_market: int
    latitude: float
    longitude: float


class PriceEvent(BaseModel):
    date: str
    price: int
    event: str
    price_change: Optional[int] = None
    price_change_pct: Optional[float] = None


class PriceHistory(BaseModel):
    property_id: str
    address: str
    current_price: int
    original_list_price: int
    history: List[PriceEvent]
    total_price_changes: int
    days_on_market: int


class MarketStats(BaseModel):
    city: str
    state: str
    report_date: str
    active_listings: int
    median_list_price: int
    median_sale_price: int
    avg_days_on_market: float
    months_of_supply: float
    list_to_sale_ratio: float
    price_per_sqft: int
    sold_last_30_days: int
    new_listings_last_30_days: int
    market_type: str
    yoy_price_change_pct: float
    by_property_type: dict


class NeighborhoodTrend(BaseModel):
    zip_code: str
    neighborhood: str
    city: str
    state: str
    report_date: str
    walk_score: int
    transit_score: int
    school_rating: float
    median_household_income: int
    population: int
    median_age: float
    yoy_price_change_pct: float
    five_year_price_change_pct: float
    avg_price_per_sqft: int
    rental_vacancy_rate: float
    owner_occupied_pct: float
    crime_index: int
    nearby_amenities: dict


class SearchResponse(BaseModel):
    total_results: int
    page: int
    page_size: int
    properties: List[PropertySummary]


class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
