"""
Channel3 API Client for PayPal LXNORO Agent 04.
Aligned with official Channel3 API v1/search schema (query & limit in payload, robust nested price parsing).
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

CHANNEL3_API_ENDPOINT = "https://api.trychannel3.com/v1/search"
DEFAULT_TIMEOUT = 10.0


def _parse_price(val: Any) -> float:
    """Safely extracts a float price from numeric, string, or nested dictionary values."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.strip())
        except ValueError:
            return 0.0
    if isinstance(val, dict):
        for k in ("amount", "value", "price", "cost"):
            if k in val:
                return _parse_price(val[k])
    return 0.0


def search_products(
    query: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Searches the Channel3 product catalog using the official v1/search endpoint.
    Sends documented query and limit parameters.
    """
    api_key = os.getenv("CHANNEL3_API_KEY")
    if not api_key or not api_key.strip():
        logger.warning("CHANNEL3_API_KEY is not configured in environment variables.")
        return {
            "success": False,
            "products": [],
            "error": "API key not configured",
            "source": "unconfigured",
        }

    headers = {
        "x-api-key": api_key.strip(),
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "query": query,
        "limit": limit,
    }

    try:
        response = requests.post(
            CHANNEL3_API_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )

        response.raise_for_status()
        data = response.json()

        # Parse products from response structure
        raw_products = data.get("products", data.get("results", data.get("data", [])))
        if not isinstance(raw_products, list):
            raw_products = []

        products = []
        for item in raw_products:
            if isinstance(item, dict):
                # Extract primary offer pricing if nested in offers list or dict
                offers = item.get("offers", [])
                price = _parse_price(item.get("price", 0.0))
                currency = str(item.get("currency", "USD"))
                
                if isinstance(offers, list) and len(offers) > 0 and isinstance(offers[0], dict):
                    primary_offer = offers[0]
                    price = _parse_price(primary_offer.get("price", primary_offer.get("cost", price)))
                    currency = str(primary_offer.get("currency", currency))

                products.append({
                    "id": str(item.get("id", item.get("product_id", "ch3-unknown"))),
                    "brand": str(item.get("brand", item.get("merchant", "Channel3 Merchant"))),
                    "title": str(item.get("title", item.get("name", "Product"))),
                    "price": price,
                    "currency": currency,
                    "condition": str(item.get("condition", "New")),
                    "rating": float(item.get("rating", 0.0)) if item.get("rating") is not None else None,
                    "reviews_count": int(item.get("reviews_count", item.get("reviews", 0))) if item.get("reviews_count") is not None or item.get("reviews") is not None else None,
                    "specs": item.get("specs", item.get("specifications", {})),
                    "pros": item.get("pros"),
                    "cons": item.get("cons"),
                    "emoji": "🛍️",
                })

        return {
            "success": True,
            "products": products,
            "error": None,
            "source": "channel3_api",
        }

    except requests.exceptions.Timeout:
        logger.error("Channel3 API request timed out after %s seconds.", DEFAULT_TIMEOUT)
        return {
            "success": False,
            "products": [],
            "error": "Request timed out",
            "source": "timeout",
        }
    except requests.exceptions.HTTPError as http_err:
        status_code = "unknown"
        reason = ""
        if http_err.response is not None:
            status_code = getattr(http_err.response, "status_code", "unknown")
            reason = getattr(http_err.response, "reason", "")
        
        safe_msg = f"HTTP error {status_code}"
        if reason:
            safe_msg += f" ({reason})"

        logger.error("Channel3 API HTTP error occurred: status=%s", status_code)
        return {
            "success": False,
            "products": [],
            "error": safe_msg,
            "source": "http_error",
        }
    except requests.exceptions.RequestException as req_err:
        logger.error("Channel3 API request exception: %s", req_err)
        return {
            "success": False,
            "products": [],
            "error": f"Connection error: {str(req_err)}",
            "source": "connection_error",
        }
    except ValueError as json_err:
        logger.error("Failed to parse JSON response from Channel3 API: %s", json_err)
        return {
            "success": False,
            "products": [],
            "error": "Malformed JSON response",
            "source": "parse_error",
        }
    except Exception as e:
        logger.error("Unexpected error in Channel3 client: %s", e)
        return {
            "success": False,
            "products": [],
            "error": f"Unexpected error: {str(e)}",
            "source": "unexpected_error",
        }
