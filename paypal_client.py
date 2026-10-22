"""
PayPal Sandbox Client for PayPal LXNORO Agent 04.
Handles secure OAuth authentication, order creation, server-side order verification,
and order capture against PayPal Sandbox API endpoints only.
Strictly enforces sandbox environment, input validation, Decimal monetary precision,
strict approval URL validation, and server-side capture verification.
"""

import os
import logging
import requests
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

SANDBOX_API_BASE = "https://api-m.sandbox.paypal.com"
ALLOWED_APPROVAL_DOMAINS = ("sandbox.paypal.com", "www.sandbox.paypal.com")
TIMEOUT_SECONDS = 10

# Maintained explicit ISO 4217 currency allowlist matching project UI options
ALLOWED_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD"}


def _validate_environment() -> bool:
    """Strictly validates that PAYPAL_ENVIRONMENT is explicitly 'sandbox' and credentials exist."""
    env = os.getenv("PAYPAL_ENVIRONMENT", "").strip().lower()
    if env != "sandbox":
        logger.error("Security violation: PAYPAL_ENVIRONMENT must be strictly set to 'sandbox'. Live mode is disabled.")
        return False

    client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        logger.error("Missing required PayPal Sandbox credentials (PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET).")
        return False

    return True


def _get_access_token() -> Optional[str]:
    """Retrieves an OAuth 2.0 access token from PayPal Sandbox using Basic Auth with bounded timeout and sanitized error logging."""
    if not _validate_environment():
        return None

    client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()
    auth_url = f"{SANDBOX_API_BASE}/v1/oauth2/token"

    try:
        response = requests.post(
            auth_url,
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=TIMEOUT_SECONDS
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if isinstance(token, str) and token:
                return token
        logger.error("Failed to retrieve PayPal access token with HTTP status: %d", response.status_code)
    except requests.exceptions.Timeout:
        logger.error("PayPal access token request timed out.")
    except requests.exceptions.RequestException:
        logger.error("PayPal access token request encountered a network or protocol error.")
    except Exception:
        logger.error("PayPal access token request encountered an unexpected error.")

    return None


def _validate_approval_url(url: str) -> bool:
    """Validates approval URL scheme is https and hostname belongs to official PayPal Sandbox domains."""
    if not isinstance(url, str) or not url.strip():
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme.lower() != "https":
            return False
        hostname = (parsed.hostname or "").lower()
        if not any(hostname == domain or hostname.endswith("." + domain) for domain in ALLOWED_APPROVAL_DOMAINS):
            return False
        return True
    except Exception:
        return False


def _validate_return_cancel_url(url: str) -> bool:
    """Validates that return/cancel URL scheme is https and has a valid hostname."""
    if not isinstance(url, str) or not url.strip():
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            return False
        return True
    except Exception:
        return False


def create_paypal_order(item_title: str, price: Any, currency: str, product_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Creates a PayPal Sandbox order server-side.
    Validates price (via Decimal), currency (via ISO allowlist), and product identifier (rejecting placeholders).
    Returns (order_id, approval_url, error_message).
    """
    if not _validate_environment():
        return None, None, "PayPal Sandbox environment or credentials not properly configured."

    # Validate product id (reject placeholders like ch3-unknown, check length & type)
    if not isinstance(product_id, str) or not product_id.strip():
        return None, None, "Invalid product identifier."
    clean_product_id = product_id.strip()
    if clean_product_id.lower() in ("ch3-unknown", "unknown", "none", "null", "undefined"):
        return None, None, "Invalid product identifier: placeholder or unknown ID rejected."
    if len(clean_product_id) > 128:
        return None, None, "Product identifier exceeds maximum allowed length."

    # Validate price using Decimal to avoid binary floating-point rounding
    try:
        dec_price = Decimal(str(price))
    except (InvalidOperation, TypeError, ValueError):
        return None, None, "Invalid product price format."

    if not dec_price.is_finite() or dec_price <= Decimal("0"):
        return None, None, "Invalid product price: must be a positive finite number."

    # Validate currency against explicit ISO 4217 allowlist
    if not isinstance(currency, str):
        return None, None, "Invalid currency format."
    clean_currency = currency.strip().upper()
    if clean_currency not in ALLOWED_CURRENCIES:
        return None, None, f"Invalid or unsupported currency code: '{clean_currency}'."

    if not isinstance(item_title, str) or not item_title.strip():
        item_title = "Curated Product"

    return_url = os.getenv("PAYPAL_RETURN_URL", "").strip()
    if not return_url or not _validate_return_cancel_url(return_url):
        return_url = "https://example.com/return"
    cancel_url = os.getenv("PAYPAL_CANCEL_URL", "").strip()
    if not cancel_url or not _validate_return_cancel_url(cancel_url):
        cancel_url = "https://example.com/cancel"

    token = _get_access_token()
    if not token:
        return None, None, "Failed to authenticate with PayPal Sandbox."

    order_url = f"{SANDBOX_API_BASE}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    formatted_amount = f"{dec_price:.2f}"
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": clean_product_id,
                "description": item_title.strip()[:127],
                "amount": {
                    "currency_code": clean_currency,
                    "value": formatted_amount
                }
            }
        ],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                    "user_action": "PAY_NOW",
                    "landing_page": "LOGIN",
                    "shipping_preference": "NO_SHIPPING"
                }
            }
        }
    }

    try:
        response = requests.post(order_url, json=payload, headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code in (200, 201):
            data = response.json()
            order_id = data.get("id")
            approval_url = None

            links = data.get("links", [])
            for link in links:
                if isinstance(link, dict) and link.get("rel") in ("approve", "payer-action"):
                    href = link.get("href")
                    if isinstance(href, str) and _validate_approval_url(href):
                        approval_url = href
                        break

            if isinstance(order_id, str) and order_id.strip() and isinstance(approval_url, str) and approval_url:
                return order_id.strip(), approval_url, None

            return None, None, "PayPal order response missing valid ID or verified approval URL."

        logger.error("PayPal order creation failed with HTTP status: %d", response.status_code)
        return None, None, f"PayPal order creation failed (HTTP {response.status_code})."

    except requests.exceptions.Timeout:
        logger.error("PayPal order creation timed out.")
        return None, None, "PayPal order creation request timed out."
    except requests.exceptions.RequestException:
        logger.error("PayPal order creation encountered a network error.")
        return None, None, "PayPal order network communication error."
    except Exception:
        logger.error("PayPal order creation encountered an unexpected error.")
        return None, None, "Unexpected error during PayPal order creation."


def verify_order_status(order_id: str) -> Tuple[bool, Optional[Dict[Any, Any]], Optional[str]]:
    """
    Verifies order details server-side. Returns (is_approved_or_completed, order_data, error_message).
    """
    if not _validate_environment():
        return False, None, "PayPal environment not configured."

    if not isinstance(order_id, str) or not order_id.strip():
        return False, None, "Invalid order ID."

    clean_order_id = order_id.strip()
    token = _get_access_token()
    if not token:
        return False, None, "Authentication failed."

    verify_url = f"{SANDBOX_API_BASE}/v2/checkout/orders/{clean_order_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(verify_url, headers=headers, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            if data.get("id") == clean_order_id and status in ("CREATED", "APPROVED", "COMPLETED"):
                return True, data, None
            return False, data, f"Order status is '{status}', expected 'CREATED', 'APPROVED', or 'COMPLETED'."

        logger.error("PayPal order verification failed with HTTP status: %d", response.status_code)
        return False, None, f"Order verification failed (HTTP {response.status_code})."

    except requests.exceptions.Timeout:
        logger.error("PayPal order verification timed out.")
        return False, None, "Order verification timed out."
    except requests.exceptions.RequestException:
        logger.error("PayPal order verification network error.")
        return False, None, "Order verification network error."
    except Exception:
        logger.error("PayPal order verification unexpected error.")
        return None, None, "Unexpected error verifying order."


def capture_paypal_order(order_id: str) -> Tuple[bool, Optional[Dict[Any, Any]], Optional[str]]:
    """
    Server-side order capture. Verifies order is APPROVED first, captures order,
    and requires both matching order ID and COMPLETED status. Handles HTTP 422
    and ambiguous outcomes via server-side re-verification.
    Returns (success, capture_response_data, error_message).
    """
    if not _validate_environment():
        return False, None, "PayPal environment not configured."

    if not isinstance(order_id, str) or not order_id.strip():
        return False, None, "Invalid order ID."

    clean_order_id = order_id.strip()

    # Step 1: Server-side verification of order status before capture
    is_valid, order_data, verify_err = verify_order_status(clean_order_id)
    if not is_valid:
        return False, None, verify_err or "Order verification failed before capture."

    current_status = order_data.get("status") if order_data else None

    # Step 2: Handle already completed / duplicate capture attempts safely
    if current_status == "COMPLETED" and order_data.get("id") == clean_order_id:
        return True, order_data, None

    if current_status != "APPROVED":
        return False, None, f"Cannot capture order with status '{current_status}'. Order must be APPROVED."

    token = _get_access_token()
    if not token:
        return False, None, "Authentication failed."

    capture_url = f"{SANDBOX_API_BASE}/v2/checkout/orders/{clean_order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(capture_url, headers=headers, json={}, timeout=TIMEOUT_SECONDS)

        # Handle 422 or successful capture codes by verifying server-side state
        if response.status_code in (200, 201, 422):
            re_valid, re_data, _ = verify_order_status(clean_order_id)
            if (
                re_valid
                and re_data
                and re_data.get("id") == clean_order_id
                and re_data.get("status") == "COMPLETED"
            ):
                return True, re_data, None

            if response.status_code in (200, 201):
                data = response.json()
                if (
                    isinstance(data, dict)
                    and data.get("id") == clean_order_id
                    and data.get("status") == "COMPLETED"
                ):
                    return True, data, None

        logger.error("PayPal order capture failed or unverified with HTTP status: %d", response.status_code)
        return False, None, f"Order capture verification failed (HTTP {response.status_code})."

    except requests.exceptions.Timeout:
        logger.error("PayPal order capture timed out.")
        return False, None, "Order capture timed out."
    except requests.exceptions.RequestException:
        logger.error("PayPal order capture network error.")
        return False, None, "Order capture network error."
    except Exception:
        logger.error("PayPal order capture unexpected error.")
        return False, None, "Unexpected error capturing order."
