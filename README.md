# real-estate-data-api
![CI](https://github.com/mainlayer/real-estate-data-api/actions/workflows/ci.yml/badge.svg)

Real estate property listings, price history, and advanced search for AI agents — billed per query via Mainlayer.

## Install

```bash
pip install mainlayer httpx
```

## Quickstart

```python
import httpx

response = httpx.get(
    "https://your-api.com/properties",
    headers={"X-Mainlayer-Token": "your-token"},
    params={"city": "Austin", "status": "active"}
)
print(response.json())
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/properties` | List properties with filters (city, price, beds, status) |
| `GET` | `/properties/{id}` | Full property details |
| `POST` | `/search` | Advanced search with flexible JSON body |
| `GET` | `/health` | Health check |

All data endpoints require `X-Mainlayer-Token` header.

## Running locally

```bash
pip install -e ".[dev]"
uvicorn src.main:app --reload
```

## Running tests

```bash
pytest tests/
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `MAINLAYER_API_KEY` | Your Mainlayer API key |
| `MAINLAYER_RESOURCE_ID` | The resource ID for this API |

📚 [mainlayer.fr](https://mainlayer.fr)
